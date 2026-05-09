"""代码执行工具。在 workspace 目录下安全执行 Python 代码。"""
import subprocess
import sys
from pathlib import Path
from langchain_core.tools import tool

from config import WORKSPACE_DIR, CODE_EXEC_TIMEOUT, BANNED_IMPORTS


def _check_banned_imports(code: str) -> list[str]:
    """检查代码中是否包含被禁止的导入语句。"""
    found = []
    for banned in BANNED_IMPORTS:
        if banned in code:
            found.append(banned)
    return found


@tool
def code_executor_tool(code: str) -> str:
    """执行 Python 代码并返回输出结果。

    代码会在 workspace 目录下以子进程方式运行，有超时保护。
    如果代码中有语法错误或运行时错误，会返回错误信息。

    Args:
        code: 要执行的 Python 代码字符串

    Returns:
        代码的 stdout 输出，或错误信息
    """
    # 安全检查
    banned = _check_banned_imports(code)
    if banned:
        return f"[安全拦截] 代码包含被禁止的操作: {', '.join(banned)}"

    # 确保 workspace 目录存在
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    # 写入临时文件
    tmp_file = WORKSPACE_DIR / "_tmp_exec.py"
    tmp_file.write_text(code, encoding="utf-8")

    try:
        result = subprocess.run(
            [sys.executable, str(tmp_file)],
            capture_output=True,
            text=True,
            timeout=CODE_EXEC_TIMEOUT,
            cwd=str(WORKSPACE_DIR),
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            return output if output else "[执行成功，无输出]"
        else:
            return f"[执行失败] 返回码: {result.returncode}\n错误信息:\n{result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return f"[执行超时] 代码运行超过 {CODE_EXEC_TIMEOUT} 秒"
    except Exception as e:
        return f"[执行异常] {type(e).__name__}: {e}"
    finally:
        # 清理临时文件
        if tmp_file.exists():
            tmp_file.unlink()
