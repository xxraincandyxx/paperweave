# 研脉 PaperWeave · 文档解析智能体

将文本型学术论文 PDF 一键转为 **真实 Mermaid 导图 + 可离线打开的交互式 HTML 论文看板**。

本项目按两份比赛文件实现，融合 ScholarFlow 的论文数据模型、章节和标题识别，改造 mindmap-generator 的递归导图生成方式，接入 PyMuPDF4LLM 的按页提取，并新增来源核对、全文覆盖记录、分层合并、离线交互和验收配置。详见 [融合与来源说明](THIRD_PARTY_NOTICES.md) 和 [比赛要求对照表](docs/比赛要求对照表.md)。

> 当前交付含可运行源码、离线 Mermaid 依赖和明确标记的教学示例。没有用户提供的真实模型密钥，因此**尚未实测主办方的 DeepSeek V4 Pro**，也不声称已经通过现场验收。教学示例使用本地确定性测试响应，不是模型生成成果。

## 先看效果

双击 `outputs/teaching-demo/dashboard.html`，无需安装 Python、无需服务器、无需网络。

- 左侧：主题与节点索引、全文关键词搜索、局限与边界筛选。
- 中间：Mermaid 思维导图与结构关系图；拖动、滚轮缩放、主题收起/展开、节点选择。
- 右侧：节点分析、通俗解释、PDF 物理页码、章节、原文摘录和匹配状态。
- 支持原文全文、内嵌 PDF、深浅主题、HTML / SVG / Mermaid / JSON 导出。
- “原文摘录匹配”只说明引文存在，不表示模型结论已通过语义事实核验；推断与未匹配节点均单独标注。

## 环境与安装

实测 Windows、Python 3.12、Microsoft Edge。建议 Python 3.12；项目支持 Python 3.10 及以上（其他系统尚未在本机验证）。

在本项目目录打开 PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
```

程序用真实 Chromium 内核校验和渲染 Mermaid。Windows 安装了 Edge 时可直接使用；如无 Edge / Chrome：

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

正常运行不需要 Node。`src/paperweave/static/mermaid.bundle.js` 已打包进提交文件；只有修改前端依赖后需要 Node 20+：

```powershell
npm ci
npm run build
```

## 模型 API 配置

```powershell
Copy-Item .env.example .env
```

编辑 `.env` 中三项：

```dotenv
LLM_BASE_URL=https://your-provider.example/v1
LLM_API_KEY=填写你自己的密钥
LLM_MODEL=填写服务商提供的准确模型ID
```

- 验收时填入主办方提供的 **DeepSeek V4 Pro 精确模型 ID、Base URL、API Key**。不能用展示名称猜模型 ID。
- Base URL 可为 `https://host/v1`，程序追加 `/chat/completions`；也支持直接配置完整的该接口地址。
- 使用 Chat Completions 兼容协议；不固定模型、不固定供应商，不发送特定模型才支持的温度或 JSON 模式参数。
- 系统环境变量优先于 `.env`。真实密钥不写源码、不输出到日志、不放进 HTML，不应放进提交包。
- 原文片段会发送至所配置的模型 API；**生成时需联网，生成后的看板不需联网**。
- `CHUNK_CHARS`、`LLM_MAX_TOKENS`、`LLM_TIMEOUT`、`LLM_RETRIES`、`EMBED_PDF` 均可配置。

检查安装与配置（不调用真实 API）：

```powershell
.\.venv\Scripts\python.exe -m paperweave doctor
```

## 一键运行

### 命令行：指定任意评委论文

```powershell
.\.venv\Scripts\python.exe -m paperweave analyze "D:\papers\论文.pdf" -o "outputs\我的论文"
```

从 PDF 提取到 HTML 全程自动，不要求输入 Prompt、选择模板或人工指定论文结构。命令失败时返回非零退出码并显示中文原因。**正常运行路径绝不会自动使用教学测试响应替代真实模型。**

### 本地上传界面

```powershell
.\.venv\Scripts\python.exe -m paperweave serve
```

浏览器打开 `http://127.0.0.1:8765`，选择 / 拖入 PDF，点击“生成论文看板”。进度自动更新，完成后打开看板。

服务只监听本机，最多三个排队/执行任务；单个 PDF 上限 80 MB。上传结果保存在 `outputs/runs/<任务ID>/`。关闭服务后，这些文件仍然存在；重启后直接从目录打开结果。

## 输出文件

| 文件 | 用途 |
|---|---|
| `dashboard.html` | 内嵌 Mermaid、CSS、交互脚本、结构数据、原文和可选 PDF 的单文件离线看板 |
| `mindmap.mmd` | Mermaid mindmap 格式导图 |
| `flowchart.mmd` | 同一主题树的 Mermaid 层级结构图；连线表示层级归属，不擅自表示因果 |
| `analysis.json` | 节点、主题树、证据、模型调用统计与校验结果 |
| `extracted.md` | 带物理页码锚点的全文提取结果 |
| `extracted.json` | 按页文本、章节、稳定来源 ID |
| `chunk_report.json` | 每个已分析块的来源 ID、页码与发现数 |

HTML 与 JSON 默认内嵌 PDF，文件会相应变大；不需要内嵌原件时设置 `EMBED_PDF=0`，页码与提取原文仍保留。内嵌 PDF 的 `#page` 跳转取决于浏览器自带阅读器；提取文本定位始终可用。

## 全文与可靠性设计

1. PyMuPDF4LLM 按页提取，保留表格 Markdown 和来源；提取异常时使用 PyMuPDF 备用读取并明确提示。使用开源提取路径，关闭可选 Layout 模块。
2. 每页拆成最多 1200 字符的来源块，再按预算组成分析块；不截断到前几页，不在发现足够主题时提前结束。
3. 所有块依次调用 API，模型输出 JSON 后检查结构、类别、证据 ID；不合法时最多两次结构修复。
4. 证据必须来自本块来源；对摘录做 Unicode 与空白规范化匹配。引文未匹配保留显眼标记，不伪造“核验通过”。
5. 保守去重：只合并类别、推断标记、详细陈述一致的节点，合并其证据，避免将相反结论合并。
6. 每批最多 24 个节点分层归纳。每个输入 ID 必须恰好分配一次；最终叶子集合必须等于所有分析节点，防止合并时静默丢失。
7. 程序编译 Mermaid，使用真实 `mermaid.parse()` 校验两种格式，使用 Chromium 实际渲染思维导图；失败尝试移除标签结构字符规则修复，仍失败则明确报错。
8. 导出包含所有渲染资源的 HTML；浏览器离线模式测试通过，无 HTTP(S) 资源请求。

分块全部完成不等于模型已理解所有科学信息；没有依据的维度会显示“未提取”，不自动编造。扫描 PDF、加密 PDF、复杂图像公式和无文本图表不在文本型 PDF 基础承诺内；混合文档的低文字页会显示警告。

## 测试与复验

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe examples/build_demo.py
.\.venv\Scripts\python.exe -m pytest -q --basetemp .test-tmp
```

测试包括：全文块无截断、分层合并无漏节点、伪造引文标记、相反结论不合并、API JSON 修复与密钥脱敏、加密/扫描件错误处理、本地 HTTP 端到端、末页内容进入导图、离线 HTML 交互与导出、移动端、跨站请求阻断、浏览器级上传流程。实测结果见 `outputs/test-results.xml` 和 `docs/测试与验收记录.md`。

无需真实密钥即可联调完整界面流程：运行 `python scripts/mock_llm.py` 启动确定性模拟 Chat Completions 接口，把 `.env` 的 `LLM_BASE_URL` 指向 `http://127.0.0.1:8902/v1`，再执行 `serve`，即可在浏览器中走通「上传 → 分析 → 看板」。`tests/test_upload_flow.py` 在 pytest 内自动执行同一流程；模拟响应来自教学规则，不代表真实模型质量。

另外用公开的《Attention Is All You Need》15 页 PDF 检查真实双栏解析，254 个来源片段全部分配到 7 个块。**仅测试提取与分块，未调用真实模型**；第 14 页文字不足的警告保留在 `outputs/real-pdf-smoke.json`。

## 常见问题

- **Python 不启动**：Windows 的 `python.exe` 可能是商店入口，请先安装 Python 3.12 并使用虚拟环境内的完整命令。
- **模型配置缺失 / 模型 ID 不正确**：检查 `.env` 的三项参数。Base URL 以服务商通知为准；环境变量可能覆盖文件配置。
- **401 / 403**：检查密钥与模型访问权限；服务响应正文不写入日志，避免泄漏凭据。
- **超时 / 429**：已有有界重试；可增大超时或降低每块字符数。已提取全文留在输出目录，不会把失败伪装为成功。
- **模型输出达到 token 上限**：减小 `CHUNK_CHARS` 或增大 `LLM_MAX_TOKENS`，再重跑。超限不会作为完整 JSON 继续使用。
- **浏览器缺失**：安装 Edge 或执行 Playwright Chromium 安装命令。
- **PDF 几乎无正文**：先 OCR；加密文件先提供未加密副本。
- **API 花费与处理时间**：与论文长度和模型有关；每块单独请求，另有有限的主题归纳/结构修复请求，不承诺固定秒数或固定费用。
- **界面字号较小**：滚轮缩放或收起主题；原文、节点详情和搜索不依赖图中字号。

## 提交前必须完成的验收

1. 使用主办方提供的准确 DeepSeek V4 Pro 参数，对一篇未参与开发的真实论文运行完整流程。
2. 人工核对研究问题、论证路径、贡献、结果数值、局限与边界；特别核对“分析者推断”和“未匹配”节点。
3. 停止本地服务并断网，双击实际生成的 `dashboard.html` 验证交互。
4. 将真实模型生成的示例放入 `outputs/`，保留当前教学示例的来源标识，不把测试响应当作模型实测成果。
5. 按比赛要求将提交包改名为 `实际队伍名称_文档解析智能体.zip`，确认不含 `.env`、密钥、虚拟环境和 node_modules。

## 开源与复用

本项目新增代码按 AGPL-3.0-or-later 发布，以明确适配所使用的 PyMuPDF / PyMuPDF4LLM 开源依赖。MIT 上游版权与授权声明保留在 `licenses/`；具体模块、上游 commit、改造内容与第三方 JS 授权见 `THIRD_PARTY_NOTICES.md` 和 `licenses/`。本地开发依赖不会打进参赛压缩包，已构建的离线 Mermaid 资源会随源码提交。
