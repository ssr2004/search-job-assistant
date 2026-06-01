import json
import tempfile
from pathlib import Path
from ..database import get_sqlite
from ..models.resume import (
    ResumeResponse, ResumeDetail, JDCreate, JDResponse, JDDetail,
    MatchResult
)
from ..models.eval import GapAnalysisResponse
from ..utils.resume_parser import parse_resume, parse_jd
from ..utils.matching import match_resume_jd
from ..utils.llm import chat_complete


class ResumeService:
    """简历服务"""

    async def upload(self, file) -> ResumeResponse:
        """上传简历并解析"""
        content = await file.read()

        # 保存临时文件
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        # 解析简历
        parsed = await parse_resume(tmp_path)
        Path(tmp_path).unlink(missing_ok=True)

        raw_text = content.decode("utf-8", errors="ignore")

        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "INSERT INTO resumes (filename, raw_text, parsed_content) VALUES (?, ?, ?)",
                (file.filename, raw_text, json.dumps(parsed, ensure_ascii=False))
            )
            await db.commit()
            return ResumeResponse(id=cursor.lastrowid, filename=file.filename, created_at="")
        finally:
            await db.close()

    async def list_all(self) -> list[ResumeResponse]:
        """获取简历列表"""
        db = await get_sqlite()
        try:
            cursor = await db.execute("SELECT id, filename, created_at FROM resumes ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [ResumeResponse(id=r[0], filename=r[1], created_at=str(r[2])) for r in rows]
        finally:
            await db.close()

    async def get_detail(self, resume_id: int) -> ResumeDetail:
        """获取简历详情"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "SELECT id, filename, raw_text, parsed_content, created_at FROM resumes WHERE id = ?",
                (resume_id,)
            )
            row = await cursor.fetchone()
            if not row:
                raise ValueError("Resume not found")
            parsed = json.loads(row[3]) if row[3] else None
            return ResumeDetail(id=row[0], filename=row[1], raw_text=row[2], parsed_content=parsed, created_at=str(row[4]))
        finally:
            await db.close()

    async def create_jd(self, request: JDCreate) -> JDResponse:
        """创建 JD 并解析"""
        # 解析 JD
        parsed = await parse_jd(request.raw_text)

        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "INSERT INTO job_descriptions (title, raw_text, parsed_content) VALUES (?, ?, ?)",
                (request.title, request.raw_text, json.dumps(parsed, ensure_ascii=False))
            )
            await db.commit()
            return JDResponse(id=cursor.lastrowid, title=request.title, created_at="")
        finally:
            await db.close()

    async def list_jds(self) -> list[JDResponse]:
        """获取 JD 列表"""
        db = await get_sqlite()
        try:
            cursor = await db.execute("SELECT id, title, created_at FROM job_descriptions ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [JDResponse(id=r[0], title=r[1], created_at=str(r[2])) for r in rows]
        finally:
            await db.close()

    async def get_jd_detail(self, jd_id: int) -> JDDetail:
        """获取 JD 详情"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "SELECT id, title, raw_text, parsed_content, created_at FROM job_descriptions WHERE id = ?",
                (jd_id,)
            )
            row = await cursor.fetchone()
            if not row:
                raise ValueError("JD not found")
            parsed = json.loads(row[3]) if row[3] else None
            return JDDetail(id=row[0], title=row[1], raw_text=row[2], parsed_content=parsed, created_at=str(row[4]))
        finally:
            await db.close()

    async def match(self, resume_id: int, jd_id: int) -> MatchResult:
        """执行匹配"""
        # 获取简历和 JD
        resume = await self._get_resume_parsed(resume_id)
        jd = await self._get_jd_parsed(jd_id)

        if not resume or not jd:
            raise ValueError("简历或 JD 不存在")

        # 执行匹配
        result = await match_resume_jd(resume, jd)

        # 保存结果
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                """INSERT INTO match_results (resume_id, jd_id, final_score, hard_score, skill_score, exp_score, project_score, details)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (resume_id, jd_id, result["final_score"],
                 result["hard_requirements"]["score"],
                 result["skill_match"]["score"],
                 result["experience_match"]["score"],
                 result["project_match"]["score"],
                 json.dumps(result, ensure_ascii=False))
            )
            await db.commit()
            match_id = cursor.lastrowid

            return MatchResult(
                id=match_id, resume_id=resume_id, jd_id=jd_id,
                final_score=result["final_score"],
                hard_score=result["hard_requirements"]["score"],
                skill_score=result["skill_match"]["score"],
                exp_score=result["experience_match"]["score"],
                project_score=result["project_match"]["score"],
                details=result,
                created_at=""
            )
        finally:
            await db.close()

    async def _get_resume_parsed(self, resume_id: int) -> dict:
        """获取简历解析结果"""
        db = await get_sqlite()
        try:
            cursor = await db.execute("SELECT parsed_content FROM resumes WHERE id = ?", (resume_id,))
            row = await cursor.fetchone()
            if row and row[0]:
                return json.loads(row[0])
            return None
        finally:
            await db.close()

    async def _get_jd_parsed(self, jd_id: int) -> dict:
        """获取 JD 解析结果"""
        db = await get_sqlite()
        try:
            cursor = await db.execute("SELECT parsed_content FROM job_descriptions WHERE id = ?", (jd_id,))
            row = await cursor.fetchone()
            if row and row[0]:
                return json.loads(row[0])
            return None
        finally:
            await db.close()

    async def get_match_results(self) -> list[MatchResult]:
        """获取匹配结果列表"""
        db = await get_sqlite()
        try:
            cursor = await db.execute(
                "SELECT id, resume_id, jd_id, final_score, hard_score, skill_score, exp_score, project_score, details, created_at FROM match_results ORDER BY created_at DESC"
            )
            rows = await cursor.fetchall()
            return [MatchResult(
                id=r[0], resume_id=r[1], jd_id=r[2], final_score=r[3],
                hard_score=r[4], skill_score=r[5], exp_score=r[6],
                project_score=r[7], details=json.loads(r[8]) if r[8] else {}, created_at=str(r[9])
            ) for r in rows]
        finally:
            await db.close()

    async def analyze_gap(self, resume_id: int, jd_id: int) -> GapAnalysisResponse:
        """分析技能差距"""
        # 获取简历和 JD
        resume = await self._get_resume_parsed(resume_id)
        jd = await self._get_jd_parsed(jd_id)

        if not resume or not jd:
            raise ValueError("简历或 JD 不存在")

        # 提取技能集合
        resume_skills = set(resume.get("skills", []))
        required_skills = set(jd.get("hard_requirements", {}).get("skills_required", []))
        preferred_skills = set(jd.get("hard_requirements", {}).get("skills_preferred", []))

        # 计算匹配情况
        matched_required = resume_skills & required_skills
        missing_required = required_skills - resume_skills
        matched_preferred = resume_skills & preferred_skills
        missing_preferred = preferred_skills - resume_skills

        # 生成学习推荐
        recommendations = await self._generate_recommendations(missing_required, missing_preferred)

        # 计算匹配率
        required_match_rate = len(matched_required) / len(required_skills) if required_skills else 1.0
        preferred_match_rate = len(matched_preferred) / len(preferred_skills) if preferred_skills else 1.0
        overall_match_rate = (required_match_rate + preferred_match_rate) / 2

        return GapAnalysisResponse(
            required_match_rate=round(required_match_rate, 3),
            preferred_match_rate=round(preferred_match_rate, 3),
            overall_match_rate=round(overall_match_rate, 3),
            matched_required=list(matched_required),
            missing_required=list(missing_required),
            matched_preferred=list(matched_preferred),
            missing_preferred=list(missing_preferred),
            recommendations=recommendations
        )

    async def _generate_recommendations(self, missing_required: set, missing_preferred: set) -> list:
        """生成学习推荐"""
        if not missing_required and not missing_preferred:
            return [{"message": "恭喜！你已满足所有技能要求"}]

        prompt = f"""作为职业顾问，请为以下缺失技能提供学习推荐。

必须掌握的技能（缺失）：{', '.join(missing_required) if missing_required else '无'}
加分技能（缺失）：{', '.join(missing_preferred) if missing_preferred else '无'}

请为每个技能提供：
1. 推荐学习资源（书籍/课程/文档）
2. 预计学习时间
3. 学习优先级（高/中/低）

以JSON数组格式输出。"""

        messages = [{"role": "user", "content": prompt}]
        result = await chat_complete(messages)

        try:
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            return json.loads(result.strip())
        except:
            return [{"skill": s, "priority": "高"} for s in missing_required]
