import re
from typing import List, Dict

QUESTION_PAT = re.compile(r"(?:(?:Soru|Question|Q)\s*(\d+)|\b(\d+)[\)\.])", re.IGNORECASE)

def split_into_questions(full_text: str) -> List[Dict[str, str]]:
    parts = []
    idxs = []
    for m in QUESTION_PAT.finditer(full_text):
        qnum = m.group(1) or m.group(2)
        idxs.append((int(qnum), m.start()))
    if not idxs:
        return [{"qid": "Q1", "text": full_text.strip()}]
    idxs.sort(key=lambda x: x[1])
    for i, (qnum, start) in enumerate(idxs):
        end = idxs[i+1][1] if i+1 < len(idxs) else len(full_text)
        chunk = full_text[start:end].strip()
        parts.append({"qid": f"Q{qnum}", "text": chunk})
    return parts
