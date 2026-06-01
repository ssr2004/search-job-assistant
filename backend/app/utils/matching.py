import json
import numpy as np
from ..utils.embedding import encode_texts
from ..utils.llm import chat_complete


async def match_resume_jd(resume: dict, jd: dict) -> dict:
    """匹配简历与 JD"""
    # 1. 硬性条件检查
    hard_score, hard_details = check_hard_requirements(resume, jd)

    # 2. 技能语义匹配
    skill_score, skill_details = compute_skill_similarity(
        resume.get("skills", []),
        jd.get("hard_requirements", {}).get("skills_required", [])
    )

    # 3. 经验匹配
    exp_score, exp_details = compute_experience_match(
        resume.get("work_experience", []),
        jd
    )

    # 4. 项目匹配
    project_score, project_details = compute_project_match(
        resume.get("project_experience", []),
        jd
    )

    # 5. 综合评分（加权平均）
    final_score = (
        0.3 * hard_score +
        0.3 * skill_score +
        0.2 * exp_score +
        0.2 * project_score
    )

    return {
        "final_score": round(final_score, 4),
        "hard_requirements": {"score": hard_score, "details": hard_details},
        "skill_match": {"score": skill_score, "details": skill_details},
        "experience_match": {"score": exp_score, "details": exp_details},
        "project_match": {"score": project_score, "details": project_details}
    }


def check_hard_requirements(resume: dict, jd: dict) -> tuple:
    """硬性条件检查"""
    scores = []
    details = {}

    # 学历检查
    education = resume.get("basic_info", {}).get("education", [])
    if education:
        highest_degree = get_highest_degree(education)
        required_degree = jd.get("hard_requirements", {}).get("education", {}).get("min_degree", "本科")
        degree_score = compare_degree(highest_degree, required_degree)
        scores.append(degree_score)
        details["education"] = {"resume": highest_degree, "required": required_degree, "match": degree_score}
    else:
        scores.append(0.5)
        details["education"] = {"resume": "未知", "required": "未知", "match": 0.5}

    # 年限检查
    work_exp = resume.get("work_experience", [])
    years = calculate_experience_years(work_exp)
    exp_req = jd.get("hard_requirements", {}).get("experience", {})
    min_years = exp_req.get("min_years", 0)
    max_years = exp_req.get("max_years", 10)
    years_score = 1.0 if min_years <= years <= max_years else max(0, 1 - abs(years - min_years) * 0.2)
    scores.append(years_score)
    details["experience_years"] = {"resume": years, "required": f"{min_years}-{max_years}", "match": years_score}

    return sum(scores) / len(scores) if scores else 0, details


def get_highest_degree(education: list) -> str:
    """获取最高学历"""
    degree_order = {"博士": 4, "硕士": 3, "本科": 2, "大专": 1}
    highest = "未知"
    highest_val = 0
    for edu in education:
        degree = edu.get("degree", "")
        val = degree_order.get(degree, 0)
        if val > highest_val:
            highest_val = val
            highest = degree
    return highest


def compare_degree(resume_degree: str, required_degree: str) -> float:
    """比较学历"""
    degree_order = {"博士": 4, "硕士": 3, "本科": 2, "大专": 1}
    resume_val = degree_order.get(resume_degree, 0)
    required_val = degree_order.get(required_degree, 0)
    if resume_val >= required_val:
        return 1.0
    elif resume_val == required_val - 1:
        return 0.5
    else:
        return 0.0


def calculate_experience_years(work_experience: list) -> int:
    """计算工作年限"""
    if not work_experience:
        return 0
    # 简单计算：取最新工作的开始年份到最早工作的开始年份
    years = len(work_experience)  # 简化处理
    return years


def compute_skill_similarity(resume_skills: list, jd_skills: list) -> tuple:
    """技能语义匹配"""
    if not resume_skills or not jd_skills:
        return 0.0, {"matched": [], "missing": jd_skills}

    # Embedding 编码
    resume_embeddings = encode_texts(resume_skills)
    jd_embeddings = encode_texts(jd_skills)

    # 余弦相似度矩阵
    resume_arr = np.array(resume_embeddings)
    jd_arr = np.array(jd_embeddings)
    sim_matrix = np.dot(resume_arr, jd_arr.T) / (
        np.linalg.norm(resume_arr, axis=1, keepdims=True) * np.linalg.norm(jd_arr, axis=1)
    )

    # 每个 JD 技能找最匹配的简历技能
    matched = []
    missing = []
    for i, jd_skill in enumerate(jd_skills):
        max_sim = sim_matrix[:, i].max()
        if max_sim > 0.7:  # 相似度阈值
            best_match_idx = sim_matrix[:, i].argmax()
            matched.append({
                "jd_skill": jd_skill,
                "resume_skill": resume_skills[best_match_idx],
                "similarity": round(float(max_sim), 3)
            })
        else:
            missing.append(jd_skill)

    score = len(matched) / len(jd_skills)
    return score, {"matched": matched, "missing": missing}


def compute_experience_match(work_experience: list, jd: dict) -> tuple:
    """经验匹配"""
    if not work_experience:
        return 0.0, {"reason": "无工作经验"}

    # 提取 JD 关键词
    keywords = jd.get("keywords", [])
    if not keywords:
        return 0.5, {"reason": "JD 无关键词"}

    # 检查工作经验中是否包含关键词
    matched_keywords = []
    for exp in work_experience:
        desc = exp.get("description", "") + " " + " ".join(exp.get("achievements", []))
        for kw in keywords:
            if kw.lower() in desc.lower() and kw not in matched_keywords:
                matched_keywords.append(kw)

    score = len(matched_keywords) / len(keywords) if keywords else 0
    return score, {"matched_keywords": matched_keywords, "total_keywords": len(keywords)}


def compute_project_match(project_experience: list, jd: dict) -> tuple:
    """项目匹配"""
    if not project_experience:
        return 0.0, {"reason": "无项目经验"}

    # 提取 JD 技能要求
    required_skills = set(jd.get("hard_requirements", {}).get("skills_required", []))
    preferred_skills = set(jd.get("hard_requirements", {}).get("skills_preferred", []))
    all_skills = required_skills | preferred_skills

    if not all_skills:
        return 0.5, {"reason": "JD 无技能要求"}

    # 检查项目技术栈是否匹配
    matched_skills = []
    for proj in project_experience:
        tech_stack = proj.get("tech_stack", [])
        for tech in tech_stack:
            if tech in all_skills and tech not in matched_skills:
                matched_skills.append(tech)

    score = len(matched_skills) / len(all_skills) if all_skills else 0
    return score, {"matched_skills": matched_skills, "total_skills": len(all_skills)}
