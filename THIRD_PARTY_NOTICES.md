# 融合、改造与第三方来源

这份说明区分直接代码复用、改造复用、依赖集成和流程参考，不把独立新增模块算成上游原有能力。

## ScholarFlow

- 仓库：https://github.com/bcefghj/scholarflow
- 锁定 commit：`cc66f78379493ad230ada60dbedf420165057230`
- 原始许可：MIT，Copyright (c) 2026 ScholarFlow Team，全文保留在 `licenses/ScholarFlow-MIT.txt`。
- **直接复用**：`scholarflow/models.py` → `src/paperweave/vendor/scholarflow_models.py`，使用 `PaperMeta`、`PaperContent`、`PaperSection`。
- **选择性代码复用**：`scholarflow/parser/pdf_parser.py` 中的章节常量、正则、`_detect_sections` 与 `_guess_title_from_text` → `vendor/scholarflow_sections.py`，新增公开别名以供融合。
- **改进**：在新的按页解析器里补充来源 ID、中文/Markdown 标题识别和字号/文字方向标题判断；避免将首页版权或侧边水印认成论文题目。
- **流程参考**：独立解析、分析与生成阶段；不引入与本题无关的 PPT/LaTeX 功能和依赖，也不沿用 Markmap CDN 输出。

## mindmap-generator

- 仓库：https://github.com/Dicklesworthstone/mindmap-generator
- 锁定 commit：`4b835da675c17cf19f286591a975385d690c8460`
- 原仓库 README 的 License 部分声明 MIT；该 commit 没有单独 LICENSE 文件。原 README 的许可声明与来源记录保留在 `licenses/mindmap-generator-NOTICE.txt`。不捏造缺失的版权声明。
- **改造复用**：`mindmap_generator.py` 中 `_generate_mermaid_mindmap`、`_add_node_to_mindmap` 的递归层级生成方式 → `vendor/mindmap_compiler.py`。保留 mindmap 层级语法，改为稳定节点 ID、明确标签转义和统一 children，不发送 emoji 选择 API。
- **分析流程参考**：提取、层级归纳、去重、来源检查。
- **修正**：不沿用“检查异常也可视为通过”的语义核验分支，不在达到若干主题后提前停止全文处理；模型名和地址配置化。

## PyMuPDF4LLM / PyMuPDF

- 仓库：https://github.com/pymupdf/pymupdf4llm
- 实测安装版本：PyMuPDF4LLM `1.28.2`、PyMuPDF `1.28.2`。
- **依赖集成**：`to_markdown(..., page_chunks=True)` 按物理页读取；文本块保留页码/章节；异常页使用 PyMuPDF 备用读取并提示。
- 明确调用 `use_layout(False)`，使用开源提取路径；不随本项目分发可选 Layout 模型或二进制。
- 包元数据声明双重许可：GNU AGPL 3.0 或 Artifex 商业许可。此开源交付选择 AGPL 路径，新增代码使用 AGPL-3.0-or-later；原始授权文本保留在 `licenses/PyMuPDF4LLM-AGPL-3.0.txt` 和项目 `LICENSE`。

## Mermaid

- 仓库：https://github.com/mermaid-js/mermaid
- 实测版本：`11.12.0`；MIT，见 `licenses/Mermaid-MIT.txt`。
- **依赖集成**：通过 esbuild 构建单个内嵌浏览器脚本；生成时调用真实 Mermaid parse/render；看板在 file:// 离线使用相同渲染器。
- Node 依赖精确树见 `package-lock.json`，各包原始 LICENSE/NOTICE 随 `licenses/npm/` 保留；bundle 内也保留构建器生成的法律注释。

## 本项目新增

`config.py`、按页来源提取适配器、结构化模型请求/重试、Unicode 引文匹配、全文分析记录、保守去重、带 ID 完整性检查的分层归纳、Mermaid 浏览器校验与规则修复、离线看板/导出、本地上传服务、命令行、验收测试和教学材料。

仓库克隆仅用于工作区参考，不放入提交包；上游 `.env` 不读取、不使用、不复制。没有将原项目附带的配置或密钥带入本项目。
