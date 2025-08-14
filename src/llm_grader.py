from typing import List, Dict, Any
import re
from .utils import guess_lang
from pydantic import BaseModel, Field

class GradeItem(BaseModel):
    question_id: str
    score: float
    max_points: float
    rationale: str

class GradeReport(BaseModel):
    total_score: float
    total_max: float
    items: List[GradeItem] = Field(default_factory=list)

def _keyword_score(answer: str, rubric_q: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple keyword-based grading.
    Each criterion is matched by keyword presence (case-insensitive).
    Score is proportional to how many criteria matched.
    """
    text = answer.lower()
    criteria = rubric_q.get("criteria", [])
    matches = 0
    for crit in criteria:
        # Extract keywords as non-stopword words
        words = [w for w in re.findall(r"\w+", crit.lower()) if len(w) > 3]
        if any(w in text for w in words):
            matches += 1
    max_points = rubric_q.get("max_points", 0)
    score = round(max_points * (matches / max(len(criteria), 1)), 2)
    rationale = f"Matched {matches}/{len(criteria)} criteria."
    return {"score": score, "rationale": rationale}

def grade_questions(question_blobs: List[Dict[str, str]], rubric: List[Dict[str, Any]], model: str = None) -> GradeReport:
    rubric_by_id = {q["id"]: q for q in rubric}
    items: List[GradeItem] = []
    for qb in question_blobs:
        qid = qb["qid"]
        rq = rubric_by_id.get(qid)
        if rq is None:
            import re
            m = re.search(r"\d+", qid or "")
            if m:
                rq = rubric_by_id.get(f"Q{m.group(0)}")
        if rq is None and rubric:
            rq = rubric[0]
        j = _keyword_score(qb["text"], rq)
        items.append(GradeItem(
            question_id=rq.get("id", qid),
            score=j["score"],
            max_points=float(rq.get("max_points", 0)),
            rationale=j["rationale"],
        ))
    total_max = sum(i.max_points for i in items)
    total_score = sum(i.score for i in items)
    return GradeReport(total_score=total_score, total_max=total_max, items=items)
