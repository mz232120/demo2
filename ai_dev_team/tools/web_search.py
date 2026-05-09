"""网络搜索工具。使用 DuckDuckGo 搜索引擎，无需 API Key。"""
from langchain_core.tools import tool


@tool
def web_search_tool(query: str) -> str:
    """通过 DuckDuckGo 搜索互联网获取信息。

    适用于搜索技术文档、API 用法、最佳实践等。
    返回前 3 条搜索结果的标题和摘要。

    Args:
        query: 搜索关键词

    Returns:
        搜索结果摘要
    """
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return f"[搜索无结果] 关键词: {query}"

        output_lines = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "")
            body = r.get("body", "")
            href = r.get("href", "")
            output_lines.append(f"{i}. {title}\n   {body}\n   链接: {href}")

        return "\n\n".join(output_lines)
    except ImportError:
        return "[搜索失败] 未安装 duckduckgo-search，请运行: pip install duckduckgo-search"
    except Exception as e:
        return f"[搜索失败] {type(e).__name__}: {e}"
