from pathlib import Path
from dataclasses import asdict
from datetime import datetime,timezone
import base64, hashlib, json
from .config import Settings
from .parser import parse_pdf,make_chunks
from .analysis import map_prompt,validate_findings,merge_findings,organize
from .llm import LLM
from .render import export_dashboard


def run(pdf_path, output_dir, settings=None, progress=None, llm=None, fixture=False):
    cfg=settings or Settings.load()
    if llm is None:
        cfg.validate()
        llm=LLM(cfg)
    path=Path(pdf_path)
    if path.suffix.lower()!='.pdf' or not path.is_file():
        raise ValueError('请选择存在的 .pdf 文件。')
    if path.stat().st_size>80*1024*1024:
        raise ValueError('PDF 超过 80 MB，请压缩或拆分后导入。')
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    def emit(step,pct):
        if progress: progress(step,pct)
    emit('按页提取 PDF 正文',8)
    content,pages,sources,warnings=parse_pdf(path)
    extraction={'title':content.meta.title,'pages':pages,'sources':[asdict(s) for s in sources],
        'sections':[asdict(s) for s in content.sections],'warnings':warnings}
    (out/'extracted.json').write_text(json.dumps(extraction,ensure_ascii=False,indent=2),encoding='utf8')
    (out/'extracted.md').write_text('\n\n'.join(f'<!-- PDF page {p["page"]} -->\n{p["text"]}' for p in pages),encoding='utf8')
    chunks=make_chunks(sources,cfg.chunk_chars)
    findings=[]; chunk_report=[]
    for i,chunk in enumerate(chunks):
        emit(f'全文分析 {i+1}/{len(chunks)} 块',15+int(55*i/max(1,len(chunks))))
        # Validate evidence IDs against the current chunk, not just the global PDF.
        allowed={s.id for s in chunk}
        def validate(obj):
            validate_findings(obj)
            for f in obj['findings']:
                if any(e['source_id'] not in allowed for e in f['evidence']):
                    raise ValueError('证据 ID 不属于当前提供的片段')
        result=llm.json(map_prompt(chunk),validate)
        findings.extend(result['findings'])
        chunk_report.append({'chunk':i+1,'source_ids':[s.id for s in chunk],
            'pages':sorted({s.page for s in chunk}),'findings':len(result['findings']),'status':'analyzed'})
        (out/'chunk_report.json').write_text(json.dumps(chunk_report,ensure_ascii=False,indent=2),encoding='utf8')
    if not findings:
        raise ValueError('模型未提取到任何发现。正文已保存，请检查模型响应或换用更合适的模型参数。')
    nodes,deduplicated=merge_findings(findings,sources)
    emit('合并主题并核对节点完整性',75)
    branches=organize(nodes,llm,cfg.chunk_chars)
    tree={'id':'root','label':content.meta.title,'children':branches}
    def leaves(n):
        if not n.get('children'): return [n['id']]
        return sum((leaves(c) for c in n['children']),[])
    if sorted(leaves(tree))!=sorted(n['id'] for n in nodes):
        raise ValueError('导图节点完整性检查失败，已停止导出。')
    if any(not c['findings'] for c in chunk_report):
        warnings.append('部分片段未提取关键发现，详见 chunk_report.json；这不代表该片段没有重要内容。')
    missing=[x for x in ('question','argument','contribution','result','limitation') if not any(n['kind']==x for n in nodes)]
    if missing:
        warnings.append('以下维度未提取到有依据的节点，未自动补编：'+', '.join(missing))
    unmatched=sum(1 for n in nodes if not any(e['matched'] for e in n['evidence']))
    if unmatched:
        warnings.append(f'{unmatched} 个节点的原文摘录未匹配，请在证据面板核对。')
    status={'source':'fixture' if fixture else 'api','model':'本地确定性测试响应（非真实模型）' if fixture else cfg.model,
        'calls':llm.calls,'tokens':llm.tokens,'json_repairs':llm.repairs}
    data={'version':'1.0.0','title':content.meta.title,'filename':path.name,
        'created_at':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'pages':pages,'sources':[asdict(s) for s in sources],'nodes':nodes,'tree':tree,
        'coverage':{'pages_total':len(pages),'pages_with_text':sum(bool(p['text'].strip()) for p in pages),
            'chunks_total':len(chunks),'chunks_analyzed':len(chunk_report),'sources_total':len(sources),
            'sources_analyzed':sum(len(c['source_ids']) for c in chunk_report),'deduplicated':deduplicated},
        'warnings':warnings,'model_info':status,
        'pdf_base64':base64.b64encode(path.read_bytes()).decode('ascii') if cfg.embed_pdf else ''}
    emit('校验 Mermaid 并生成离线看板',88)
    dashboard=export_dashboard(data,out)
    emit('处理完成',100)
    return dashboard
