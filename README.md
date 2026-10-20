# 研脉 PaperWeave

把学术论文 PDF 转成带原文证据的 Mermaid 导图和可离线打开的交互式 HTML 阅读看板。

PaperWeave 按页提取论文，使用可配置的模型接口逐块分析，再把研究问题、方法、贡献、实验结论与局限组织成主题树。每个内容节点保留来源编号、PDF 物理页码和原文摘录，方便从分析结果回到原文。

![PaperWeave 论文阅读看板](outputs/dashboard-preview.png)

## 功能

- **按页解析 PDF**：提取 Markdown 文本，记录章节、物理页码和稳定来源 ID。
- **分块分析长文**：逐块处理全部已提取来源，保存每块的处理记录，再分层归纳主题。
- **证据关联**：节点附原文摘录与页码，标明摘录匹配、分析者推断或未匹配状态。
- **两种 Mermaid 视图**：思维导图与层级结构关系图，支持平移、缩放和主题收起/展开。
- **交互阅读**：节点搜索、局限与边界筛选、原文窗口、可选内嵌 PDF、深浅主题和键盘操作。
- **独立交付**：单文件 HTML 内嵌脚本、样式、分析数据和可选 PDF，保存后可以离线阅读。
- **多格式导出**：HTML、SVG、Mermaid 源码和分析 JSON。
- **接口配置**：通过 Base URL、API Key 和模型 ID 连接 Chat Completions 兼容接口。

## 快速体验

在项目目录依次打开 `outputs` → `teaching-demo`，双击 `dashboard.html`，选择 Edge 或 Chrome 打开。查看已有看板不需要启动 Python 服务或连接网络。

自带示例使用 `examples/teaching-paper.pdf`，是一份包含末页限制条件的四页合成文档，不是已发表论文。看板来自确定性测试响应，页面明确标注其来源，用于体验交互，不代表真实模型的论文分析效果。

安装项目后，也可以重新生成示例：

```powershell
.\.venv\Scripts\python.exe examples/build_demo.py
```

要分析自己的论文，请先完成[模型接口配置](docs/configuration.md)，再使用[网页界面](docs/usage-web.md)或[命令行](docs/usage-cli.md)。

## 文档导航

| 文档 | 内容 |
|---|---|
| [安装指南](docs/install.md) | Python 环境、依赖与浏览器准备 |
| [模型接口配置](docs/configuration.md) | `.env` 三项参数、可选参数与自检 |
| [网页使用指南](docs/usage-web.md) | 上传、生成、阅读证据、导出与离线打开（含截图） |
| [命令行与输出](docs/usage-cli.md) | `analyze` 命令与输出文件说明 |
| [工作原理](docs/how-it-works.md) | 流水线各阶段的设计与保证 |
| [开发与测试](docs/development.md) | 开发环境、测试套件、无密钥联调与运行记录 |
| [示例与已知限制](docs/limitations.md) | 真实论文抽取核查结果与使用边界 |
| [常见问题](docs/faq.md) | 安装、配置与使用问题速查 |

## 项目结构

```text
src/paperweave/
├─ config.py       # 环境变量与本地配置
├─ parser.py       # PDF 按页提取、来源编号与分块
├─ llm.py          # Chat Completions 请求、重试与 JSON 修复
├─ analysis.py     # 证据检查、节点去重与主题归纳
├─ pipeline.py     # 串联处理步骤并保存过程文件
├─ render.py       # Mermaid 校验与单文件 HTML 生成
├─ server.py       # 本地上传与任务接口
├─ __main__.py     # 命令行入口
├─ static/         # 页面、样式、脚本与离线 Mermaid
└─ vendor/         # 保留来源声明的复用模块
```

`examples/` 包含合成教学 PDF 与示例生成脚本；`scripts/` 包含本地确定性模拟模型接口；`tests/` 包含自动化测试；`docs/` 保存说明文档、配图、来源元数据和机器测试记录。

## 开源与复用

PaperWeave 使用 ScholarFlow 的数据模型和部分标题、章节识别代码，改造 mindmap-generator 的递归 Mermaid 编译方式，集成 PyMuPDF4LLM / PyMuPDF 和 Mermaid，并新增按页证据、分层归纳完整性检查、离线看板及本地上传流程。

新增代码采用 AGPL-3.0-or-later。上游 MIT 版权、各依赖授权文本与具体改造来源保留在 [LICENSE](LICENSE)、[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) 和 [licenses/](licenses/) 中。
