import json,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from paperweave.config import Settings
from paperweave.pipeline import run
from fixture_model import FixtureLLM
from create_sample import create

def test_real_http_pipeline_and_last_page(tmp_path):
    fixture=FixtureLLM();requests=[]
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            obj=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            requests.append(obj)
            prompt=obj['messages'][-1]['content']
            result=fixture.json(prompt)
            payload=json.dumps({'choices':[{'message':{'content':json.dumps(result,ensure_ascii=False)},'finish_reason':'stop'}],
                'usage':{'prompt_tokens':1,'completion_tokens':1}}).encode()
            self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(payload)
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    try:
        pdf=tmp_path/'paper.pdf';create(pdf)
        cfg=Settings(f'http://127.0.0.1:{server.server_port}/v1','fixture-key','fixture-local-http',chunk_chars=2500)
        result=run(pdf,tmp_path/'result',cfg,fixture=True)
        data=json.loads(result.with_name('analysis.json').read_text(encoding='utf8'))
        assert data['coverage']['sources_analyzed']==data['coverage']['sources_total']
        assert data['coverage']['chunks_analyzed']==data['coverage']['chunks_total']>=2
        assert any('末页' in n['label'] and n['evidence'][0]['page']==4 for n in data['nodes'])
        assert all(e['matched'] for n in data['nodes'] for e in n['evidence'])
        assert data['validation']['mindmap'] and data['validation']['flowchart']
        assert len(requests)>=data['coverage']['chunks_total']
        assert all(r['model']=='fixture-local-http' for r in requests)
        assert 'fixture-key' not in result.read_text(encoding='utf8')
    finally:
        server.shutdown();server.server_close();thread.join()
