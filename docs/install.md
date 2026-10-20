# 安装指南

[← 返回 README](../README.md)

当前在 Windows、Python 3.12、Microsoft Edge 上运行并测试。项目声明支持 Python 3.10 及以上，建议使用已经测试的 Python 3.12；其他系统尚未在本机验证。

## 准备项目目录

先解压或克隆项目，进入同时包含 `README.md`、`pyproject.toml`、`requirements.txt` 和 `src/` 的根目录。在资源管理器地址栏输入 `powershell` 并按 Enter，即可在这个目录打开终端。

## 确认 Python

```powershell
py -3.12 --version
```

输出应为 `Python 3.12.x`。如果尚未安装，可按 [Python 官方 Windows 安装说明](https://docs.python.org/3.12/using/windows.html) 准备 Python 3.12。若系统使用 `python3.12` 而非 `py`，可把下面创建环境的第一行替换为 `python3.12 -m venv .venv`。

## 创建虚拟环境并安装依赖

在项目根目录逐行执行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e . --no-deps
```

## 准备浏览器内核

程序通过 Playwright 调用 Chromium 内核校验、渲染 Mermaid，会依次尝试本机 Edge、Chrome 和已安装的 Playwright Chromium。找不到可用浏览器时执行：

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

## 前端依赖（通常不需要）

正常运行不需要 Node。仓库已包含构建好的 `src/paperweave/static/mermaid.bundle.js`；只有修改浏览器依赖后才需要使用 Node 20+ 重新构建：

```powershell
npm ci
npm run build
```

## 下一步

- [配置模型接口](configuration.md)
- [通过网页使用](usage-web.md)
- [通过命令行使用](usage-cli.md)
