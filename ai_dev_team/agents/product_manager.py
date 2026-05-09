"""产品经理 Agent。分析用户需求，输出结构化需求文档。"""
from agents.base import BaseAgent
from tools.web_search import web_search_tool


class ProductManagerAgent(BaseAgent):
    """产品经理 Agent。

    职责：将用户的自然语言需求转化为结构化的需求文档。
    可用工具：web_search（搜索技术方案）。
    """

    def __init__(self):
        self.role = "product_manager"
        self.prompt_file = "product_manager.txt"
        self.tools = [web_search_tool]
        super().__init__()
