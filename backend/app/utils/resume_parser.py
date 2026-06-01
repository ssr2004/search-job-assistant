import json
import tempfile
from pathlib import Path
from ..utils.llm import chat_complete


async def parse_resume(file_path: str) -> dict:
    """解析简历，提取结构化信息"""
    # 提取文本
    raw_text = extract_text(file_path)

    # LLM 结构化提取
    prompt = f"""请从以下简历文本中提取结构化信息。

简历文本：
{raw_text}

请提取以下字段（JSON格式）：
{{
    "basic_info": {{
        "name": "姓名",
        "phone": "电话",
        "email": "邮箱",
        "education": [
            {{"school": "学校", "degree": "学历", "major": "专业", "start": "2020-09", "end": "2024-06"}}
        ]
    }},
    "skills": ["Python", "Java", "机器学习"],
    "work_experience": [
        {{
            "company": "公司名",
            "position": "职位",
            "start": "2024-07",
            "end": "至今",
            "description": "工作描述",
            "achievements": ["成就1", "成就2"]
        }}
    ],
    "project_experience": [
        {{
            "name": "项目名",
            "role": "角色",
            "tech_stack": ["技术栈"],
            "description": "项目描述",
            "achievements": ["成就1"]
        }}
    ]
}}

只输出 JSON，不要其他文字。"""

    messages = [{"role": "user", "content": prompt}]
    result = await chat_complete(messages)

    # 解析 JSON
    try:
        # 尝试提取 JSON
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        return json.loads(result.strip())
    except json.JSONDecodeError:
        return {"raw_text": raw_text, "parse_error": "JSON 解析失败", "llm_output": result}


async def parse_jd(jd_text: str) -> dict:
    """解析 JD，提取结构化招聘要求"""
    prompt = f"""请分析以下职位描述，提取结构化的招聘要求。

职位描述：
{jd_text}

请提取以下信息（JSON格式）：
{{
    "position": "职位名称",
    "hard_requirements": {{
        "education": {{"min_degree": "本科", "major": ["计算机"]}},
        "experience": {{"min_years": 0, "max_years": 3}},
        "skills_required": ["Python", "机器学习"],
        "skills_preferred": ["LangChain", "RAG"]
    }},
    "keywords": ["LLM", "RAG", "Agent"],
    "keyword_weights": {{
        "LLM": 0.9,
        "RAG": 0.8,
        "Agent": 0.7
    }}
}}

只输出 JSON，不要其他文字。"""

    messages = [{"role": "user", "content": prompt}]
    result = await chat_complete(messages)

    # 解析 JSON
    try:
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        return json.loads(result.strip())
    except json.JSONDecodeError:
        return {"raw_text": jd_text, "parse_error": "JSON 解析失败", "llm_output": result}


def extract_text(file_path: str) -> str:
    """提取文本"""
    suffix = Path(file_path).suffix.lower()

    if suffix == ".pdf":
        import fitz
        doc = fitz.open(file_path)
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        doc.close()
        return "\n".join(text_parts)
    elif suffix == ".docx":
        from docx import Document
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
