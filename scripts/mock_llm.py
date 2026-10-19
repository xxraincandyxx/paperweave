"""确定性模拟 Chat Completions 接口，用于无密钥端到端联调。

启动后把 .env 的 LLM_BASE_URL 指向 http://127.0.0.1:<端口>/v1，
即可走通「上传界面 → 分析 → 离线看板」完整流程。
响应由 examples/fixture_model.py 的教学规则生成，仅覆盖教学样例关键词，
不代表真实模型质量，不得用于验收演示。
"""
import argparse, json, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'examples'))
from fixture_model import FixtureLLM


class Handler(BaseHTTPRequestHandler):
    fixture = FixtureLLM()

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        prompt = body['messages'][-1]['content']
        result = self.fixture.json(prompt)
        payload = json.dumps({'choices': [{'message': {'content': json.dumps(result, ensure_ascii=False)},
            'finish_reason': 'stop'}], 'usage': {'prompt_tokens': 1, 'completion_tokens': 1}}).encode('utf8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='本地确定性模拟 Chat Completions 接口')
    parser.add_argument('--port', type=int, default=8902)
    args = parser.parse_args()
    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'模拟模型接口：http://127.0.0.1:{args.port}/v1（教学规则响应，非真实模型）')
    server.serve_forever()
