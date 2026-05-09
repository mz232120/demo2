# Multi-Agent AI 研发团队协作系统 - 设计文档

## 1. 项目概述

### 1.1 目标
构建一个基于 LangChain 的 Multi-Agent 协作系统，模拟 AI 研发团队（产品经理→开发工程师→测试工程师）协作完成软件开发任务。支持工具调用（代码执行、文件读写），通过 Gradio Web 界面交互。

### 1.2 目标用户
- 简历项目展示
- 面试时能讲清楚 Agent 编排、工具调用、协作机制等技术细节

### 1.3 技术栈
| 层 | 技术 | 说明 |
|---|------|------|
| LLM 框架 | LangChain | Agent 定义、消息传递、工具调用 |
| 大模型 | DeepSeek-V4 | OpenAI 兼容接口，通过 ChatOpenAI 接入 |
| 工具 | Python 自定义 | 代码执行、文件读写 |
| 前端 | Gradio | Web 界面，实时展示 Agent 工作过程 |
| 语言 | Python 3.10+ | 项目开发语言 |

## 2. 系统架构

### 2.1 整体流程

```
用户输入需求（Web 界面）
    │
    ▼
┌─────────────────────┐
│   Orchestrator      │  ← 核心调度器，管理 Agent 协作流程
│   (orchestrator.py) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│  产品经理 Agent      │  接收需求 → 分析 → 输出需求文档
│  (product_manager)  │
└─────────┬───────────┘
          │ 结构化输出（需求文档）
          ▼
┌─────────────────────┐
│  开发工程师 Agent    │  读取需求 → 写代码 → 执行验证 → 修复错误（最多3次）
│  (developer)        │
└─────────┬───────────┘
          │ 结构化输出（代码文件）
          ▼
┌─────────────────────┐
│  测试工程师 Agent    │  读取代码 → 写测试 → 执行测试 → 输出报告
│  (tester)           │
└─────────┬───────────┘
          │
          ▼
    汇总结果返回 Web 界面
    （需求文档 + 代码 + 测试报告）
```

### 2.2 目录结构

```
ai_dev_team/
├── main.py                  # 入口，启动 Gradio 界面
├── orchestrator.py          # 调度器：管理 Agent 协作流程
├── agents/
│   ├── __init__.py
│   ├── base.py              # Agent 基类（封装 LangChain Agent）
│   ├── product_manager.py   # 产品经理 Agent
│   ├── developer.py         # 开发工程师 Agent
│   └── tester.py            # 测试工程师 Agent
├── tools/
│   ├── __init__.py
│   ├── code_executor.py     # 代码执行工具（沙箱运行 Python）
│   ├── file_manager.py      # 文件读写工具
│   └── web_search.py        # 搜索工具（可选）
├── prompts/
│   ├── product_manager.txt  # 产品经理 System Prompt
│   ├── developer.txt        # 开发工程师 System Prompt
│   └── tester.txt           # 测试工程师 System Prompt
├── config.py                # 配置（API Key、模型参数等）
├── requirements.txt         # 依赖
└── README.md                # 项目说明
```

## 3. 模块详细设计

### 3.1 配置模块 (config.py)

```python
# 统一管理 API Key、模型名称、超时等配置
DEEPSEEK_API_KEY = "your-api-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"
MAX_RETRY = 3  # Agent 最大重试次数
```

### 3.2 Agent 基类 (agents/base.py)

每个 Agent 继承基类，封装 LangChain 的 AgentExecutor：
- `role`: 角色名称
- `system_prompt`: 角色人设提示词
- `tools`: 该 Agent 可用的工具列表
- `run(input_data) -> dict`: 执行任务，返回结构化结果

关键设计：Agent 接收的输入和输出都是**结构化字典**，不是纯文本，确保下游 Agent 能精确解析。

### 3.3 产品经理 Agent (agents/product_manager.py)

- **输入**: 用户的自然语言需求
- **工具**: web_search（可选，搜索技术方案）
- **输出**:
  ```python
  {
      "project_name": "项目名称",
      "description": "需求描述",
      "features": ["功能点1", "功能点2"],
      "tech_stack": ["技术选型"],
      "api_design": "接口设计",
      "acceptance_criteria": "验收标准"
  }
  ```

### 3.4 开发工程师 Agent (agents/developer.py)

- **输入**: 产品经理输出的需求文档
- **工具**: code_executor, file_manager
- **流程**:
  1. 根据需求编写代码
  2. 调用 file_manager 保存代码文件
  3. 调用 code_executor 验证语法/运行
  4. 如果报错，分析错误并修复，最多重试 3 次
- **输出**:
  ```python
  {
      "files": {"main.py": "代码内容", "utils.py": "代码内容"},
      "execution_result": "执行结果",
      "summary": "实现概述"
  }
  ```

### 3.5 测试工程师 Agent (agents/tester.py)

- **输入**: 开发工程师输出的代码
- **工具**: code_executor, file_manager
- **流程**:
  1. 分析代码逻辑
  2. 编写测试用例（pytest 风格）
  3. 保存测试文件并执行
  4. 输出测试报告
- **输出**:
  ```python
  {
      "test_files": {"test_main.py": "测试代码内容"},
      "test_results": "通过/失败详情",
      "coverage_summary": "测试覆盖概述"
  }
  ```

### 3.6 调度器 (orchestrator.py)

核心控制逻辑，负责：
1. 按顺序调用三个 Agent
2. 解析每个 Agent 的结构化输出，喂给下一个 Agent
3. 错误处理：代码执行失败时回传给开发 Agent 修复
4. 收集每一步的中间结果，实时推送到 Web 界面
5. 最终汇总结果

```python
class Orchestrator:
    def __init__(self):
        self.pm = ProductManagerAgent()
        self.dev = DeveloperAgent()
        self.tester = TesterAgent()
        self.max_retry = 3

    def run(self, user_requirement: str, callback=None) -> dict:
        # 1. 产品经理分析需求
        # 2. 开发工程师实现代码（含重试）
        # 3. 测试工程师验证代码
        # 4. 汇总返回
        pass
```

### 3.7 工具模块

#### code_executor.py - 代码执行工具
- 使用 Python `subprocess` 在隔离环境中执行代码
- 设置超时（默认 30 秒）
- 捕获 stdout/stderr/返回码
- 安全限制：禁止危险模块导入（os.system, subprocess 等可配置）

#### file_manager.py - 文件读写工具
- `write_file(path, content)`: 写入文件
- `read_file(path)`: 读取文件
- `list_files(dir)`: 列出目录文件
- 所有操作限制在 `workspace/` 目录下，防止越权

#### web_search.py - 搜索工具（可选）
- 使用 DuckDuckGo Search（无需 API Key）
- 供产品经理 Agent 搜索技术方案

### 3.8 前端界面 (main.py)

使用 Gradio 构建，界面布局：
- **输入区**: 文本框输入需求 + "开始"按钮
- **过程展示区**: 实时流式显示每个 Agent 的工作过程
  - 产品经理：需求分析
  - 开发工程师：代码编写 + 执行结果
  - 测试工程师：测试用例 + 测试报告
- **结果区**: 最终的代码文件、测试报告可下载

## 4. Agent 协作机制

### 4.1 消息传递
Agent 之间传递**结构化数据（字典）**，不是纯文本。每个 Agent 的 Prompt 中包含明确的输入格式说明和输出 JSON Schema 要求。

### 4.2 错误处理
- 代码执行失败 → 错误信息 + 原始代码回传给开发 Agent → 修复后重试（最多 3 次）
- 3 次仍失败 → 标记任务失败，返回已有结果和错误信息
- Agent 输出格式异常 → 调度器尝试提取关键信息，兜底处理

### 4.3 重试策略
- 开发 Agent 代码执行失败时自动重试
- 每次重试时，把上一次的错误信息作为额外上下文传入
- 超过最大重试次数则终止流程

## 5. 安全设计

- 代码执行在 `workspace/` 目录下，限制文件访问范围
- 设置执行超时（30秒），防止死循环
- 禁止导入危险模块（可配置黑名单）
- API Key 通过环境变量加载，不硬编码

## 6. 依赖

```
langchain>=0.3
langchain-openai>=0.3
langchain-community>=0.3
gradio>=5.0
duckduckgo-search  # 可选
```
