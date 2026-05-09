"""测试工程师 Agent。分析代码，编写并执行测试用例。"""
import re
from typing import Any

from agents.base import BaseAgent
from tools.code_executor import code_executor_tool
from tools.file_manager import file_write_tool


class TesterAgent(BaseAgent):
    """测试工程师 Agent。

    职责：分析代码，编写 pytest 测试用例，执行测试并输出报告。
    可用工具：code_executor, file_write。
    """

    def __init__(self):
        self.role = "tester"
        self.prompt_file = "tester.txt"
        self.tools = [code_executor_tool, file_write_tool]
        super().__init__()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """分析代码并生成测试报告。

        Args:
            input_data: 包含 "code_files" 键的代码文件字典

        Returns:
            包含测试文件和测试结果的字典
        """
        # 调用 LLM 生成测试
        result = super().run(input_data)

        # 如果 LLM 输出了 test_files，保存并执行测试
        if "test_files" in result and isinstance(result["test_files"], dict):
            result = self._run_tests(result)

        return result

    def _extract_from_text(self, text: str) -> dict[str, Any] | None:
        """从自然语言输出中提取测试代码块。"""
        # 提取所有带文件名的代码块
        named_blocks = re.findall(
            r"```python\s*\n#\s*(test_\S+\.py)\s*\n(.*?)\n```",
            text, re.DOTALL
        )
        if named_blocks:
            test_files = {name: code.strip() for name, code in named_blocks}
            return {"test_files": test_files, "coverage_summary": "从 LLM 输出中提取的测试代码"}

        # 提取所有 ```python ... ``` 代码块
        code_blocks = re.findall(r"```python\s*\n(.*?)\n```", text, re.DOTALL)
        if code_blocks:
            test_files = {}
            for i, code in enumerate(code_blocks):
                name = "test_main.py" if i == 0 else f"test_module_{i}.py"
                test_files[name] = code.strip()
            return {"test_files": test_files, "coverage_summary": "从 LLM 输出中提取的测试代码"}

        return None

    def _run_tests(self, result: dict) -> dict:
        """保存测试文件并执行测试。"""
        test_files = result["test_files"]

        # 保存测试文件
        for filename, content in test_files.items():
            file_write_tool.invoke({"path": filename, "content": content})

        # 执行 pytest
        test_names = ", ".join(f"'{name}'" for name in test_files.keys())
        test_code = (
            "import subprocess, sys\n"
            f"result = subprocess.run(\n"
            f"    [sys.executable, '-m', 'pytest', {test_names}, '-v', '--tb=short'],\n"
            f"    capture_output=True, text=True\n"
            f")\n"
            f"print(result.stdout)\n"
            f"if result.stderr:\n"
            f"    print('STDERR:', result.stderr)\n"
            f"print(f'返回码: {{result.returncode}}')\n"
        )
        test_result = code_executor_tool.invoke(test_code)
        result["test_results"] = test_result

        return result
