"""PyMuPDF4LLM pages + ScholarFlow data models and section detection."""
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib, re
import pymupdf
import pymupdf4llm
from .vendor.scholarflow_models import PaperContent, PaperMeta
from .vendor.scholarflow_sections import detect_sections, HEADING_RE, guess_title_from_text

@dataclass
class Source:
    id: str
    page: int
    section: str
    text: str


def parse_pdf(path: Path):
    warnings=[]
    with pymupdf.open(path) as doc:
        if doc.needs_pass:
            raise ValueError('PDF 已加密，请先提供可打开的未加密副本。')
        if not len(doc):
            raise ValueError('PDF 没有页面。')
        metadata=doc.metadata or {}
        page_count=len(doc)
        # Disable the optional Layout engine; keep the open-source extraction path explicit.
        if hasattr(pymupdf4llm, 'use_layout'):
            pymupdf4llm.use_layout(False)
        pages=[]
        for number in range(page_count):
            try:
                result=pymupdf4llm.to_markdown(doc, pages=[number], page_chunks=True,
                    show_progress=False, write_images=False)
                text=result[0]['text'] if result else ''
            except Exception:
                text=doc[number].get_text('text', sort=True)
                warnings.append(f'第 {number+1} 页使用 PyMuPDF 备用提取；请核对阅读顺序。')
            pages.append({'page': number+1, 'text': text})
            if len(text.strip()) < 20:
                warnings.append(f'第 {number+1} 页可提取文字不足，可能为扫描页或空白页；未自动执行 OCR。')
        full='\n\n'.join(p['text'] for p in pages)
        if len(full.strip()) < 80:
            raise ValueError('未提取到足够正文。基础版支持文本型 PDF；扫描件请先 OCR 后再导入。')
        title=(metadata.get('title') or '').strip()
        if len(title)<5 or title.lower().startswith(('untitled','microsoft word')):
            first_page=doc[0].get_text('text',sort=True)
            title=guess_title_from_text(first_page)
            # Prefer actual title-sized lines over copyright / permission boilerplate.
            lines=[]
            for block in doc[0].get_text('dict')['blocks']:
                for line in block.get('lines',[]):
                    spans=line.get('spans',[])
                    text=''.join(s.get('text','') for s in spans).strip()
                    size=max((s.get('size',0) for s in spans),default=0)
                    direction=line.get('dir',(1,0))
                    if len(text)>5 and abs(direction[1])<.1 and direction[0]>.9 and line['bbox'][1]<doc[0].rect.height*.6:
                        lines.append((size,line['bbox'][1],text))
            if lines:
                largest=max(x[0] for x in lines)
                candidates=[x for x in lines if x[0]>=largest*.95 and len(x[2])>7]
                candidates.sort(key=lambda x:x[1])
                if candidates:
                    top=candidates[0][1]
                    title=' '.join(x[2] for x in candidates if x[1]-top<100)
            title=title or path.stem
        content=PaperContent(meta=PaperMeta(title=title[:200]), full_text=full,
            sections=detect_sections(full), pdf_path=path, num_pages=page_count)
        toc=doc.get_toc()
    sources=[]
    heading='正文'
    for page in pages:
        for entry in toc:
            if entry[2] == page['page']:
                heading=entry[1]
        # Small stable source blocks retain page and section while preventing giant paragraphs.
        for paragraph in re.split(r'\n\s*\n', page['text']):
            paragraph=paragraph.strip()
            if not paragraph:
                continue
            first=paragraph.splitlines()[0].strip()
            if (first.startswith('#') or HEADING_RE.fullmatch(first) or
                re.fullmatch(r'(?:\d+(?:\.\d+)*[.、]?\s*)?(?:摘要|引言|绪论|方法|实验|结果|讨论|结论|参考文献|附录).*', first)) and len(first)<90:
                heading=first.strip('# ')
            for start in range(0,len(paragraph),1200):
                sources.append(Source(f'p{page["page"]:04d}b{len(sources)+1:05d}',page['page'],heading,paragraph[start:start+1200]))
    return content, pages, sources, warnings


def make_chunks(sources, limit):
    chunks=[]
    current=[]
    size=0
    for source in sources:
        cost=len(json_source(source))+2
        if current and size+cost>limit:
            chunks.append(current); current=[]; size=0
        current.append(source); size+=cost
    if current:
        chunks.append(current)
    return chunks


def json_source(source):
    import json
    return json.dumps(asdict(source),ensure_ascii=False)
