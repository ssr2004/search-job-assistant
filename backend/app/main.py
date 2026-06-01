from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .database import init_database
from .api import chat, knowledge, resume, jd, match, eval, gap


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    await init_database()
    yield


app = FastAPI(
    title="智能求职助手 API",
    description="覆盖面试准备、知识问答、简历筛选、技能差距分析的完整求职助手",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(resume.router)
app.include_router(jd.router)
app.include_router(match.router)
app.include_router(eval.router)
app.include_router(gap.router)


@app.get("/")
async def root():
    return {"message": "智能求职助手 API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
