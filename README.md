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

**使用方法**
- 1.为本项目点上 Star
- 2.访问该项目在[Smithery](https://smithery.ai/server/@jinyinghua/simple-search)上部署的 MCP Server
- 3.参考页面的 connect 部分链接到 AI 客户端

**开发与贡献**
- 欢迎通过 PR 提交改进：例如增加更好的正文抽取、缓存、或更细粒度的错误处理。

**许可证**
- MIT License

---

如果你希望我为这个项目生成 `requirements.txt`、示例 `smithery.yaml`（基于你实际的 smithery 版本）或添加运行脚本（如 `run_dev.py`），告诉我你的偏好，我可以继续创建这些文件并运行简单验证。

