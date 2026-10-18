import json
from pathlib import Path
from dataclasses import asdict
import pymupdf, pytest
from paperweave.parser import Source,make_chunks,parse_pdf
from paperweave.analysis import check_evidence,organize,merge_findings
from paperweave.llm import LLM
from paperweave.config import Settings
from paperweave.vendor.mindmap_compiler import generate_mindmap
from fixture_model import FixtureLLM

def test_full_coverage_without_truncation():
    sources=[Source(f'p{i}',i,'section','A'*1100) for i in range(1,151)]
    chunks=make_chunks(sources,2500)
    assert [s.id for chunk in chunks for s in chunk]==[s.id for s in sources]
    assert chunks[-1][-1].page==150
    assert all(sum(len(json.dumps(asdict(s),ensure_ascii=False))+2 for s in c)<=2500 for c in chunks)

def test_fabricated_quote_and_unknown_source_not_verified():
    src=Source('p1',1,'Methods','We preserve the complete source text and physical page numbers.')
    finding={'evidence':[{'source_id':'p1','quote':'We preserve the complete source text'},
        {'source_id':'p1','quote':'The model always proves scientific truth'},
        {'source_id':'p99','quote':'We preserve the complete source text'}]}
    checked=check_evidence(finding,{'p1':src})
    assert [e['matched'] for e in checked]==[True,False,False]
    assert checked[2]['page'] is None

def test_entire_tree_retained_in_recursive_reduction():
    nodes=[{'id':f'n{i}','label':f'finding {i}','topic':f'science topic {i%4}'} for i in range(130)]
    tree=organize(nodes,FixtureLLM(),2500)
    def leaves(n):return sum((leaves(c) for c in n.get('children',[])),[]) if n.get('children') else [n['id']]
    assigned=sum((leaves(n) for n in tree),[])
    assert sorted(assigned)==sorted(n['id'] for n in nodes)

def test_dedup_does_not_merge_opposite_claims():
    src=Source('p1',1,'Results','The effect is not established under the second condition.')
    a={'label':'effect','kind':'result','topic':'effect','detail':'effect increases','explanation':'x','inference':False,'evidence':[{'source_id':'p1','quote':src.text}]}
    b={**a,'detail':'effect does not increase'}
    nodes,count=merge_findings([a,b,a],[src])
    assert len(nodes)==2 and count==1

def test_encrypted_and_scanned_pdf_fail_with_actionable_errors(tmp_path):
    path=tmp_path/'secret.pdf'
    with pymupdf.open() as doc:
        doc.new_page().insert_text((40,40),'Confidential test document')
        doc.save(path,encryption=pymupdf.PDF_ENCRYPT_AES_256,user_pw='test-password')
    with pytest.raises(ValueError,match='加密'):parse_pdf(path)
    blank=tmp_path/'scan.pdf'
    with pymupdf.open() as doc:
        doc.new_page();doc.save(blank)
    with pytest.raises(ValueError,match='OCR'):parse_pdf(blank)

def test_llm_repairs_invalid_json_and_uses_configured_model(monkeypatch):
    import httpx
    sent=[]
    def handler(req):
        obj=json.loads(req.content);sent.append(obj)
        content='not JSON' if len(sent)==1 else '{"ok":true}'
        return httpx.Response(200,json={'choices':[{'message':{'content':content},'finish_reason':'stop'}]})
    client=httpx.Client
    monkeypatch.setattr(httpx,'Client',lambda **kw:client(transport=httpx.MockTransport(handler),**kw))
    llm=LLM(Settings('https://model.invalid/v1','fixture-key','organizer-exact-model'))
    assert llm.json('test')['ok']
    assert llm.repairs==1 and all(s['model']=='organizer-exact-model' for s in sent)

def test_auth_failure_redacts_body_and_key(monkeypatch):
    import httpx
    client=httpx.Client
    monkeypatch.setattr(httpx,'Client',lambda **kw:client(transport=httpx.MockTransport(lambda req:httpx.Response(401,text='private key contents')),**kw))
    with pytest.raises(ValueError) as error:LLM(Settings('https://model.invalid','private-key-value','model')).json('x')
    assert 'private' not in str(error.value)

def test_mermaid_label_injection_is_removed():
    code=generate_mindmap({'id':'root','label':'<script> bad " )) %%{init:evil}', 'children':[]})
    assert '<script>' not in code and '%%{' not in code and '\n' not in code.splitlines()[-1]


def test_title_uses_large_text_not_permission_notice(tmp_path):
    path=tmp_path/'notice.pdf'
    with pymupdf.open() as doc:
        page=doc.new_page()
        page.insert_text((40,35),'Provided proper attribution is provided, permission is granted.',fontsize=8)
        page.insert_text((40,110),'A Correct Research Title',fontsize=20)
        page.insert_textbox(pymupdf.Rect(40,160,540,600),'This paper studies traceability in long documents. '*20,fontsize=11)
        doc.save(path)
    content,_,_,_=parse_pdf(path)
    assert content.meta.title=='A Correct Research Title'
