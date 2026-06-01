from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM 配置（通义千问）
    llm_provider: str = "dashscope"
    llm_api_key: str = ""
    llm_model: str = "qwen-turbo"
    llm_base_url: str = "https://dashscope.aliyuncs.com"

    # 数据库
    chromadb_path: str = "./data/chromadb"
    sqlite_path: str = "./data/sqlite/app.db"

    # 服务端口
    backend_port: int = 8000
    frontend_port: int = 5173

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
