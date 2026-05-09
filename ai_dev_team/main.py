"""Gradio Web 界面入口。实时展示 Multi-Agent 协作过程。"""
import json
import gradio as gr

from orchestrator import Orchestrator

CUSTOM_CSS = """
.markdown-body {max-height: 400px; overflow-y: auto;}
.markdown-body pre {max-height: 250px; overflow-y: auto;}
"""


def _truncate_code(content: str, max_lines: int = 30) -> str:
    """截断过长的代码，保留前 N 行。"""
    lines = content.split("\n")
    if len(lines) <= max_lines:
        return content
    return "\n".join(lines[:max_lines]) + f"\n... (共 {len(lines)} 行，已截断)"


def _format_dev_result(dev_result: dict) -> str:
    """格式化开发工程师的输出。"""
    if "files" in dev_result and dev_result["files"]:
        lines = []
        for filename, content in dev_result["files"].items():
            lines.append(f"**{filename}:**\n```python\n{_truncate_code(content)}\n```")
        exec_result = dev_result.get("execution_result", "")
        if exec_result:
            lines.append(f"**执行结果：**\n```\n{exec_result[:500]}\n```")
        return "\n".join(lines)
    raw = dev_result.get("raw_output", "无输出")
    return raw[:1500]


def _format_tester_result(tester_result: dict) -> str:
    """格式化测试工程师的输出。"""
    if "test_files" in tester_result and tester_result["test_files"]:
        lines = []
        for filename, content in tester_result["test_files"].items():
            lines.append(f"**{filename}:**\n```python\n{_truncate_code(content)}\n```")
        test_results = tester_result.get("test_results", "")
        if test_results:
            lines.append(f"**测试结果：**\n```\n{test_results[:500]}\n```")
        coverage = tester_result.get("coverage_summary", "")
        if coverage:
            lines.append(f"\n**覆盖概述：** {coverage}")
        return "\n".join(lines)
    raw = tester_result.get("raw_output", "无输出")
    return raw[:1500]


def create_app() -> gr.Blocks:
    """创建 Gradio 应用。"""
    orch = Orchestrator()

    def run_team(requirement: str):
        """执行 Agent 协作流程，流式返回每一步的结果。"""
        if not requirement.strip():
            yield "", "", "", "请输入需求"
            return

        pm_text, dev_text, tester_text, status = "", "", "", ""

        # 产品经理
        status = "产品经理正在分析需求..."
        yield pm_text, dev_text, tester_text, status

        pm_result = orch.pm.run({"requirement": requirement})
        pm_text = json.dumps(pm_result, ensure_ascii=False, indent=2)
        status = "产品经理完成，开发工程师开始编写代码..."
        yield pm_text, dev_text, tester_text, status

        # 开发工程师
        dev_result = orch.dev.run({"requirements": pm_result})
        dev_text = _format_dev_result(dev_result)
        status = "开发工程师完成，测试工程师开始编写测试..."
        yield pm_text, dev_text, tester_text, status

        # 测试工程师
        tester_result = orch.tester.run({
            "code_files": dev_result.get("files", {}),
            "requirements": pm_result,
        })
        tester_text = _format_tester_result(tester_result)
        status = "所有 Agent 工作完成！"
        yield pm_text, dev_text, tester_text, status

    # 构建界面
    with gr.Blocks(title="AI 研发团队", css=CUSTOM_CSS) as app:
        gr.Markdown("# AI 研发团队协作系统")

        with gr.Row():
            requirement_input = gr.Textbox(
                label="需求描述",
                placeholder="例如：用 Python 实现一个计算器，支持加减乘除运算",
                lines=2,
                scale=4,
            )
            run_btn = gr.Button("开始协作", variant="primary", scale=1)

        with gr.Accordion("产品经理", open=False):
            pm_output = gr.Code(language="json", label="", interactive=False)
        with gr.Accordion("开发工程师", open=True):
            dev_output = gr.Markdown(value="等待输入...")
        with gr.Accordion("测试工程师", open=False):
            tester_output = gr.Markdown(value="等待输入...")

        status_output = gr.Markdown(value="等待输入...")

        run_btn.click(
            fn=run_team,
            inputs=[requirement_input],
            outputs=[pm_output, dev_output, tester_output, status_output],
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
