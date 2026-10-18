# 示例说明

`teaching-paper.pdf` 是本项目编写的四页合成教学文档，包含末页限制条件，不是已发表论文。

`build_demo.py` 使用明确标记的确定性测试响应生成演示看板；没有调用真实大模型，不代表分析质量已通过验收。

安装项目后运行 `python examples/build_demo.py`。正常分析任意评委提供的文本型论文请使用 `python -m paperweave analyze 论文.pdf -o outputs/论文名`，此路径始终调用所配置的真实模型 API，不会自动降级到示例。
