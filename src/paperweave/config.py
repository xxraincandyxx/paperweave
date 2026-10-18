from dataclasses import dataclass
from pathlib import Path
import os
from urllib.parse import urlsplit
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]

@dataclass
class Settings:
    base_url: str = ''
    api_key: str = ''
    model: str = ''
    chunk_chars: int = 10000
    max_tokens: int = 5000
    timeout: int = 180
    retries: int = 2
    embed_pdf: bool = True

    @classmethod
    def load(cls, env_file=None):
        load_dotenv(env_file or ROOT / '.env', override=False)
        result = cls(os.getenv('LLM_BASE_URL', '').rstrip('/'), os.getenv('LLM_API_KEY', ''),
            os.getenv('LLM_MODEL', ''), int(os.getenv('CHUNK_CHARS', '10000')),
            int(os.getenv('LLM_MAX_TOKENS', '5000')), int(os.getenv('LLM_TIMEOUT', '180')),
            int(os.getenv('LLM_RETRIES', '2')), os.getenv('EMBED_PDF', '1') == '1')
        if not 2000 <= result.chunk_chars <= 24000:
            raise ValueError('CHUNK_CHARS 应在 2000 至 24000 之间。')
        if not 512 <= result.max_tokens <= 32000 or not 0 <= result.retries <= 5 or result.timeout <= 0:
            raise ValueError('模型 token、重试或超时配置无效。')
        return result

    def validate(self):
        if not all([self.base_url, self.api_key, self.model]):
            raise ValueError('请在 .env 配置 LLM_BASE_URL、LLM_API_KEY、LLM_MODEL；验收时填入主办方提供的准确参数。')
        url = urlsplit(self.base_url)
        if url.scheme not in {'https', 'http'} or not url.netloc or url.username or url.password:
            raise ValueError('LLM_BASE_URL 必须是无内嵌用户名或密码的 HTTP(S) 地址。')
        if self.model.startswith('REPLACE_'):
            raise ValueError('请将 LLM_MODEL 占位符替换为主办方提供的实际模型 ID。')
