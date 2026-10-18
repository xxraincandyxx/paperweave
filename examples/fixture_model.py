"""Deterministic test double. Never a substitute for real API validation."""
import json,re

class FixtureLLM:
    def __init__(self):
        self.calls=0;self.tokens={'input':0,'output':0};self.repairs=0
    def json(self,prompt,validate=None):
        self.calls+=1
        if '"findings"' in prompt:
            sources=[]
            for line in prompt.splitlines():
                try:
                    obj=json.loads(line)
                    if isinstance(obj,dict) and 'text' in obj and 'id' in obj:sources.append(obj)
                except json.JSONDecodeError:pass
            findings=[]
            rules=[
                ('core question','question','稳定来源能否穿过分块流程','可追溯阅读的研究问题','把信息拆开分析之后，还能找到它最初在哪一页吗？'),
                ('Our contribution','contribution','先保留来源，再组织结论','来源优先的处理流程','先给原文编号，再让每条发现指回它的依据。'),
                ('Each paragraph receives','method','段落绑定来源 ID 与页码','来源优先的处理流程','每段文字都有自己的编号和 PDF 页序。'),
                ('First preserve','argument','先提取，再分析，最后合并','来源优先的处理流程','先建证据底稿，然后逐块阅读，最后组织主题。'),
                ('does not prove','boundary','原文匹配不等于结论成立','核对与阅读边界','能找到引文，还需要再看它是否真的支持结论。'),
                ('self-contained','method','导图与证据打包在单个看板','离线交付与阅读体验','渲染代码和论文内容一起放进 HTML 文件。'),
                ('not an evaluation','limitation','测试响应不能代表模型质量','核对与阅读边界','软件跑通和模型读懂论文是两件需要分别验证的事。'),
                ('records analyzed','result','分析分块留有覆盖记录','离线交付与阅读体验','可以检查每个片段是否实际经过处理。'),
                ('synthetic text','limitation','教学文本不能替代真实论文验证','核对与阅读边界','这个示例用于测试流程，不用于证明科研分析准确率。'),
                ('Image-only','boundary','扫描论文需要先执行 OCR','核对与阅读边界','图片里的文字需要先识别出来才能分析。'),
                ('TAIL_SENTINEL','result','末页内容进入分析覆盖记录','离线交付与阅读体验','即便关键内容在最后一页，也应该进入分析流程。')]
            for s in sources:
                for match,kind,label,topic,explanation in rules:
                    if match.lower() in s['text'].lower():
                        sentence=next((line.strip(' #*') for line in s['text'].splitlines() if match.lower() in line.lower()),s['text'][:240])
                        findings.append({'label':label,'topic':topic,'kind':kind,'detail':sentence,
                            'explanation':explanation,'inference':False,'evidence':[{'source_id':s['id'],'quote':sentence}]})
            result={'findings':findings[:32]}
        else:
            items=json.loads(prompt[prompt.rfind('数据：')+3:])
            buckets={}
            for item in items:
                topic=item.get('topic') or ('核对与阅读边界' if any(w in item['label'] for w in ['边界','核对']) else '来源与阅读流程')
                buckets.setdefault(topic,[]).append(item['id'])
            if len(buckets)==1 and len(items)>2:
                keys=list(buckets); ids=buckets.pop(keys[0]);buckets={keys[0]+' A':ids[::2],keys[0]+' B':ids[1::2]}
            result={'groups':[{'label':k,'ids':v} for k,v in buckets.items()]}
        if validate:validate(result)
        return result
