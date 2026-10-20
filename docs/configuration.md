# 模型接口配置

[← 返回 README](../README.md)

## 1. 创建配置文件

```powershell
if (-not (Test-Path -LiteralPath ".env")) {
    Copy-Item -LiteralPath ".env.example" -Destination ".env"
}
notepad .env
```

在 `.env` 中填写三项真实参数，替换模板中的占位内容：

```dotenv
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=填写自己的API密钥
LLM_MODEL=填写服务商提供的准确模型ID
```

在编辑器按 Ctrl+S 保存，确认文件名是 `.env`，不是 `.env.txt`。上述创建命令保留已有配置文件。

- Base URL 可以是 `https://host/v1`，程序会追加 `/chat/completions`；也支持完整的 Chat Completions 接口地址。
- 模型 ID 以服务商文档和账号权限为准。程序不固定模型或供应商，也不发送特定模型才支持的温度或 JSON 模式参数。
- 系统环境变量优先于 `.env`。修改配置后应退出旧服务并重新启动，再刷新页面。
- 原文片段会发送到配置的模型服务。生成时必须能连接该服务；使用远端服务时需要网络，生成后的 HTML 可以离线打开。
- `.env` 只保存在本机。密钥不写入源码、分析结果和导出的 HTML，也不应提交到 Git。

## 2. 可选参数

| 参数 | 默认值 | 作用 |
|---|---|---|
| `CHUNK_CHARS` | `10000` | 分析块的字符预算，包含序列化来源信息；范围 2000–24000 |
| `LLM_MAX_TOKENS` | `5000` | 单次请求的输出 token 上限；范围 512–32000 |
| `LLM_TIMEOUT` | `180` | HTTP 请求超时设置，单位为秒，必须大于 0 |
| `LLM_RETRIES` | `2` | 连接或部分服务错误的重试次数；范围 0–5 |
| `EMBED_PDF` | `1` | 是否把原 PDF 内嵌到看板和分析 JSON；设为 `0` 可减小文件 |

## 3. 检查本地配置

```powershell
.\.venv\Scripts\python.exe -m paperweave doctor
```

该命令检查配置完整性、浏览器和 Mermaid 资源，不调用真实 API。因此检查通过不等于密钥和模型权限已经验证。

## 4. 无密钥联调（可选）

没有真实 API Key 时，可用仓库自带的确定性模拟接口走通全流程：

```powershell
# 终端 1：启动模拟模型接口（响应来自教学规则，不代表真实模型质量）
.\.venv\Scripts\python.exe scripts\mock_llm.py

# 终端 2：把 .env 的 LLM_BASE_URL 指向 http://127.0.0.1:8902/v1 后启动服务
.\.venv\Scripts\python.exe -m paperweave serve
```

自动化测试 `tests/test_upload_flow.py` 在 pytest 内自动执行同一流程。
