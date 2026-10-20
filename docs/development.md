# 开发与测试

[← 返回 README](../README.md)

## 开发环境

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe examples/build_demo.py
.\.venv\Scripts\python.exe -m pytest -q --basetemp .test-tmp
```

测试覆盖来源完整分配、归纳叶子无遗漏、相反陈述去重、引文标记、JSON 修复、API 错误脱敏、PDF 错误处理、本地 HTTP 上传、移动布局与离线交互。

## 无密钥端到端联调

没有真实 API Key 时，可用 `scripts/mock_llm.py` 的确定性模拟接口走通「上传界面 → 分析 → 看板」的完整 GUI 流程：

```powershell
# 终端 1：启动模拟模型接口（响应来自 examples/fixture_model.py 的教学规则）
.\.venv\Scripts\python.exe scripts\mock_llm.py

# 终端 2：把 .env 的 LLM_BASE_URL 指向 http://127.0.0.1:8902/v1 后启动
.\.venv\Scripts\python.exe -m paperweave serve
```

`tests/test_upload_flow.py` 在 pytest 内自动执行同一流程：临时端口模拟接口 + 上传 PDF + 轮询任务至完成 + 打开看板并断言渲染。

## 运行记录

2026 年 10 月 20 日的运行记录：

| 范围 | 结果 | 原始记录 |
|---|---|---|
| 完整自动化测试 | 16 项通过 | [test-results.xml](../outputs/test-results.xml) |
| 最终浏览器/UI 复验 | 4 项通过，是已有测试的重复执行 | [ui-test-results.xml](../outputs/ui-test-results.xml) |
| 完整页面操作 | 本地模拟接口完成上传、分析、结果打开与四种下载 | [walkthrough-test.json](images/usage/walkthrough-test.json) |
| 离线重开 | 停止测试服务后重新打开下载的 HTML，搜索与证据定位可用，无外部 HTTP(S) 请求或页面脚本错误 | 同上 |

自动化测试和操作截图使用合成教学文档与确定性响应，用于验证软件行为，不证明真实模型的科学理解或分析准确率。

## 相关文档

- [示例与已知限制](limitations.md)
- [模型接口配置](configuration.md)
