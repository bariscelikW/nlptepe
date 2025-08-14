# dotsocr-exam-grader

End-to-end demo repository to **grade hand-written exams quickly** using **dots.ocr** for OCR and an **LLM** for rubric-driven scoring.

> ⚡ Built for fast submission: drop your scanned exam images/PDFs into `examples/sample_exam/`, provide a rubric (JSON), set your OpenAI key, and run one command.

---

## Features
- Uses **dots.ocr** (if available) with graceful fallback to `pytesseract`.
- Splits long pages into **per-question** text using regex heuristics (customizable).
- **LLM grading** with a structured rubric (per-question criteria and max points).
- Saves **CSV** and **JSON** with scores and rationales; also writes **per-question text** for auditing.
- Lightweight CLI, no frameworks.

## Quickstart

### 1) Install
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> If `dots-ocr` isn't available on your machine, the pipeline will automatically fallback to `pytesseract`.

### 2) Put inputs
- Place exam scans into: `examples/sample_exam/` (PNG/JPG/PDF).
- Prepare a rubric JSON (see `config/example_rubric.json`).

### 3) Set your LLM key
```bash
export OPENAI_API_KEY=YOUR_KEY_HERE   # Windows PowerShell: $env:OPENAI_API_KEY="YOUR_KEY_HERE"
```

### 4) Run
```bash
python grade_exam.py   --input examples/sample_exam   --rubric config/example_rubric.json   --outdir outputs
```

Outputs:
- `outputs/<run_id>/grades.csv`
- `outputs/<run_id>/grades.json`
- `outputs/<run_id>/questions/` (per-question extracted text)

## Rubric format
A simple list of questions with `id`, `title`, `max_points`, and natural-language `criteria`.

See: [`config/example_rubric.json`](config/example_rubric.json)

## Question detection
By default, we look for headings like `1)`, `2.`, `Q1`, `Soru 1`, etc. via a regex.
You can tweak the regex in `src/split_questions.py`.

## Notes
- This is a **reference demo**. In production, add authentication, better document segmentation, and evaluation.
- OCR quality strongly impacts grading. Ensure scans are sharp (300dpi+), high contrast, well-lit.
- **Privacy:** keep data local; do not upload student data to public repos.

## License
MIT
