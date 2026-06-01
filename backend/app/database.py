import aiosqlite
import chromadb
from pathlib import Path
from .config import get_settings

settings = get_settings()

# ChromaDB 客户端
chroma_client = chromadb.PersistentClient(path=settings.chromadb_path)

# 知识库集合
knowledge_collection = chroma_client.get_or_create_collection(
    name="knowledge_base",
    metadata={"hnsw:space": "cosine"}
)


async def get_sqlite() -> aiosqlite.Connection:
    """获取 SQLite 连接"""
    db_path = Path(settings.sqlite_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(str(db_path))
    db.row_factory = aiosqlite.Row
    return db


async def init_database():
    """初始化数据库表"""
    db = await get_sqlite()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(255),
                domain VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id VARCHAR(50) NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS knowledge_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL,
                file_type VARCHAR(20),
                file_size INTEGER,
                chunk_count INTEGER DEFAULT 0,
                domain VARCHAR(50),
                status VARCHAR(20) DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL,
                raw_text TEXT,
                parsed_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255),
                raw_text TEXT,
                parsed_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS match_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER,
                jd_id INTEGER,
                final_score FLOAT,
                hard_score FLOAT,
                skill_score FLOAT,
                exp_score FLOAT,
                project_score FLOAT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (resume_id) REFERENCES resumes(id),
                FOREIGN KEY (jd_id) REFERENCES job_descriptions(id)
            );

            CREATE TABLE IF NOT EXISTS eval_experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100),
                status VARCHAR(20) DEFAULT 'pending',
                faithfulness FLOAT,
                context_precision FLOAT,
                context_recall FLOAT,
                answer_relevancy FLOAT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.commit()
    finally:
        await db.close()
