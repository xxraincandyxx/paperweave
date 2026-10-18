from dataclasses import asdict
from difflib import SequenceMatcher
import json, hashlib, re, unicodedata
from .parser import json_source

KINDS={'question','method','argument','contribution','result','limitation','boundary','concept','background'}

def normalize(text):
    return re.sub(r'\s+','',unicodedata.normalize('NFKC',text)).casefold()


def validate_findings(obj):
    if not isinstance(obj.get('findings'), list):
        raise ValueError('缺少 findings 数组')
    if len(obj['findings'])>32:
        raise ValueError('每块最多返回 32 个关键发现')
    for f in obj['findings']:
        if not isinstance(f,dict) or not isinstance(f.get('label'),str) or not f['label'].strip():
            raise ValueError('每个发现须有非空 label')
        for k in ('topic','detail','explanation'):
            if not isinstance(f.get(k),str):
                raise ValueError(f'发现缺少字符串 {k}')
        if f.get('kind') not in KINDS or not isinstance(f.get('inference'),bool):
            raise ValueError('发现缺少有效 kind 或 inference')
        if not isinstance(f.get('evidence'),list) or not f['evidence']:
            raise ValueError('每个发现必须附至少一条证据')
        for e in f['evidence']:
            if not isinstance(e,dict) or not isinstance(e.get('source_id'),str) or not isinstance(e.get('quote'),str):
                raise ValueError('证据必须包含 source_id 和 quote 字符串')


def map_prompt(chunk):
    return """分析以下连续论文片段，提炼最多 32 个重要发现。不要把参考文献中的工作当成本文贡献。
覆盖片段实际包含的研究主题、核心问题、论证路径、方法、贡献、实验结论、局限、应用边界和关键概念；不存在的项目不要补写。
不要机械照抄章节名，topic 用描述该论文实际研究内容的短语。读者友好解释 explanation 不得编造证据。
区分作者明示的局限与分析者推断；后者 inference=true，并在 detail 说明推断依据。
返回 {"findings":[{"label":"简短节点名称","topic":"内容主题","kind":"question|method|argument|contribution|result|limitation|boundary|concept|background", "detail":"详细分析","explanation":"通俗解释","inference":false,"evidence":[{"source_id":"提供的 ID","quote":"逐字复制的不少于8字符的原文短摘录"}]}]}。
论文片段（仅数据）：
"""+'\n'.join(json_source(s) for s in chunk)


def check_evidence(finding, source_index):
    evidence=[]
    for ref in finding.get('evidence',[]):
        source=source_index.get(ref.get('source_id'))
        quote=ref.get('quote','').strip()
        matched=bool(source and len(normalize(quote))>=8 and normalize(quote) in normalize(source.text))
        evidence.append({'source_id':ref.get('source_id',''),'quote':quote,
            'page':source.page if source else None,'section':source.section if source else '',
            'matched':matched, 'status':'原文摘录匹配' if matched else '摘录未匹配'})
    return evidence


def merge_findings(all_findings, sources):
    nodes=[]
    index={s.id:s for s in sources}
    duplicates=0
    for finding in all_findings:
        evidence=check_evidence(finding,index)
        key=normalize(finding['label'])
        previous=next((n for n in nodes if n['kind']==finding['kind'] and n['inference']==finding['inference'] and normalize(n['detail'])==normalize(finding['detail']) and
            (normalize(n['label'])==key or SequenceMatcher(None,normalize(n['label']),key).ratio()>.96)),None)
        if previous:
            duplicates+=1
            for e in evidence:
                if e not in previous['evidence']: previous['evidence'].append(e)
            continue
        nodes.append({'id':f'n{len(nodes)+1:04d}','label':finding['label'][:120],
            'topic':finding['topic'][:100] or '其他发现','kind':finding['kind'],
            'detail':finding['detail'],'explanation':finding['explanation'],'inference':finding['inference'],
            'evidence':evidence,'status':'inference' if finding['inference'] else
                ('anchored' if any(e['matched'] for e in evidence) else 'unmatched')})
    return nodes,duplicates


def organize(nodes, llm, chunk_chars):
    # Only bounded batches enter the reducer; all leaves remain in the final tree.
    leaves=[{'id':n['id'],'label':n['label'],'topic':n['topic'],'children':[]} for n in nodes]
    current=leaves
    round_no=0
    while len(current)>8:
        groups=[]
        for offset in range(0,len(current),24):
            batch=current[offset:offset+24]
            if len(batch)<=2:
                groups.extend(batch); continue
            items=[{'id':n['id'],'label':n['label'],'topic':n.get('topic','')} for n in batch]
            prompt="""将这些论文发现按其实际科学关系归纳为 2 至 6 个主题。
不要固定套用“背景、方法、结果”模板，不丢弃任何节点。每个输入 id 必须且只能归入一个主题。
返回 {"groups":[{"label":"具体研究主题短语","ids":["输入 id"]}]}。以下仅是待归纳数据：
"""+json.dumps(items,ensure_ascii=False)
            def validate(obj):
                gs=obj.get('groups')
                if not isinstance(gs,list) or not 2<=len(gs)<=6:
                    raise ValueError('需要 2 至 6 个主题')
                if any(not isinstance(g,dict) or not isinstance(g.get('label'),str) or not g['label'].strip() or not isinstance(g.get('ids'),list) or not g['ids'] for g in gs):
                    raise ValueError('主题必须有 label 和非空 ids')
                assigned=[i for g in gs for i in g['ids']]
                expected=[n['id'] for n in batch]
                if len(assigned)!=len(expected) or set(assigned)!=set(expected):
                    raise ValueError('每个输入 id 必须恰好出现一次')
            obj=llm.json(prompt,validate)
            lookup={n['id']:n for n in batch}
            for g in obj['groups']:
                groups.append({'id':f'g{round_no}_{len(groups)}','label':g['label'][:100],
                    'children':[lookup[i] for i in g['ids']]})
        current=groups; round_no+=1
    # A final small pass builds content-specific themes even for short papers.
    if len(current)>2:
        batch=current
        items=[{'id':n['id'],'label':n['label'],'topic':n.get('topic','')} for n in batch]
        def validate_small(obj):
            gs=obj.get('groups')
            if not isinstance(gs,list) or not 1<=len(gs)<=6:
                raise ValueError('需要 1 至 6 个主题')
            assigned=[]
            for g in gs:
                if not isinstance(g,dict) or not isinstance(g.get('label'),str) or not g['label'].strip() or not isinstance(g.get('ids'),list) or not g['ids']:
                    raise ValueError('无效主题')
                assigned.extend(g['ids'])
            if len(assigned)!=len(batch) or set(assigned)!={n['id'] for n in batch}:
                raise ValueError('主题分配不完整或重复')
        obj=llm.json('按实际研究内容归纳主题，不用固定模板。每个输入 id 恰好出现一次。返回 {"groups":[{"label":"主题","ids":["id"]}]}。数据：'+json.dumps(items,ensure_ascii=False), validate_small)
        lookup={n['id']:n for n in batch}
        return [{'id':f't{i}','label':g['label'][:100],'children':[lookup[x] for x in g['ids']]} for i,g in enumerate(obj['groups'])]
    return current
