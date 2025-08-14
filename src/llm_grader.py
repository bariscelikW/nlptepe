from typing import List, Dict, Any
import os, json
from pydantic import BaseModel, Field
from .utils import guess_lang

class GradeItem(BaseModel):
    question_id: str
    score: float
    max_points: float
    rationale: str

class GradeReport(BaseModel):
    total_score: float
    total_max: float
    items: List[GradeItem] = Field(default_factory=list)

def _build_prompt(question_text: str, rubric_q: Dict[str, Any]) -> str:
    lang = guess_lang(question_text + " " + " ".join(rubric_q.get("criteria", [])))
    preface = "Sen bir hoca gibi puanlama yapan yardımcısın." if lang == "tr" else "You are a teaching assistant grading with a rubric."
    return f"""{preface}

Rubric:
- Question ID: {rubric_q.get('id')}
- Title: {rubric_q.get('title')}
- Max Points: {rubric_q.get('max_points')}
- Criteria:
{chr(10).join(f"- {c}" for c in rubric_q.get('criteria', []))}

Student answer:
\"\"\"
{question_text.strip()}
\"\"\"

Return STRICT JSON with fields: score (number 0..max), rationale (concise 1-3 sentences).
"""

def _call_openai(prompt: str, model: str) -> Dict[str, Any]:
    # Supports Responses API (>=1.0)
    from openai import OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    client = OpenAI(api_key=api_key, base_url=base_url or None)
    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "Return only JSON. No prose."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )
    content = resp.output_text
    try:
        return json.loads(content)
    except Exception:
        # last resort: try to extract JSON
        import re
        m = re.search(r"\{.*\}", content, re.S)
        return json.loads(m.group(0)) if m else {"score": 0, "rationale": "Parse error."}

def grade_questions(question_blobs: List[Dict[str, str]], rubric: List[Dict[str, Any]], model: str) -> GradeReport:
    rubric_by_id = {q["id"]: q for q in rubric}
    items: List[GradeItem] = []
    for qb in question_blobs:
        qid = qb["qid"]
        # find closest rubric entry (exact match or fallback by number)
        rq = rubric_by_id.get(qid)
        if rq is None:
            # try by numeric part
            import re
            m = re.search(r"\d+", qid or "")
            if m:
                rq = rubric_by_id.get(f"Q{m.group(0)}")
        if rq is None and rubric:
            # fallback to first for demos
            rq = rubric[0]
        prompt = _build_prompt(qb["text"], rq)
        model_name = model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        j = _call_openai(prompt, model=model_name)
        score = float(max(0, min(j.get("score", 0), rq.get("max_points", 0))))
        items.append(GradeItem(
            question_id=rq.get("id", qid),
            score=score,
            max_points=float(rq.get("max_points", 0)),
            rationale=j.get("rationale", ""),
        ))
    total_max = sum(i.max_points for i in items)
    total_score = sum(i.score for i in items)
    return GradeReport(total_score=total_score, total_max=total_max, items=items)
