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
cd ai_dev_team
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

### 1. Agent 编排
本项目没有使用现成的 Multi-Agent 框架（如 AutoGen、CrewAI），而是基于 LangChain 自己实现了 Agent 间的协作编排。Orchestrator 调度器负责管理 Agent 的执行顺序、数据传递和错误处理。

### 2. 结构化消息传递
Agent 之间传递的是结构化字典（JSON），不是纯文本。每个 Agent 的 Prompt 中明确要求输出 JSON 格式，基类 `_parse_json_output` 方法支持从多种格式中提取 JSON。这样下游 Agent 能精确解析上游的输出。

### 3. 工具调用与安全设计
- 代码执行：使用 subprocess 隔离运行，设置超时保护，禁止危险模块导入
- 文件操作：限制在 workspace/ 目录下，_safe_path 方法防止目录穿越攻击
- 搜索工具：使用 DuckDuckGo，无需 API Key

### 4. 错误处理与自动修复
开发 Agent 的代码如果执行失败，会将错误信息回传给 LLM 分析修复，最多重试 3 次。每次重试都会附带上一次的错误信息作为上下文。

### 5. 为什么选 LangChain 而不是 AutoGen
- LangChain 更底层，能完全掌控 Agent 的行为和消息格式
- 面试时可以深入讲 LLM 调用链（Prompt → Model → Parser）
- 不依赖框架的黑盒行为，所有逻辑都在自己代码中
