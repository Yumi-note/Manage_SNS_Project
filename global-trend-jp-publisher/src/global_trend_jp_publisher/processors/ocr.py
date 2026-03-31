from __future__ import annotations

from io import BytesIO

import requests


def ocr_from_image_url(url: str, timeout: int = 20) -> str:
    # Prefer RapidOCR (no system tesseract binary required).
    try:
        from rapidocr_onnxruntime import RapidOCR
        import cv2
        import numpy as np

        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        arr = np.frombuffer(response.content, np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if image is not None:
            engine = RapidOCR()
            result, _ = engine(image)
            if result:
                text = " ".join([line[1] for line in result if len(line) >= 2])
                text = " ".join(text.split())
                if len(text) >= 30:
                    return text
    except Exception:
        pass

    # Fallback: pytesseract path.
    try:
        from PIL import Image
        import pytesseract
    except Exception:
        return ""

    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
    except Exception:
        return ""

    # Try multilingual OCR first, then fallback to default configuration.
    for lang in ["chi_sim+jpn+eng", "eng"]:
        try:
            text = pytesseract.image_to_string(image, lang=lang)
            if text and len(text.strip()) >= 30:
                return " ".join(text.split())
        except Exception:
            continue
    return ""
