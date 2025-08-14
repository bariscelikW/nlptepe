from typing import Dict, Any
class OCRNotAvailable(Exception):
    pass

def _try_import_dots():
    for name in ("dots", "dots.ocr", "dots_ocr", "dotsocr"):
        try:
            mod = __import__(name, fromlist=['*'])
            return mod
        except Exception:
            continue
    return None

def ocr_image(image_path: str) -> Dict[str, Any]:
    dots = _try_import_dots()
    if dots is not None:
        for attr in ("ocr", "recognize", "recognize_image", "run"):
            fn = getattr(getattr(dots, "ocr", dots), attr, None) if hasattr(dots, "ocr") else getattr(dots, attr, None)
            if callable(fn):
                try:
                    res = fn(image_path)
                    if isinstance(res, str):
                        return {"text": res, "blocks": []}
                    if isinstance(res, dict):
                        text = res.get("text") or res.get("full_text") or ""
                        blocks = res.get("blocks") or []
                        return {"text": text, "blocks": blocks}
                except Exception:
                    pass
    try:
        from PIL import Image
        import pytesseract
        img = Image.open(image_path).convert("L")
        txt = pytesseract.image_to_string(img)
        return {"text": txt, "blocks": []}
    except Exception as e:
        raise OCRNotAvailable(f"OCR failed for {image_path}: {e}") from e
