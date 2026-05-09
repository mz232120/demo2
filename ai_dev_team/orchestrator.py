"""调度器。管理三个 Agent 的协作流程，串联产品→开发→测试。"""
import json
from typing import Callable

from agents.product_manager import ProductManagerAgent
from agents.developer import DeveloperAgent
from agents.tester import TesterAgent
from config import WORKSPACE_DIR


class Orchestrator:
    """Multi-Agent 调度器。

    按顺序调用：产品经理 → 开发工程师 → 测试工程师。
    每个 Agent 的输出自动格式化为下一个 Agent 的输入。
    支持回调函数实时推送中间结果到前端。
    """

    def __init__(self):
        self.pm = ProductManagerAgent()
        self.dev = DeveloperAgent()
        self.tester = TesterAgent()

    def run(self, user_requirement: str, callback: Callable[[str, str], None] | None = None) -> dict:
        """执行完整的研发协作流程。

        Args:
            user_requirement: 用户的自然语言需求
            callback: 回调函数 callback(step_name, content) 用于实时推送进度

        Returns:
            包含所有步骤结果的汇总字典
        """
        results = {"requirement": user_requirement}

        def _notify(step: str, content: str):
            if callback:
                callback(step, content)

        # === 第一步：产品经理分析需求 ===
        _notify("产品经理", "正在分析需求...")
        pm_input = {"requirement": user_requirement}
        pm_result = self.pm.run(pm_input)
        results["product_manager"] = pm_result
        _notify("产品经理", json.dumps(pm_result, ensure_ascii=False, indent=2))

        # === 第二步：开发工程师实现代码 ===
        _notify("开发工程师", "正在编写代码...")
        dev_input = {"requirements": pm_result}
        dev_result = self.dev.run(dev_input)
        results["developer"] = dev_result
        _notify("开发工程师", json.dumps(dev_result, ensure_ascii=False, indent=2))

        # === 第三步：测试工程师验证代码 ===
        _notify("测试工程师", "正在编写测试...")
        tester_input = {
            "code_files": dev_result.get("files", {}),
            "requirements": pm_result,
        }
        tester_result = self.tester.run(tester_input)
        results["tester"] = tester_result
        _notify("测试工程师", json.dumps(tester_result, ensure_ascii=False, indent=2))

        # === 汇总 ===
        _notify("完成", "所有 Agent 工作完成！")
        results["status"] = "completed"
        return results

    def cleanup_workspace(self):
        """清理 workspace 目录。"""
        import shutil
        if WORKSPACE_DIR.exists():
            shutil.rmtree(WORKSPACE_DIR)
            WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
