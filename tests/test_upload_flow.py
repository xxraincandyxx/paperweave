"""浏览器级上传流程：上传界面 → 任务轮询 → 离线看板，全程不调用真实 API。"""
import json, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from create_sample import create
from fixture_model import FixtureLLM


def test_browser_upload_flow_produces_offline_dashboard(tmp_path, monkeypatch):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
            result = FixtureLLM().json(body['messages'][-1]['content'])
            payload = json.dumps({'choices': [{'message': {'content': json.dumps(result, ensure_ascii=False)},
                'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 1, 'completion_tokens': 1}}).encode('utf8')
            self.send_response(200); self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload))); self.end_headers(); self.wfile.write(payload)
        def log_message(self, *args): pass
    mock = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    threading.Thread(target=mock.serve_forever, daemon=True).start()
    # 环境变量优先于 .env（load_dotenv 不覆盖已有变量），避免依赖本机配置。
    monkeypatch.setenv('LLM_BASE_URL', f'http://127.0.0.1:{mock.server_port}/v1')
    monkeypatch.setenv('LLM_API_KEY', 'test-browser-key')
    monkeypatch.setenv('LLM_MODEL', 'fixture-browser')
    monkeypatch.setenv('EMBED_PDF', '0')
    import uvicorn
    from paperweave.server import app
    server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=0, log_level='warning'))
    thread = threading.Thread(target=server.run, daemon=True); thread.start()
    while not server.started:
        time.sleep(0.05)
    port = server.servers[0].sockets[0].getsockname()[1]
    try:
        from playwright.sync_api import sync_playwright, expect
        from paperweave.render import browser_launch
        pdf = tmp_path / 'paper.pdf'; create(pdf)
        with sync_playwright() as p:
            browser = browser_launch(p)
            try:
                page = browser.new_context(viewport={'width': 1440, 'height': 900}).new_page()
                page.goto(f'http://127.0.0.1:{port}/')
                expect(page.locator('#config')).to_contain_text('模型已配置')
                page.set_input_files('#file', str(pdf))
                page.locator('#submit').click()
                expect(page.locator('#status')).to_have_text('离线看板已生成', timeout=180000)
                page.goto(f'http://127.0.0.1:{port}' + page.get_attribute('#result a', 'href'))
                expect(page.locator('#render-state')).to_have_text('Mermaid 已校验', timeout=30000)
                assert page.locator('#diagram svg').count() == 1
                expect(page.locator('.node-button').first).to_be_visible()
                assert page.locator('#notice').count() == 0 or '非真实模型' not in page.locator('#notice').inner_text()
            finally: browser.close()
    finally:
        server.should_exit = True; thread.join(timeout=10)
        mock.shutdown(); mock.server_close()
