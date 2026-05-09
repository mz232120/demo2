"""文件管理工具。在 workspace 目录下进行文件读写操作。"""
from pathlib import Path
from langchain_core.tools import tool

from config import WORKSPACE_DIR


def _safe_path(path: str) -> Path:
    """将相对路径解析为 workspace 下的安全绝对路径，防止目录穿越。"""
    target = (WORKSPACE_DIR / path).resolve()
    workspace_resolved = WORKSPACE_DIR.resolve()
    if not str(target).startswith(str(workspace_resolved)):
        raise ValueError(f"路径越权: {path} (只能访问 workspace/ 目录)")
    return target


@tool
def file_write_tool(path: str, content: str) -> str:
    """将内容写入文件。

    文件会创建在 workspace 目录下。如果父目录不存在会自动创建。

    Args:
        path: 相对文件路径，例如 "main.py" 或 "src/utils.py"
        content: 要写入的文件内容

    Returns:
        写入结果的描述
    """
    try:
        target = _safe_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"[写入成功] {path} ({len(content)} 字符)"
    except ValueError as e:
        return f"[写入失败] {e}"
    except Exception as e:
        return f"[写入失败] {type(e).__name__}: {e}"


@tool
def file_read_tool(path: str) -> str:
    """读取文件内容。

    Args:
        path: 相对文件路径，例如 "main.py"

    Returns:
        文件内容，或错误信息
    """
    try:
        target = _safe_path(path)
        if not target.exists():
            return f"[读取失败] 文件不存在: {path}"
        content = target.read_text(encoding="utf-8")
        return content
    except ValueError as e:
        return f"[读取失败] {e}"
    except Exception as e:
        return f"[读取失败] {type(e).__name__}: {e}"


@tool
def file_list_tool(directory: str = ".") -> str:
    """列出目录下的文件。

    Args:
        directory: 相对目录路径，默认为 workspace 根目录

    Returns:
        文件列表，每个文件一行
    """
    try:
        target = _safe_path(directory)
        if not target.exists():
            return f"[列出失败] 目录不存在: {directory}"
        if not target.is_dir():
            return f"[列出失败] 不是目录: {directory}"
        items = []
        for item in sorted(target.iterdir()):
            prefix = "[DIR] " if item.is_dir() else "[FILE]"
            items.append(f"{prefix} {item.name}")
        return "\n".join(items) if items else "[空目录]"
    except ValueError as e:
        return f"[列出失败] {e}"
    except Exception as e:
        return f"[列出失败] {type(e).__name__}: {e}"
