"""
Thin adapter around dots.ocr with graceful fallback to pytesseract.
"""
from typing import List, Dict, Any, Optional
import os

class OCRNotAvailable(Exception):
    pass

def _try_import_dots():
    # Try common import patterns
    for name in ("dots", "dots.ocr", "dots_ocr", "dotsocr"):
        try:
            mod = __import__(name, fromlist=['*'])
            return mod
        except Exception:
            continue
    return None

def ocr_image(image_path: str) -> Dict[str, Any]:
    """
    Returns:
        {
          "text": "full text",
          "blocks": [{"text": "...", "bbox": [x,y,w,h]} ...]
        }
    """
    dots = _try_import_dots()
    if dots is not None:
        # Very generic usage to avoid tight coupling.
        # Expect that dots.ocr exposes a callable `recognize(image_path)` or similar.
        # We try a few common names reflectively.
        for attr in ("ocr", "recognize", "recognize_image", "run"):
            fn = getattr(getattr(dots, "ocr", dots), attr, None) if hasattr(dots, "ocr") else getattr(dots, attr, None)
            if callable(fn):
                try:
                    res = fn(image_path)  # expected to return text or structured result
                    if isinstance(res, str):
                        return {"text": res, "blocks": []}
                    # Try to coerce to our schema
                    if isinstance(res, dict):
                        text = res.get("text") or res.get("full_text") or ""
                        blocks = res.get("blocks") or []
                        return {"text": text, "blocks": blocks}
                except Exception:
                    pass

    # Fallback to pytesseract
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(image_path).convert("L")
        txt = pytesseract.image_to_string(img)
        return {"text": txt, "blocks": []}
    except Exception as e:
        raise OCRNotAvailable(f"OCR backends failed for {image_path}: {e}") from e
