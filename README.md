# Simple Tavily Search MCP Server

这是一个用于 Smithery 的简化版 Tavily 搜索与网页抓取 MCP 服务器，旨在通过更小的 token/调用开销提供实时网络检索与页面抓取功能。

**主要用途**：当你在 Smithery 工作流中需要查询最新网页信息或抓取网页正文时，将此 MCP 作为工具集接入即可得到两个常用工具：`simple_search`（调用 Tavily 简化搜索）和 `fetch`（抓取并提取页面正文）。

**设计初衷**：Tavily 的官方工具对 token 的消耗偏高，本项目提供更轻量的封装以减少无关输出并提供可控的抓取逻辑。

**特性概览**
- **simple_search**: 使用 Tavily 执行简化网络搜索，返回格式化摘要（最多若干条结果）。
- **fetch**: 抓取指定 URL 的页面正文，去除脚本/样式并返回纯文本（带长度限制以防止超长返回）。

**Requirements / 依赖**
- **Python**: 3.8+
- 需要安装的包（示例）: `requests`, `beautifulsoup4`, `tavily`, `smithery`, `mcp`。

**安装（示例）**
1. 建议在虚拟环境中操作：

```bash
python -m venv .venv
source .venv/bin/activate
```

2. 安装依赖（根据你的项目依赖管理器选择安装方式）。示例使用 `pip`：

```bash
pip install requests beautifulsoup4 tavily smithery mcp
# 或者如果项目有 pyproject.toml/poetry，可以用 poetry 安装依赖
```

**环境变量**
- `TAVILY_API_KEY`: 必须设置该环境变量，`simple_search` 工具会从环境变量读取 API Key。

示例：

```bash
export TAVILY_API_KEY="your_tavily_api_key_here"
```

**快速验证（本地快速检查）**
你可以简单导入并创建服务器实例来做一次快速检查：

```bash
export TAVILY_API_KEY="your_tavily_api_key_here"
python -c "from my_tavily_server.server import create_server; s=create_server(); print('server name:', s.name)"
```

该命令会导入 `create_server` 并创建一个 `FastMCP` 实例（若缺少依赖将抛出 ImportError）。

**在 Smithery 中使用（示例）**
将此模块作为 MCP 服务器加载到你的 `smithery` 配置中（示例片段，视你的 smithery 配置格式调整）：

```yaml
# smithery.yaml（示例）
# 确保 smithery 能发现并加载 `my_tavily_server.server.create_server`
servers:
	- module: my_tavily_server.server
		create: create_server
```

然后使用 `smithery` 命令启动/加载你的服务（取决于你使用的 smithery CLI）：

```bash
# 示例命令（具体以您本地 smithery 使用方式为准）
smithery run
```

**工具说明与示例**
- `simple_search(query: str) -> str`:
	- 输入: 搜索关键词字符串。
	- 输出: 格式化的搜索结果摘要（Markdown 风格），或错误信息。
	- 注意: 会从 `TAVILY_API_KEY` 读取 API Key。

- `fetch(url: str) -> str`:
	- 输入: 以 `http://` 或 `https://` 开头的 URL。
	- 输出: 页面正文的纯文本（长度受限），或错误信息。

示例（伪代码）:

```py
# 由 Smithery 或客户端在运行时调用：
result = await server.tools['simple_search']('最新 的 AI 研究进展')
page_text = await server.tools['fetch']('https://example.com/article')
```

**开发与贡献**
- 欢迎通过 PR 提交改进：例如增加更好的正文抽取、缓存、或更细粒度的错误处理。

**许可证**
- MIT License

---

如果你希望我为这个项目生成 `requirements.txt`、示例 `smithery.yaml`（基于你实际的 smithery 版本）或添加运行脚本（如 `run_dev.py`），告诉我你的偏好，我可以继续创建这些文件并运行简单验证。

