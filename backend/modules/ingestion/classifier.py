"""
Module 1 — LLM Document Classifier
Sends first-page text to Claude/GPT to classify into one of 7 categories.
Also handles LLM parsing of qualitative officer input.
"""

import os
import json
import re
from typing import Optional

VALID_CATEGORIES = ["GST_RETURN", "BANK_STATEMENT", "ANNUAL_REPORT", "LEGAL_DOC", "ITR", "RATING_REPORT", "OTHER"]


def _get_llm_client():
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    if provider == "anthropic":
        import anthropic
        return "anthropic", anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    else:
        import openai
        return "openai", openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def classify_document(pdf_path: str) -> str:
    """Classify a PDF document into one of 7 categories."""
    filename = os.path.basename(pdf_path)

    # Fast rule-based check on filename first
    rule_result = _rule_based_classify("", filename)
    if rule_result != "OTHER":
        return rule_result

    # Extract first page text
    first_page_text = _extract_first_page(pdf_path)

    if not first_page_text.strip():
        return "OTHER"

    # Demo mode or no API keys — use rule-based on text content
    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    api_key = os.getenv("ANTHROPIC_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if demo_mode or not api_key or api_key.startswith("test-key"):
        return _rule_based_classify(first_page_text, filename)

    prompt = f"""Classify this document into exactly one of these categories based on the text:
GST_RETURN, BANK_STATEMENT, ANNUAL_REPORT, LEGAL_DOC, ITR, RATING_REPORT, OTHER

Return only the category label, nothing else.

Document text (first page):
{first_page_text[:2000]}"""

    try:
        provider, client = _get_llm_client()
        if provider == "anthropic":
            fast_model = os.getenv("FAST_MODEL", "claude-haiku-4-20250514")
            resp = client.messages.create(
                model=fast_model,
                max_tokens=20,
                messages=[{"role": "user", "content": prompt}]
            )
            label = resp.content[0].text.strip().upper()
        else:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=20,
                messages=[{"role": "user", "content": prompt}]
            )
            label = resp.choices[0].message.content.strip().upper()

        # Validate
        for cat in VALID_CATEGORIES:
            if cat in label:
                return cat
        return "OTHER"

    except Exception as e:
        print(f"[CLASSIFIER] LLM call failed: {e}. Falling back to rule-based.")
        return _rule_based_classify(first_page_text, filename)


def _extract_first_page(pdf_path: str) -> str:
    """Extract text from first page using PyMuPDF."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        if len(doc) == 0:
            return ""
        text = doc[0].get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"[CLASSIFIER] PyMuPDF failed: {e}")
        return ""


def _rule_based_classify(text: str, filename: str = "") -> str:
    """Keyword-based fallback classification. Checks filename first, then text content."""
    fn = filename.lower()
    # Filename-based fast classification
    if any(k in fn for k in ["gstr", "gst_ret", "gstin"]):
        return "GST_RETURN"
    if any(k in fn for k in ["bank", "statement", "sbi", "hdfc", "icici", "axis"]):
        return "BANK_STATEMENT"
    if any(k in fn for k in ["annual_report", "annual report", "ar_20", "ar_fy", "fy24", "fy23", "balance_sheet"]):
        return "ANNUAL_REPORT"
    if any(k in fn for k in ["itr", "income_tax", "income tax", "tax_return"]):
        return "ITR"
    if any(k in fn for k in ["legal", "court", "nclt", "ecourt"]):
        return "LEGAL_DOC"
    if any(k in fn for k in ["rating", "crisil", "icra", "care"]):
        return "RATING_REPORT"

    # Text content fallback
    text_lower = text.lower()
    if any(k in text_lower for k in ["gstr", "gstin", "goods and services tax", "gst return", "taxable outward"]):
        return "GST_RETURN"
    if any(k in text_lower for k in ["bank statement", "account statement", "current account", "savings account", "debit", "credit", "balance brought"]):
        return "BANK_STATEMENT"
    if any(k in text_lower for k in ["annual report", "board of directors", "chairman's message", "auditor", "balance sheet", "profit and loss"]):
        return "ANNUAL_REPORT"
    if any(k in text_lower for k in ["income tax return", "itr", "assessment year", "tax payable"]):
        return "ITR"
    if any(k in text_lower for k in ["legal notice", "court", "plaintiff", "defendant", "petition", "writ"]):
        return "LEGAL_DOC"
    if any(k in text_lower for k in ["credit rating", "rated", "outlook", "crisil", "icra", "care", "fitch"]):
        return "RATING_REPORT"
    return "OTHER"


async def parse_qualitative_input(text: str) -> list:
    """Parse free-text qualitative observation into credit risk adjustments."""
    if not text.strip():
        return []

    demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
    api_key = os.getenv("ANTHROPIC_API_KEY", "") or os.getenv("OPENAI_API_KEY", "")
    if demo_mode or not api_key or api_key.startswith("test-key"):
        return _demo_qualitative_parse(text)

    prompt = f"""You are a credit risk system. Parse this site visit observation and map it to credit risk adjustments.
Observation: "{text}"
Output JSON array: [{{"observation": "...", "five_c_pillar": "C1/C2/C3/C4/C5", "score_delta": <number between -15 and 15>, "reasoning": "one sentence"}}]
Return only valid JSON array, no other text."""

    try:
        provider, client = _get_llm_client()
        if provider == "anthropic":
            fast_model = os.getenv("FAST_MODEL", "claude-haiku-4-20250514")
            resp = client.messages.create(
                model=fast_model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = resp.content[0].text.strip()
        else:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = resp.choices[0].message.content.strip()

        # Parse JSON
        raw = re.sub(r"```json|```", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        print(f"[CLASSIFIER] Qualitative parsing failed: {e}")
        return _demo_qualitative_parse(text)


def _demo_qualitative_parse(text: str) -> list:
    """Heuristic qualitative parsing without LLM, for demo/test mode."""
    adjustments = []
    text_lower = text.lower()

    if any(k in text_lower for k in ["idle", "low utilisation", "below capacity", "70%", "underutil"]):
        adjustments.append({"observation": "Capacity below optimal", "five_c_pillar": "C2", "score_delta": -5, "reasoning": "Factory utilisation below 80% indicates underperformance."})
    if any(k in text_lower for k in ["absent", "evasive", "uncooperative", "concerned"]):
        adjustments.append({"observation": "Management availability risk", "five_c_pillar": "C1", "score_delta": -5, "reasoning": "Director absent from meeting raises governance concerns."})
    if any(k in text_lower for k in ["strong", "confident", "transparent", "positive"]):
        adjustments.append({"observation": "Positive management interaction", "five_c_pillar": "C1", "score_delta": 4, "reasoning": "Management engagement quality is a positive character signal."})
    return adjustments

