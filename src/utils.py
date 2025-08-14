import os, re, uuid, time, json, pathlib
from typing import List, Dict, Any

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def load_rubric(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def new_run_dir(base_outdir: str) -> str:
    rid = time.strftime("%Y%m%d-%H%M%S")
    full = os.path.join(base_outdir, rid)
    ensure_dir(full)
    ensure_dir(os.path.join(full, "questions"))
    return full

def guess_lang(text: str) -> str:
    if re.search(r"[çğıöşüÇĞİÖŞÜ]", text):
        return "tr"
    return "en"
