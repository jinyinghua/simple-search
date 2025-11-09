# src/my_tavily_server/server.py
import os
import requests
from typing import Any, Dict
from bs4 import BeautifulSoup

from tavily import TavilyClient
from mcp.server.fastmcp import FastMCP
from smithery.decorators import smithery

# 这个函数将被 Smithery 调用，用于创建 FastMCP 服务器实例。
@smithery.server()
def create_server() -> FastMCP:
    """
    创建并返回一个 FastMCP 服务器实例，
    该实例包含简化的 Tavily 搜索和网页内容抓取工具。
    """
    server = FastMCP(name="search-and-fetch-tools")

    # --- 辅助函数 ---
    def get_tavily_client() -> TavilyClient:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("请设置 TAVILY_API_KEY 环境变量")
        return TavilyClient(api_key=api_key)

    def format_search_results(response: Dict[str, Any]) -> str:
        if not response or "results" not in response or not response["results"]:
            return "没有找到相关信息"
        formatted = "## 搜索结果\n\n"
        for i, result in enumerate(response["results"], 1):
            title = result.get("title", "无标题")
            url = result.get("url", "")
            content = result.get("content", "")
            summary = content[:200] + "..." if len(content) > 200 else content
            formatted += f"### {i}. {title}\n**链接**: {url}\n**摘要**: {summary}\n\n"
        return formatted

    # --- 工具定义 ---

    # 工具 1: simple_search (保持不变)
    @server.tool(
        description="搜索网络获取实时信息。当需要查询最新事件、事实信息或当前数据时使用此工具。",
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
                query=query, search_depth="basic", max_results=3,
                include_answer=False, include_raw_content=False
            )
            return format_search_results(response)
        except Exception as e:
            return f"搜索出错: {str(e)}"

    # 工具 2: fetch (新增)
    @server.tool(
        description="获取指定 URL 的网页文本内容。当搜索结果的摘要信息不足，需要阅读网页全文时使用此工具。",
    )
    async def fetch(url: str) -> str:
        """
        抓取并解析给定 URL 的主要文本内容。
        """
        if not url or not url.startswith(('http://', 'https://')):
            return "错误：请提供一个有效的 URL (以 http:// 或 https:// 开头)。"

        try:
            # 发送请求时设置 User-Agent 和超时
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # 如果请求失败 (如 404, 500)，则抛出异常

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 移除脚本和样式标签，减少噪音
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()

            # 获取 body 标签内的所有文本，用空格连接
            body = soup.find('body')
            if not body:
                return "错误：无法在该页面找到主要内容。"
            
            text_content = body.get_text(separator=' ', strip=True)

            # 限制返回内容的长度，避免过长
            max_length = 4000
            if len(text_content) > max_length:
                return text_content[:max_length] + "... (内容已截断)"
            
            return text_content

        except requests.exceptions.RequestException as e:
            return f"抓取 URL 时出错: {str(e)}"
        except Exception as e:
            return f"处理页面内容时发生未知错误: {str(e)}"

    return server
