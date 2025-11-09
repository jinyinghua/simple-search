#!/usr/bin/env python3
"""
简化版 Tavily MCP 工具
只暴露 query 参数，内部使用优化的默认值
"""
import asyncio
import json
import os
from typing import Any, Dict, Optional

from tavily import TavilyClient
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# 初始化服务器
server = Server("simple-tavily-search")

# 初始化 Tavily 客户端
def get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("请设置 TAVILY_API_KEY 环境变量")
    return TavilyClient(api_key=api_key)

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """返回简化的工具定义"""
    return [
        types.Tool(
            name="simple_search",
            description="搜索网络获取实时信息。当需要查询最新事件、事实信息或当前数据时使用此工具。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，建议简洁明了"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """处理工具调用"""
    if name != "simple_search":
        return [types.TextContent(
            type="text",
            text=f"未知工具: {name}"
        )]

    query = arguments.get("query", "").strip()
    if not query:
        return [types.TextContent(
            type="text", 
            text="请提供搜索关键词"
        )]

    try:
        client = get_tavily_client()
        
        # 使用预设的优化参数调用Tavily API
        response = client.search(
            query=query,
            search_depth="basic",  # 使用基础搜索
            max_results=3,         # 限制结果数量
            include_answer=False,  # 不包含AI答案
            include_raw_content=False  # 不包含原始内容
        )
        
        # 格式化返回结果
        formatted_results = format_search_results(response)
        
        return [types.TextContent(
            type="text",
            text=formatted_results
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"搜索出错: {str(e)}"
        )]

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
        score = result.get("score", 0)
        
        formatted += f"### {i}. {title}\n"
        if url:
            formatted += f"**链接**: {url}\n"
        if score:
            formatted += f"**相关性**: {score:.2f}\n"
        if content:
            # 截取前200个字符作为摘要
            summary = content[:200] + "..." if len(content) > 200 else content
            formatted += f"**摘要**: {summary}\n"
        formatted += "\n"
    
    return formatted

async def main():
    """主函数"""
    # 使用stdio传输
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="simple-tavily-search",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
