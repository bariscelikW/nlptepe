import argparse, os, json, csv
from src.utils import load_rubric, new_run_dir, ensure_dir
from src.ocr_pipeline import extract_questions
from src.llm_grader import grade_questions
import pandas as pd

def main():
    ap = argparse.ArgumentParser(description="Grade exams with dots.ocr + LLM.")
    ap.add_argument("--input", required=True, help="Path to exam image/PDF or folder of images")
    ap.add_argument("--rubric", required=True, help="Path to rubric JSON")
    ap.add_argument("--outdir", default="outputs", help="Base output directory")
    ap.add_argument("--model", default=None, help="OpenAI model name (overrides OPENAI_MODEL)")
    args = ap.parse_args()

    run_dir = new_run_dir(args.outdir)
    qdir = os.path.join(run_dir, "questions")
    print(f"[i] Writing outputs to: {run_dir}")

    # 1) OCR + split
    qs = extract_questions(args.input, qdir)
    if not qs:
        print("[!] No questions detected. Exiting.")
        return

    # 2) Grade
    rubric = load_rubric(args.rubric)
    report = grade_questions(qs, rubric, model=args.model)

    # 3) Save JSON
    jpath = os.path.join(run_dir, "grades.json")
    with open(jpath, "w", encoding="utf-8") as f:
        f.write(report.model_dump_json(indent=2, ensure_ascii=False))

    # 4) Save CSV
    rows = [{
        "question_id": it.question_id,
        "score": it.score,
        "max_points": it.max_points,
        "rationale": it.rationale,
    } for it in report.items]
    df = pd.DataFrame(rows)
    cpath = os.path.join(run_dir, "grades.csv")
    df.to_csv(cpath, index=False, encoding="utf-8")

    print(f"[✓] Saved: {cpath}")
    print(f"[✓] Saved: {jpath}")
    print(f"[✓] Total: {report.total_score}/{report.total_max}")

if __name__ == "__main__":
    main()
