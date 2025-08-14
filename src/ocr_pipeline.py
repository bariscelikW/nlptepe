import os, glob
from typing import List, Dict
from pdf2image import convert_from_path
from .dots_ocr_adapter import ocr_image
from .split_questions import split_into_questions
from .utils import ensure_dir

SUPPORTED = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".pdf")

def _iter_images(input_path: str) -> List[str]:
    paths: List[str] = []
    if os.path.isdir(input_path):
        for ext in SUPPORTED:
            paths.extend(glob.glob(os.path.join(input_path, f"*{ext}")))
    elif os.path.isfile(input_path) and input_path.lower().endswith(".pdf"):
        tmp = os.path.join(input_path + "_pages")
        ensure_dir(tmp)
        pages = convert_from_path(input_path, dpi=200)
        out = []
        for i, img in enumerate(pages):
            p = os.path.join(tmp, f"page_{i+1:03d}.png")
            img.save(p)
            out.append(p)
        return out
    elif os.path.isfile(input_path):
        paths.append(input_path)
    return sorted(paths)

def extract_questions(input_path: str, out_questions_dir: str) -> List[Dict[str, str]]:
    ensure_dir(out_questions_dir)
    all_qs: List[Dict[str, str]] = []
    for img_path in _iter_images(input_path):
        res = ocr_image(img_path)
        text = res.get("text", "")
        qs = split_into_questions(text)
        for q in qs:
            qid = q["qid"]
            fname = f"{qid}_{os.path.basename(img_path)}.txt"
            with open(os.path.join(out_questions_dir, fname), "w", encoding="utf-8") as f:
                f.write(q["text"])
        all_qs.extend(qs)
    return all_qs
