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
BANNED_IMPORTS = ["os.system", "shutil.rmtree"]
