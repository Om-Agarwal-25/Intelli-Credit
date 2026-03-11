"""
Module 1 — Text Extractor
Handles three document types:
  1. Clean digital PDFs → PyMuPDF
  2. Scanned/image PDFs → EasyOCR
  3. Complex table PDFs → Camelot
"""

import os
from pathlib import Path
from typing import Optional


def extract_text(pdf_path: str) -> str:
    """Main extraction entry point with fallback chain."""
    text = _extract_pymupdf(pdf_path)

    # If very little text extracted, assume scanned → OCR
    if len(text.strip()) < 100:
        print(f"[EXTRACTOR] Low text from PyMuPDF ({len(text)} chars), trying OCR...")
        ocr_text = _extract_easyocr(pdf_path)
        if ocr_text and len(ocr_text) > len(text):
            text = ocr_text

    return text


def _extract_pymupdf(pdf_path: str) -> str:
    """Fast digital PDF extraction using PyMuPDF (fitz)."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages = []
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():
                pages.append(f"[PAGE {page_num + 1}]\n{page_text}")
        doc.close()
        return "\n\n".join(pages)
    except Exception as e:
        print(f"[EXTRACTOR] PyMuPDF failed for {pdf_path}: {e}")
        return ""


def _extract_easyocr(pdf_path: str) -> str:
    """OCR extraction for scanned PDFs using EasyOCR."""
    try:
        import easyocr
        import fitz
        import numpy as np
        from PIL import Image
        import io

        reader = easyocr.Reader(["en", "hi"], gpu=False)
        doc = fitz.open(pdf_path)
        all_text = []

        for page_num, page in enumerate(doc):
            # Render page to image
            mat = fitz.Matrix(2.0, 2.0)  # 2x scale for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_bytes))
            img_array = np.array(img)

            results = reader.readtext(img_array, detail=0)
            page_text = " ".join(results)
            if page_text.strip():
                all_text.append(f"[PAGE {page_num + 1} — OCR]\n{page_text}")

        doc.close()
        return "\n\n".join(all_text)

    except ImportError:
        print("[EXTRACTOR] EasyOCR not installed. Run: pip install easyocr")
        return ""
    except Exception as e:
        print(f"[EXTRACTOR] EasyOCR failed: {e}")
        return ""


def extract_tables_camelot(pdf_path: str) -> list:
    """Extract tables from PDFs using Camelot (for GST schedules, P&L)."""
    try:
        import camelot

        # Try lattice first (bordered tables), fall back to stream
        try:
            tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
        except Exception:
            tables = camelot.read_pdf(pdf_path, pages="all", flavor="stream")

        result = []
        for t in tables:
            df = t.df
            result.append(df.to_dict(orient="records"))
        return result

    except ImportError:
        print("[EXTRACTOR] Camelot not installed. Run: pip install camelot-py[cv]")
        return []
    except Exception as e:
        print(f"[EXTRACTOR] Camelot failed: {e}")
        return []


def extract_all(pdf_path: str) -> dict:
    """Comprehensive extraction returning text + tables."""
    return {
        "text": extract_text(pdf_path),
        "tables": extract_tables_camelot(pdf_path),
        "path": pdf_path,
    }
