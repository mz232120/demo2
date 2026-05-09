"""开发工程师 Agent。根据需求文档编写代码并验证。"""
import json
import re
from typing import Any

from agents.base import BaseAgent
from tools.code_executor import code_executor_tool
from tools.file_manager import file_write_tool, file_read_tool
from config import MAX_RETRY


class DeveloperAgent(BaseAgent):
    """开发工程师 Agent。

    职责：根据需求文档编写代码，保存文件并执行验证。
    支持代码执行失败自动重试修复（最多 MAX_RETRY 次）。
    可用工具：code_executor, file_write, file_read。
    """

    def __init__(self):
        self.role = "developer"
        self.prompt_file = "developer.txt"
        self.tools = [code_executor_tool, file_write_tool, file_read_tool]
        super().__init__()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """根据需求文档实现代码。

        Args:
            input_data: 包含 "requirements" 键的需求文档

        Returns:
            包含代码文件和执行结果的字典
        """
        # 调用 LLM 生成代码
        result = super().run(input_data)

        # 如果 LLM 输出了 files，尝试执行验证并自动修复
        if "files" in result and isinstance(result["files"], dict):
            result = self._verify_and_fix(result, input_data)

        return result

    def _extract_from_text(self, text: str) -> dict[str, Any] | None:
        """从自然语言输出中提取代码块，构造成 files 格式。"""
        # 提取所有带文件名的代码块: ```python\n# filename.py\n...
        named_blocks = re.findall(
            r"```python\s*\n#\s*(\S+\.py)\s*\n(.*?)\n```",
            text, re.DOTALL
        )
        if named_blocks:
            files = {name: code.strip() for name, code in named_blocks}
            return {"files": files, "summary": "从 LLM 输出中提取的代码"}

        # 提取所有 ```python ... ``` 代码块，命名为 main.py, utils.py 等
        code_blocks = re.findall(r"```python\s*\n(.*?)\n```", text, re.DOTALL)
        if code_blocks:
            files = {}
            for i, code in enumerate(code_blocks):
                name = "main.py" if i == 0 else f"module_{i}.py"
                files[name] = code.strip()
            return {"files": files, "summary": "从 LLM 输出中提取的代码"}

        return None

    def _verify_and_fix(self, result: dict, original_input: dict) -> dict:
        """验证代码执行结果，失败则自动修复。"""
        files = result["files"]

        for attempt in range(MAX_RETRY):
            # 保存所有代码文件
            for filename, content in files.items():
                file_write_tool.invoke({"path": filename, "content": content})

            # 找到主文件执行验证
            main_file = self._find_main_file(files)
            if main_file:
                exec_result = code_executor_tool.invoke(main_file["content"])
                result["execution_result"] = exec_result

                # 执行成功，直接返回
                if not exec_result.startswith("[执行失败]") and not exec_result.startswith("[执行异常]"):
                    return result

                # 执行失败，让 LLM 修复
                fix_input = {
                    **original_input,
                    "error_info": exec_result,
                    "current_code": json.dumps(files, ensure_ascii=False, indent=2),
                    "attempt": attempt + 1,
                    "instruction": f"上面的代码执行出错了（第 {attempt + 1} 次尝试），请分析错误原因并修复代码。"
                                   f"返回修复后的完整代码 JSON，格式与之前相同。",
                }
                result = super().run(fix_input)

                if "files" not in result or not isinstance(result["files"], dict):
                    result["execution_result"] = exec_result
                    result["auto_fix_failed"] = True
                    return result

                files = result["files"]
            else:
                result["execution_result"] = "[跳过验证] 未找到可执行的主文件"
                return result

        result["max_retry_reached"] = True
        return result

    def _find_main_file(self, files: dict) -> dict | None:
        """找到应该执行的主文件。优先 main.py，其次第一个 .py 文件。"""
        if "main.py" in files:
            return {"path": "main.py", "content": files["main.py"]}
        for name, content in files.items():
            if name.endswith(".py"):
                return {"path": name, "content": content}
        return None
