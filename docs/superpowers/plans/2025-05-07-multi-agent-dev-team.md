# Multi-Agent AI 研发团队协作系统 - 实现计划

> **For agentic workers:** Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于 LangChain 构建 Multi-Agent 协作系统，模拟产品经理→开发→测试的研发团队，支持工具调用和 Gradio Web 界面。

**Architecture:** 三个独立 Agent（产品/开发/测试）通过 Orchestrator 调度器串联协作，Agent 间传递结构化字典数据。每个 Agent 基于 LangChain 的 ChatPromptTemplate + output parsing 实现。工具模块（代码执行、文件读写、搜索）供 Agent 调用。Gradio 前端实时展示协作过程。

**Tech Stack:** Python 3.10+, LangChain, DeepSeek-V4 (OpenAI compatible), Gradio

---

## File Structure

```
ai_dev_team/
├── main.py                  # Gradio 入口
├── orchestrator.py          # 调度器
├── config.py                # 配置
├── requirements.txt         # 依赖
├── .env                     # 环境变量（API Key）
├── agents/
│   ├── __init__.py
│   ├── base.py              # Agent 基类
│   ├── product_manager.py   # 产品经理
│   ├── developer.py         # 开发工程师
│   └── tester.py            # 测试工程师
├── tools/
│   ├── __init__.py
│   ├── code_executor.py     # 代码执行
│   ├── file_manager.py      # 文件读写
│   └── web_search.py        # 搜索
├── prompts/
│   ├── product_manager.txt
│   ├── developer.txt
│   └── tester.txt
└── workspace/               # Agent 工作目录（运行时生成）
```

---

### Task 1: 项目骨架搭建

**Files:**
- Create: `ai_dev_team/requirements.txt`
- Create: `ai_dev_team/config.py`
- Create: `ai_dev_team/.env`
- Create: `ai_dev_team/agents/__init__.py`
- Create: `ai_dev_team/tools/__init__.py`

- [ ] **Step 1: 创建目录结构**

```bash
mkdir -p ai_dev_team/agents ai_dev_team/tools ai_dev_team/prompts ai_dev_team/workspace
```

- [ ] **Step 2: 写 requirements.txt**

```txt
langchain>=0.3.0
langchain-openai>=0.3.0
langchain-community>=0.3.0
gradio>=5.0.0
python-dotenv>=1.0.0
duckduckgo-search>=7.0.0
```

- [ ] **Step 3: 写 config.py**

```python
"""项目配置模块。统一管理 API Key、模型参数、路径等配置。"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv(Path(__file__).parent / ".env")

# DeepSeek API 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Agent 配置
MAX_RETRY = 3  # 开发 Agent 代码执行失败最大重试次数
TEMPERATURE = 0.7  # LLM 温度，越高越有创意，越低越稳定

# 路径配置
PROJECT_ROOT = Path(__file__).parent
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

# 代码执行配置
CODE_EXEC_TIMEOUT = 30  # 代码执行超时（秒）
BANNED_IMPORTS = ["os.system", "subprocess.call", "subprocess.run", "shutil.rmtree"]
```

- [ ] **Step 4: 写 .env 文件**

```env
# 在这里填入你的 DeepSeek API Key
# 获取地址: https://platform.deepseek.com/api_keys
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

- [ ] **Step 5: 写空的 __init__.py**

`ai_dev_team/agents/__init__.py`:
```python
from agents.product_manager import ProductManagerAgent
from agents.developer import DeveloperAgent
from agents.tester import TesterAgent

__all__ = ["ProductManagerAgent", "DeveloperAgent", "TesterAgent"]
```

`ai_dev_team/tools/__init__.py`:
```python
from tools.code_executor import code_executor_tool
from tools.file_manager import file_write_tool, file_read_tool, file_list_tool
from tools.web_search import web_search_tool

__all__ = [
    "code_executor_tool",
    "file_write_tool", "file_read_tool", "file_list_tool",
    "web_search_tool",
]
```

- [ ] **Step 6: 初始化 git 仓库并提交**

```bash
cd ai_dev_team
git init
git add requirements.txt config.py .env agents/__init__.py tools/__init__.py
git commit -m "chore: init project skeleton"
```

---

### Task 2: 工具 - 代码执行器

**Files:**
- Create: `ai_dev_team/tools/code_executor.py`

- [ ] **Step 1: 写代码执行工具**

```python
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
```

- [ ] **Step 2: 验证工具能正常工作**

在 `ai_dev_team/` 目录下运行：

```bash
cd ai_dev_team
python -c "
from tools.code_executor import code_executor_tool
print(code_executor_tool.invoke('print(\"hello world\")'))
print('---')
print(code_executor_tool.invoke('1/0'))
print('---')
print(code_executor_tool.invoke('import os; os.system(\"ls\")'))
"
```

预期输出：
```
hello world
---
[执行失败] 返回码: 1
错误信息:
Traceback (most recent call last):
  File "...", line 1, in <module>
    1/0
ZeroDivisionError: division by zero
---
[安全拦截] 代码包含被禁止的操作: os.system
```

- [ ] **Step 3: 提交**

```bash
git add tools/code_executor.py
git commit -m "feat: add code executor tool with sandbox and timeout"
```

---

### Task 3: 工具 - 文件管理器

**Files:**
- Create: `ai_dev_team/tools/file_manager.py`

- [ ] **Step 1: 写文件管理工具**

```python
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
```

- [ ] **Step 2: 验证工具能正常工作**

```bash
cd ai_dev_team
python -c "
from tools.file_manager import file_write_tool, file_read_tool, file_list_tool
print(file_write_tool.invoke({'path': 'test/hello.py', 'content': 'print(123)'}))
print('---')
print(file_read_tool.invoke({'path': 'test/hello.py'}))
print('---')
print(file_list_tool.invoke({'directory': 'test'}))
print('---')
print(file_read_tool.invoke({'path': 'not_exist.py'}))
print('---')
print(file_write_tool.invoke({'path': '../../etc/passwd', 'content': 'hack'}))
"
```

预期：写入成功 → 读取内容 → 列出文件 → 不存在报错 → 路径越权被拦截

- [ ] **Step 3: 提交**

```bash
git add tools/file_manager.py
git commit -m "feat: add file manager tool with path sandbox"
```

---

### Task 4: 工具 - 网络搜索

**Files:**
- Create: `ai_dev_team/tools/web_search.py`

- [ ] **Step 1: 写搜索工具**

```python
"""网络搜索工具。使用 DuckDuckGo 搜索引擎，无需 API Key。"""
from langchain_core.tools import tool

from config import WORKSPACE_DIR


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
```

- [ ] **Step 2: 验证工具能正常工作**

```bash
cd ai_dev_team
python -c "
from tools.web_search import web_search_tool
print(web_search_tool.invoke('Python FastAPI hello world'))
"
```

预期：输出 3 条搜索结果，包含标题、摘要和链接

- [ ] **Step 3: 提交**

```bash
git add tools/web_search.py
git commit -m "feat: add web search tool using DuckDuckGo"
```

---

### Task 5: Agent 提示词

**Files:**
- Create: `ai_dev_team/prompts/product_manager.txt`
- Create: `ai_dev_team/prompts/developer.txt`
- Create: `ai_dev_team/prompts/tester.txt`

- [ ] **Step 1: 写产品经理提示词**

```
ai_dev_team/prompts/product_manager.txt
```

内容：
```
你是一位资深产品经理，擅长将用户的自然语言需求转化为结构化的软件需求文档。

## 你的职责
1. 分析用户提出的需求，理解核心目标
2. 将需求拆解为具体的功能点
3. 确定技术选型建议
4. 设计接口/API 结构
5. 定义验收标准

## 输出格式
你必须严格按照以下 JSON 格式输出需求文档，不要输出任何其他内容：

```json
{
    "project_name": "项目名称（简短有力）",
    "description": "项目描述（2-3句话说明做什么、解决什么问题）",
    "features": [
        "功能点1：具体描述",
        "功能点2：具体描述",
        "功能点3：具体描述"
    ],
    "tech_stack": ["技术1", "技术2"],
    "api_design": "接口设计描述（包括输入输出）",
    "acceptance_criteria": "验收标准（怎样算完成）"
}
```

## 注意事项
- 功能点要具体可实现，不要空泛
- 技术选型要合理，考虑开发难度
- 如果需求不清晰，基于合理假设补充细节
- 保持简洁，不要过度设计
```

- [ ] **Step 2: 写开发工程师提示词**

```
ai_dev_team/prompts/developer.txt
```

内容：
```
你是一位资深全栈开发工程师，擅长根据需求文档快速实现高质量的代码。

## 你的职责
1. 阅读产品经理提供的需求文档
2. 设计代码结构，选择合适的实现方式
3. 编写完整可运行的代码
4. 使用工具保存代码文件并执行验证
5. 如果执行报错，分析错误并修复

## 工作流程
1. 先仔细阅读需求文档，理解每个功能点
2. 规划代码文件结构
3. 逐个编写代码文件，使用 file_write_tool 保存
4. 使用 code_executor_tool 执行代码验证
5. 如果报错，分析错误信息，修改代码后重新验证

## 代码要求
- 代码必须完整可运行，不要有省略号或 TODO
- 包含必要的注释说明关键逻辑
- 函数和变量命名清晰
- 适当处理异常情况

## 输出格式
你必须严格按照以下 JSON 格式输出最终结果：

```json
{
    "files": {
        "main.py": "完整的代码内容",
        "utils.py": "完整的代码内容"
    },
    "execution_result": "最后一次代码执行的结果",
    "summary": "实现概述（用了什么方案、实现了哪些功能）"
}
```

注意：files 中的每个文件都必须是完整的、可直接运行的代码。
```

- [ ] **Step 3: 写测试工程师提示词**

```
ai_dev_team/prompts/tester.txt
```

内容：
```
你是一位资深测试工程师，擅长编写全面的测试用例并发现代码中的问题。

## 你的职责
1. 阅读开发工程师提交的代码
2. 分析代码逻辑，识别关键路径和边界情况
3. 编写 pytest 风格的测试用例
4. 执行测试并输出测试报告

## 工作流程
1. 仔细阅读所有源代码文件，理解每个函数的输入输出
2. 为每个关键函数编写测试用例，覆盖：
   - 正常输入（happy path）
   - 边界条件（空输入、极大值、特殊字符）
   - 异常情况（错误输入、类型不匹配）
3. 使用 file_write_tool 保存测试文件
4. 使用 code_executor_tool 运行测试（先安装 pytest）
5. 根据测试结果输出报告

## 测试要求
- 使用 pytest 框架
- 测试函数名要描述测试场景，如 test_add_positive_numbers
- 每个测试函数只测一个场景
- 使用 assert 断言结果

## 输出格式
你必须严格按照以下 JSON 格式输出测试报告：

```json
{
    "test_files": {
        "test_main.py": "完整的测试代码内容"
    },
    "test_results": "测试执行的详细输出",
    "coverage_summary": "测试覆盖了哪些功能点，有哪些可能未覆盖"
}
```
```

- [ ] **Step 4: 提交**

```bash
git add prompts/
git commit -m "feat: add system prompts for all 3 agents"
```

---

### Task 6: Agent 基类

**Files:**
- Create: `ai_dev_team/agents/base.py`

- [ ] **Step 1: 写 Agent 基类**

```python
"""Agent 基类。封装 LangChain 的 LLM 调用和输出解析逻辑。"""
import json
import re
from abc import ABC, abstractmethod
from typing import Any

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, TEMPERATURE, PROMPTS_DIR


class BaseAgent(ABC):
    """所有 Agent 的基类。

    封装了 LLM 初始化、Prompt 加载、调用和输出解析。
    子类只需实现 role、prompt_file、tools 属性即可。
    """

    def __init__(self):
        self.role: str = ""
        self.prompt_file: str = ""
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
        # 将输入数据格式化为文本
        input_text = self._format_input(input_data)

        # 调用 LLM
        raw_output = self._chain.invoke({"input": input_text})

        # 尝试解析 JSON 输出
        parsed = self._parse_json_output(raw_output)

        if parsed is not None:
            return parsed

        # 如果 JSON 解析失败，返回原始文本
        return {"raw_output": raw_output, "parse_error": "无法解析为 JSON 格式"}

    def _format_input(self, input_data: dict[str, Any]) -> str:
        """将输入字典格式化为文本。子类可以重写以自定义格式。"""
        lines = []
        for key, value in input_data.items():
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

        # 尝试找到第一个 { ... } 块
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    def run_with_tools(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """带工具调用的执行方式。

        将工具描述注入 Prompt，让 LLM 在输出中指定要调用的工具，
        然后执行工具并将结果反馈给 LLM。
        """
        if not self.tools:
            return self.run(input_data)

        # 构建工具描述
        tool_desc = "\n".join(
            f"- {t.name}: {t.description}" for t in self.tools
        )
        tool_names = ", ".join(t.name for t in self.tools)

        enhanced_input = {
            **input_data,
            "_available_tools": tool_desc,
            "_tool_names": tool_names,
        }

        return self.run(enhanced_input)
```

- [ ] **Step 2: 验证基类能正常导入**

```bash
cd ai_dev_team
python -c "
from agents.base import BaseAgent
print('BaseAgent 导入成功')
print(f'方法列表: {[m for m in dir(BaseAgent) if not m.startswith(\"_\")]}')
"
```

预期输出：
```
BaseAgent 导入成功
方法列表: ['run', 'run_with_tools']
```

- [ ] **Step 3: 提交**

```bash
git add agents/base.py
git commit -m "feat: add agent base class with LLM and JSON parsing"
```

---

### Task 7: 产品经理 Agent

**Files:**
- Create: `ai_dev_team/agents/product_manager.py`

- [ ] **Step 1: 写产品经理 Agent**

```python
"""产品经理 Agent。分析用户需求，输出结构化需求文档。"""
from typing import Any

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

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """分析用户需求并输出需求文档。

        Args:
            input_data: 包含 "requirement" 键的字典

        Returns:
            结构化需求文档
        """
        # 产品经理直接调用 LLM 分析需求，不走工具调用流程
        # 搜索工具作为 LLM 的参考信息来源
        return super().run(input_data)
```

- [ ] **Step 2: 验证 Agent 能创建**

```bash
cd ai_dev_team
python -c "
from agents.product_manager import ProductManagerAgent
pm = ProductManagerAgent()
print(f'角色: {pm.role}')
print(f'工具: {[t.name for t in pm.tools]}')
print('ProductManagerAgent 创建成功')
"
```

预期输出：
```
角色: product_manager
工具: ['web_search_tool']
ProductManagerAgent 创建成功
```

- [ ] **Step 3: 提交**

```bash
git add agents/product_manager.py
git commit -m "feat: add product manager agent"
```

---

### Task 8: 开发工程师 Agent

**Files:**
- Create: `ai_dev_team/agents/developer.py`

- [ ] **Step 1: 写开发工程师 Agent**

```python
"""开发工程师 Agent。根据需求文档编写代码并验证。"""
import json
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
        # 第一次调用：让 LLM 生成代码
        result = super().run(input_data)

        # 如果 LLM 输出了 files，尝试执行验证并自动修复
        if "files" in result and isinstance(result["files"], dict):
            result = self._verify_and_fix(result, input_data)

        return result

    def _verify_and_fix(self, result: dict, original_input: dict) -> dict:
        """验证代码执行结果，失败则自动修复。

        保存代码到 workspace，执行验证，如果报错则把错误信息
        回传给 LLM 让它修复，最多重试 MAX_RETRY 次。
        """
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
                    # LLM 没有返回有效的 files，使用之前的结果
                    result["execution_result"] = exec_result
                    result["auto_fix_failed"] = True
                    return result

                files = result["files"]
            else:
                result["execution_result"] = "[跳过验证] 未找到可执行的主文件"
                return result

        # 超过最大重试次数
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
```

- [ ] **Step 2: 验证 Agent 能创建**

```bash
cd ai_dev_team
python -c "
from agents.developer import DeveloperAgent
dev = DeveloperAgent()
print(f'角色: {dev.role}')
print(f'工具: {[t.name for t in dev.tools]}')
print('DeveloperAgent 创建成功')
"
```

预期输出：
```
角色: developer
工具: ['code_executor_tool', 'file_write_tool', 'file_read_tool']
DeveloperAgent 创建成功
```

- [ ] **Step 3: 提交**

```bash
git add agents/developer.py
git commit -m "feat: add developer agent with auto-retry"
```

---

### Task 9: 测试工程师 Agent

**Files:**
- Create: `ai_dev_team/agents/tester.py`

- [ ] **Step 1: 写测试工程师 Agent**

```python
"""测试工程师 Agent。分析代码，编写并执行测试用例。"""
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
        # 先确保 pytest 已安装
        install_result = code_executor_tool.invoke(
            "import subprocess; subprocess.run(['pip', 'install', 'pytest', '-q'], capture_output=True)"
        )

        # 调用 LLM 生成测试
        result = super().run(input_data)

        # 如果 LLM 输出了 test_files，保存并执行测试
        if "test_files" in result and isinstance(result["test_files"], dict):
            result = self._run_tests(result)

        return result

    def _run_tests(self, result: dict) -> dict:
        """保存测试文件并执行测试。"""
        test_files = result["test_files"]

        # 保存测试文件
        for filename, content in test_files.items():
            file_write_tool.invoke({"path": filename, "content": content})

        # 执行 pytest
        test_names = ", ".join(test_files.keys())
        test_code = (
            "import subprocess, sys\n"
            f"result = subprocess.run(\n"
            f"    [sys.executable, '-m', 'pytest', {test_names!r}, '-v', '--tb=short'],\n"
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
```

- [ ] **Step 2: 验证 Agent 能创建**

```bash
cd ai_dev_team
python -c "
from agents.tester import TesterAgent
tester = TesterAgent()
print(f'角色: {tester.role}')
print(f'工具: {[t.name for t in tester.tools]}')
print('TesterAgent 创建成功')
"
```

预期输出：
```
角色: tester
工具: ['code_executor_tool', 'file_write_tool']
TesterAgent 创建成功
```

- [ ] **Step 3: 提交**

```bash
git add agents/tester.py
git commit -m "feat: add tester agent with pytest execution"
```

---

### Task 10: 调度器

**Files:**
- Create: `ai_dev_team/orchestrator.py`

- [ ] **Step 1: 写调度器**

```python
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
```

- [ ] **Step 2: 验证调度器能创建**

```bash
cd ai_dev_team
python -c "
from orchestrator import Orchestrator
orch = Orchestrator()
print(f'产品经理: {orch.pm.role}')
print(f'开发工程师: {orch.dev.role}')
print(f'测试工程师: {orch.tester.role}')
print('Orchestrator 创建成功')
"
```

预期输出：
```
产品经理: product_manager
开发工程师: developer
测试工程师: tester
Orchestrator 创建成功
```

- [ ] **Step 3: 提交**

```bash
git add orchestrator.py
git commit -m "feat: add orchestrator for multi-agent collaboration"
```

---

### Task 11: Gradio Web 界面

**Files:**
- Create: `ai_dev_team/main.py`

- [ ] **Step 1: 写 Gradio 界面**

```python
"""Gradio Web 界面入口。实时展示 Multi-Agent 协作过程。"""
import json
import gradio as gr

from orchestrator import Orchestrator


def create_app() -> gr.Blocks:
    """创建 Gradio 应用。"""
    orch = Orchestrator()

    def run_team(requirement: str):
        """执行 Agent 协作流程，流式返回每一步的结果。"""
        if not requirement.strip():
            yield "请输入需求", "", "", ""
            return

        steps = {"pm": "", "dev": "", "tester": "", "summary": ""}

        def callback(step_name: str, content: str):
            if "产品" in step_name:
                steps["pm"] = f"### 产品经理\n\n{content}"
            elif "开发" in step_name:
                steps["dev"] = f"### 开发工程师\n\n```python\n{content}\n```"
            elif "测试" in step_name:
                steps["tester"] = f"### 测试工程师\n\n{content}"
            elif "完成" in step_name:
                steps["summary"] = f"### 执行完成\n\n{content}"

        # 生成器：每收到一个回调就 yield 更新
        result = {}

        def streaming_callback(step_name: str, content: str):
            callback(step_name, content)
            yield steps["pm"], steps["dev"], steps["tester"], steps["summary"]

        # 实际执行
        def run_with_updates():
            pm_result = {}
            dev_result = {}
            tester_result = {}

            # 产品经理
            steps["pm"] = "### 产品经理\n\n正在分析需求..."
            yield steps["pm"], steps["dev"], steps["tester"], steps["summary"]

            pm_result = orch.pm.run({"requirement": requirement})
            pm_text = json.dumps(pm_result, ensure_ascii=False, indent=2)
            steps["pm"] = f"### 产品经理\n\n**需求分析完成：**\n\n```json\n{pm_text}\n```"
            yield steps["pm"], steps["dev"], steps["tester"], steps["summary"]

            # 开发工程师
            steps["dev"] = "### 开发工程师\n\n正在编写代码..."
            yield steps["pm"], steps["dev"], steps["tester"], steps["summary"]

            dev_result = orch.dev.run({"requirements": pm_result})
            files_text = json.dumps(dev_result.get("files", {}), ensure_ascii=False, indent=2)
            exec_text = dev_result.get("execution_result", "无")
            steps["dev"] = (
                f"### 开发工程师\n\n**代码文件：**\n\n```json\n{files_text}\n```\n\n"
                f"**执行结果：**\n\n```\n{exec_text}\n```"
            )
            yield steps["pm"], steps["dev"], steps["tester"], steps["summary"]

            # 测试工程师
            steps["tester"] = "### 测试工程师\n\n正在编写测试..."
            yield steps["pm"], steps["dev"], steps["tester"], steps["summary"]

            tester_result = orch.tester.run({
                "code_files": dev_result.get("files", {}),
                "requirements": pm_result,
            })
            test_files_text = json.dumps(tester_result.get("test_files", {}), ensure_ascii=False, indent=2)
            test_results_text = tester_result.get("test_results", "无")
            coverage_text = tester_result.get("coverage_summary", "无")
            steps["tester"] = (
                f"### 测试工程师\n\n**测试代码：**\n\n```python\n{test_files_text}\n```\n\n"
                f"**测试结果：**\n\n```\n{test_results_text}\n```\n\n"
                f"**覆盖概述：**\n\n{coverage_text}"
            )
            yield steps["pm"], steps["dev"], steps["tester"], steps["summary"]

            # 完成
            steps["summary"] = "### 所有 Agent 工作完成！"
            yield steps["pm"], steps["dev"], steps["tester"], steps["summary"]

        # 使用生成器
        for update in run_with_updates():
            yield update

    # 构建界面
    with gr.Blocks(title="AI 研发团队", theme=gr.themes.Soft()) as app:
        gr.Markdown("# AI 研发团队协作系统")
        gr.Markdown("输入你的需求，AI 产品经理、开发工程师、测试工程师将协作完成开发任务。")

        with gr.Row():
            requirement_input = gr.Textbox(
                label="请输入你的需求",
                placeholder="例如：用 Python 实现一个计算器，支持加减乘除运算",
                lines=3,
            )

        run_btn = gr.Button("开始协作", variant="primary", size="lg")

        with gr.Row():
            pm_output = gr.Markdown(label="产品经理", value="等待输入...")
            dev_output = gr.Markdown(label="开发工程师", value="等待输入...")

        with gr.Row():
            tester_output = gr.Markdown(label="测试工程师", value="等待输入...")
            summary_output = gr.Markdown(label="执行状态", value="等待输入...")

        run_btn.click(
            fn=run_team,
            inputs=[requirement_input],
            outputs=[pm_output, dev_output, tester_output, summary_output],
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
```

- [ ] **Step 2: 验证界面能启动**

```bash
cd ai_dev_team
python main.py
```

预期：浏览器打开 http://localhost:7860 ，看到输入框和"开始协作"按钮

- [ ] **Step 3: 提交**

```bash
git add main.py
git commit -m "feat: add Gradio web interface with streaming updates"
```

---

### Task 12: README 文档

**Files:**
- Create: `ai_dev_team/README.md`

- [ ] **Step 1: 写 README**

```markdown
# AI 研发团队协作系统

基于 LangChain 的 Multi-Agent 协作系统，模拟产品经理→开发工程师→测试工程师的研发团队。

## 功能

- **产品经理 Agent**：分析需求，输出结构化需求文档
- **开发工程师 Agent**：编写代码，自动执行验证，失败自动修复（最多3次）
- **测试工程师 Agent**：编写 pytest 测试用例，执行测试并输出报告
- **工具调用**：代码执行（沙箱）、文件读写（目录隔离）、网络搜索
- **Web 界面**：Gradio 实时展示每个 Agent 的工作过程

## 技术栈

- Python 3.10+
- LangChain（Agent 框架）
- DeepSeek-V4（大模型）
- Gradio（Web 界面）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

编辑 `.env` 文件，填入你的 DeepSeek API Key：

```env
DEEPSEEK_API_KEY=你的API密钥
```

获取地址：https://platform.deepseek.com/api_keys

### 3. 启动

```bash
python main.py
```

浏览器访问 http://localhost:7860

## 项目结构

```
ai_dev_team/
├── main.py                  # Gradio 入口
├── orchestrator.py          # 调度器（串联 Agent 流程）
├── config.py                # 配置
├── agents/
│   ├── base.py              # Agent 基类
│   ├── product_manager.py   # 产品经理
│   ├── developer.py         # 开发工程师
│   └── tester.py            # 测试工程师
├── tools/
│   ├── code_executor.py     # 代码执行（沙箱+超时）
│   ├── file_manager.py      # 文件读写（目录隔离）
│   └── web_search.py        # 网络搜索
├── prompts/
│   ├── product_manager.txt
│   ├── developer.txt
│   └── tester.txt
└── workspace/               # Agent 工作目录
```

## 面试要点

1. **Agent 编排**：如何设计 Agent 间的协作流程和消息传递？
2. **工具调用**：Agent 如何自主决定调用哪个工具？
3. **错误处理**：代码执行失败如何自动修复？
4. **安全设计**：代码执行沙箱、路径隔离、超时保护
5. **结构化输出**：Agent 间传递 JSON 而非纯文本的原因
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add README with usage guide and interview points"
```

---

## 验证清单

完成所有 Task 后，按以下顺序验证整个系统：

1. **环境检查**
   ```bash
   cd ai_dev_team
   pip install -r requirements.txt
   # 确认 .env 中有正确的 DEEPSEEK_API_KEY
   ```

2. **模块导入检查**
   ```bash
   python -c "from orchestrator import Orchestrator; print('全部模块导入成功')"
   ```

3. **完整流程测试**
   ```bash
   python main.py
   ```
   在浏览器输入需求（例如："用 Python 实现一个两数之和的函数"），观察三个 Agent 是否依次工作并输出结果。

4. **检查 workspace 目录**
   Agent 执行后，workspace/ 下应该有代码文件和测试文件。
