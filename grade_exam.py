import argparse, os
from src.utils import load_rubric, new_run_dir
from src.ocr_pipeline import extract_questions
from src.llm_grader import grade_questions
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description="Grade exams with dots.ocr + offline keyword scoring.")
    ap.add_argument("--input", required=True, help="Path to exam image/PDF or folder of images")
    ap.add_argument("--rubric", required=True, help="Path to rubric JSON")
    ap.add_argument("--outdir", default="outputs", help="Base output directory")
    args = ap.parse_args()

    run_dir = new_run_dir(args.outdir)
    qdir = os.path.join(run_dir, "questions")
    print(f"[i] Writing outputs to: {run_dir}")

    qs = extract_questions(args.input, qdir)
    if not qs:
        print("[!] No questions detected.")
        return

    rubric = load_rubric(args.rubric)
    report = grade_questions(qs, rubric)

    import json
    with open(os.path.join(run_dir, "grades.json"), "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2, ensure_ascii=False))

    rows = [{
        "question_id": it.question_id,
        "score": it.score,
        "max_points": it.max_points,
        "rationale": it.rationale,
    } for it in report.items]
    pd.DataFrame(rows).to_csv(os.path.join(run_dir, "grades.csv"), index=False, encoding="utf-8")
    print(f"[✓] Done. Total score: {report.total_score}/{report.total_max}")

if __name__ == "__main__":
    main()
