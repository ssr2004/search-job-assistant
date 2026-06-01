from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # LLM 配置
    llm_provider: str = "deepseek"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    llm_base_url: str = "https://api.deepseek.com"

    # Embedding 模型
    embedding_model: str = "BAAI/bge-small-zh-v1.5"

    # Re-ranking 模型
    reranker_model: str = "BAAI/bge-reranker-base"

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
