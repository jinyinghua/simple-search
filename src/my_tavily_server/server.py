# src/my_tavily_server/server.py
import os
from typing import Any, Dict

from tavily import TavilyClient
from mcp.server.fastmcp import FastMCP # 导入 FastMCP
from smithery.decorators import smithery # 导入 smithery 装饰器

# 这个函数将被 Smithery 调用，用于创建 FastMCP 服务器实例。
# 它必须用 @smithery.server() 装饰。
@smithery.server()
def create_server() -> FastMCP:
    """
    创建并返回一个用于简化 Tavily 搜索的 FastMCP 服务器实例。
    """
    server = FastMCP(name="simple-tavily-search")

    # 辅助函数：获取 Tavily 客户端
    def get_tavily_client() -> TavilyClient:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("请设置 TAVILY_API_KEY 环境变量")
        return TavilyClient(api_key=api_key)

    # 定义简化的搜索工具。
    # FastMCP 会自动从函数签名推断 inputSchema。
    @server.tool(
        description="搜索网络获取实时信息。当需要查询最新事件、事实信息或当前数据时使用此工具。",
        # 'query' 参数的描述将从函数参数的类型提示和名称自动生成，
        # 或者由 Smithery 从 pyproject.toml 中的工具定义（如果存在）获取。
    )
    async def simple_search(query: str) -> str:
        """
        使用 Tavily 执行简化的网络搜索。
        """
        if not query.strip():
            return "请提供搜索关键词"

        try:
            client = get_tavily_client()
            response = client.search(
                query=query,
                search_depth="basic",  # 使用基础搜索
                max_results=3,         # 限制结果数量
                include_answer=False,  # 不包含 AI 答案
                include_raw_content=False # 不包含原始内容
            )
            formatted_results = format_search_results(response)
            return formatted_results
        except Exception as e:
            # 对于 FastMCP 工具，直接返回错误字符串作为工具输出
            return f"搜索出错: {str(e)}"

    def format_search_results(response: Dict[str, Any]) -> str:
        """格式化搜索结果，提取关键信息"""
        if not response or "results" not in response:
            return "没有找到相关信息"

        results = response["results"]
        if not results:
            return "没有找到相关信息"

        formatted = "## 搜索结果\n\n"

        for i, result in enumerate(results, 1):
            title = result.get("title", "无标题")
            url = result.get("url", "")
            content = result.get("content", "")

            formatted += f"### {i}. {title}\n"
            if url:
                formatted += f"**链接**: {url}\n"
            if content:
                # 截取前200个字符作为摘要
                summary = content[:200] + "..." if len(content) > 200 else content
                formatted += f"**摘要**: {summary}\n"
            formatted += "\n"

        return formatted

    return server
