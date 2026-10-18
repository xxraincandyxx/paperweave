import argparse,sys
from pathlib import Path
from .config import ROOT, Settings

def main():
    parser=argparse.ArgumentParser(description='研脉 PaperWeave · PDF → 证据导图 → 离线 HTML')
    sub=parser.add_subparsers(dest='command',required=True)
    analyze=sub.add_parser('analyze',help='一键分析 PDF')
    analyze.add_argument('pdf'); analyze.add_argument('-o','--output',default=str(ROOT/'outputs'/'paper'))
    analyze.add_argument('--env',default=None)
    serve=sub.add_parser('serve',help='打开本地上传界面')
    serve.add_argument('--port',type=int,default=8765)
    sub.add_parser('doctor',help='检查配置与浏览器')
    args=parser.parse_args()
    try:
        if args.command=='serve':
            import uvicorn
            from .server import app
            print(f'本地入口：http://127.0.0.1:{args.port}；按 Ctrl+C 停止。')
            uvicorn.run(app,host='127.0.0.1',port=args.port)
        elif args.command=='analyze':
            from .pipeline import run
            result=run(args.pdf,args.output,Settings.load(args.env),lambda step,pct:print(f'[{pct:3d}%] {step}',flush=True))
            print(f'离线看板：{result.resolve()}')
        else:
            from .render import browser_launch,STATIC
            from playwright.sync_api import sync_playwright
            cfg=Settings.load()
            cfg.validate()
            if not (STATIC/'mermaid.bundle.js').is_file():
                raise ValueError('缺少内嵌 Mermaid 依赖，请先 npm ci && npm run build。')
            with sync_playwright() as p:
                browser=browser_launch(p); browser.close()
            print(f'配置完整，模型 ID：{cfg.model}；浏览器和 Mermaid 可用。尚未调用真实 API。')
    except Exception as exc:
        print('处理失败：'+str(exc),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    sys.exit(main())
