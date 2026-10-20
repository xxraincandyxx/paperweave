# 命令行与输出

[← 返回 README](../README.md)

## 命令行分析

```powershell
.\.venv\Scripts\python.exe -m paperweave analyze "D:\papers\论文.pdf" -o "outputs\我的论文"
```

程序自动完成提取、分析、主题归纳和看板生成，不要求输入提示词或选择模板。处理状态输出到终端；失败时返回非零退出码并显示原因。

也可指定配置文件：

```powershell
.\.venv\Scripts\python.exe -m paperweave analyze "D:\papers\论文.pdf" -o "outputs\我的论文" --env ".env.local"
```

完成后直接打开输出目录里的 `dashboard.html`。

## 输出文件

命令行使用 `-o` 指定目录。网页上传结果保存在 `outputs/runs/<任务ID>/`，服务重启后可以直接从目录打开已生成结果。

| 文件 | 内容 |
|---|---|
| `input.pdf` | 网页上传服务保存的原件；看板中可能显示这一内部文件名 |
| `dashboard.html` | 内嵌 Mermaid、样式、交互脚本、分析数据、原文和可选 PDF 的离线看板 |
| `mindmap.mmd` | Mermaid mindmap 格式源码 |
| `flowchart.mmd` | Mermaid 层级结构关系图源码 |
| `analysis.json` | 内容节点、主题树、证据、覆盖记录、模型调用统计与校验信息 |
| `extracted.md` | 带物理页码锚点的全文提取结果 |
| `extracted.json` | 按页文本、章节和稳定来源 ID |
| `chunk_report.json` | 每个分析块的来源 ID、页码、发现数与处理状态 |

默认内嵌 PDF 会增大 HTML 与 JSON。`EMBED_PDF=0` 时仍保留按页提取文本和来源，原始 PDF 预览不可用。内嵌 PDF 的页码跳转取决于浏览器自带阅读器，必要时手动翻页。

## 相关文档

- [网页使用指南](usage-web.md)
- [运行参数](configuration.md)
