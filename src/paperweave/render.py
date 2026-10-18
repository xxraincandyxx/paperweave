from pathlib import Path
import json, re
from playwright.sync_api import sync_playwright, TimeoutError as BrowserTimeout
from .config import ROOT
from .vendor.mindmap_compiler import generate_mindmap,generate_flowchart

STATIC=Path(__file__).parent/'static'

def browser_launch(p):
    import os
    for name in ('msedge','chrome'):
        try:
            return p.chromium.launch(channel=name,headless=True)
        except Exception:
            pass
    try:
        return p.chromium.launch(headless=True)
    except Exception:
        raise ValueError('未找到可用浏览器。请安装 Microsoft Edge，或执行 python -m playwright install chromium。') from None


def compile_and_validate(tree):
    codes={'mindmap':generate_mindmap(tree),'flowchart':generate_flowchart(tree)}
    repaired=False
    with sync_playwright() as p:
        browser=browser_launch(p)
        try:
            page=browser.new_page(viewport={'width':1500,'height':1000})
            page.route('**/*',lambda route:route.abort())
            page.set_content('<html><body><main id="diagram"></main></body></html>')
            page.add_script_tag(path=str(STATIC/'mermaid.bundle.js'))
            page.evaluate("""() => window.PaperMermaid.initialize({startOnLoad:false,securityLevel:'strict',theme:'base',maxTextSize:2000000,maxEdges:20000,themeVariables:{fontFamily:'Georgia, Microsoft YaHei, serif',primaryColor:'#edf5ef',primaryTextColor:'#1b332d',primaryBorderColor:'#6f9887',lineColor:'#a6b6ae'}})""")
            for mode,code in codes.items():
                result=page.evaluate("""async code=>{try{await PaperMermaid.parse(code);return {ok:true}}catch(e){return {ok:false,error:String(e)}}}""",code)
                if not result['ok']:
                    # Rule repair only touches display labels, preserving IDs and evidence.
                    def simplify(node):
                        return {**node,'label':re.sub(r'[^\w\s\u4e00-\u9fff]',' ',node['label']),
                            'children':[simplify(c) for c in node.get('children',[])]}
                    safer=simplify(tree)
                    code=generate_mindmap(safer) if mode=='mindmap' else generate_flowchart(safer)
                    page.evaluate('async code=>await PaperMermaid.parse(code)',code)
                    codes[mode]=code; repaired=True
            svg=page.evaluate("""async code=>{const r=await PaperMermaid.render('validated-map',code);return r.svg}""",codes['mindmap'])
            if '<svg' not in svg:
                raise ValueError('Mermaid 未生成 SVG。')
        finally:
            browser.close()
    return codes,svg,repaired


def export_dashboard(result,directory):
    codes,svg,repaired=compile_and_validate(result['tree'])
    result['mermaid']=codes
    result['validation']={'parser':'Mermaid 11.12.0 / Chromium','mindmap':True,'flowchart':True,'rule_repair':repaired}
    template=(STATIC/'dashboard.html').read_text(encoding='utf8')
    data=json.dumps(result,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    # No assets are fetched when file:// is opened; both renderer and data are inline.
    html=template.replace('/*__STYLE__*/',(STATIC/'dashboard.css').read_text(encoding='utf8'))
    html=html.replace('/*__MERMAID__*/',(STATIC/'mermaid.bundle.js').read_text(encoding='utf8').replace('</script','<\\/script'))
    html=html.replace('/*__APP__*/',(STATIC/'dashboard.js').read_text(encoding='utf8'))
    html=html.replace('__PAPER_DATA__',data).replace('__INITIAL_SVG__',svg)
    (directory/'dashboard.html').write_text(html,encoding='utf8')
    for mode,code in codes.items():
        (directory/f'{mode}.mmd').write_text(code,encoding='utf8')
    (directory/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    return directory/'dashboard.html'
