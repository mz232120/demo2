"""Agent 基类。封装 LangChain 的 LLM 调用和输出解析逻辑。"""
import json
import re
from abc import ABC
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TEMPERATURE, PROMPTS_DIR


class BaseAgent(ABC):
    """所有 Agent 的基类。

    封装了 LLM 初始化、Prompt 加载、调用和输出解析。
    子类只需设置 role、prompt_file、tools 属性即可。
    """

    def __init__(self):
        if not hasattr(self, "role"):
            self.role: str = ""
        if not hasattr(self, "prompt_file"):
            self.prompt_file: str = ""
        if not hasattr(self, "tools"):
            self.tools: list = []
        self._llm = self._create_llm()
        self._system_prompt = self._load_prompt()
        self._chain = self._build_chain()

    def _create_llm(self) -> ChatOpenAI:
        """创建 LLM 实例。使用 DeepSeek API（OpenAI 兼容接口）。"""
        return ChatOpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            model=DEEPSEEK_MODEL,
            temperature=TEMPERATURE,
        )

    def _load_prompt(self) -> str:
        """从文件加载 System Prompt。"""
        prompt_path = PROMPTS_DIR / self.prompt_file
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt 文件不存在: {prompt_path}")
        return prompt_path.read_text(encoding="utf-8")

    def _build_chain(self):
        """构建 LangChain 调用链: Prompt → LLM → 输出解析。"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._system_prompt),
            ("human", "{input}"),
        ])
        return prompt | self._llm | StrOutputParser()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """执行 Agent 任务。

        Args:
            input_data: 输入数据字典

        Returns:
            结构化输出字典
        """
        input_text = self._format_input(input_data)
        raw_output = self._chain.invoke({"input": input_text})

        # 尝试解析 JSON 输出
        parsed = self._parse_json_output(raw_output)
        if parsed is not None:
            return parsed

        # JSON 解析失败，尝试从自然语言中提取代码块
        fallback = self._extract_from_text(raw_output)
        if fallback:
            return fallback

        return {"raw_output": raw_output, "parse_error": "无法解析输出"}

    def _format_input(self, input_data: dict[str, Any]) -> str:
        """将输入字典格式化为文本。子类可以重写以自定义格式。"""
        lines = []
        for key, value in input_data.items():
            if key.startswith("_"):
                continue
            if isinstance(value, (dict, list)):
                lines.append(f"## {key}\n```json\n{json.dumps(value, ensure_ascii=False, indent=2)}\n```")
            else:
                lines.append(f"## {key}\n{value}")
        return "\n\n".join(lines)

    def _parse_json_output(self, text: str) -> dict[str, Any] | None:
        """从 LLM 输出中提取 JSON。支持 ```json ``` 代码块和裸 JSON。"""
        # 尝试从 ```json ... ``` 代码块中提取
        code_block = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if code_block:
            try:
                return json.loads(code_block.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 尝试直接解析整个文本
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass

        # 尝试找到第一个 { ... } 块（贪婪匹配）
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def _extract_from_text(self, text: str) -> dict[str, Any] | None:
        """从自然语言输出中提取代码块，子类可以重写。"""
        # 提取所有 ```python ... ``` 代码块
        code_blocks = re.findall(r"```python\s*\n(.*?)\n```", text, re.DOTALL)
        if code_blocks:
            return {"raw_output": text, "code_blocks": code_blocks}
        return None
