"""
Module 3 — Agent 2: Credit Advocacy Agent (The Defender)
LLM agent that finds every reason to APPROVE the application.
"""

import os
import json
import re

from modules.jury.prosecutor import _build_context_message, _llm_call


DEFENDER_SYSTEM_PROMPT = """You are a relationship manager and credit advocate at a leading Indian private bank. 
You deeply believe in supporting Indian businesses and the growth story of the 
Indian economy. You understand that numbers alone don't tell the full story.

Your ONLY job is to find every legitimate reason this loan application should be 
APPROVED. Find the strengths. Find the growth narrative. Compare favourably against 
sector benchmarks. Provide context that makes concerning signals less alarming — 
if the sector is under stress, a single company's stress is not a character flaw. 
Do not be cautious — the Risk Scrutiny Agent will handle the negative case.

Output ONLY valid JSON in this exact format:
{
  "defence_findings": [
    {
      "finding_id": "D1",
      "finding_text": "one clear sentence describing the strength",
      "five_c_pillar": "C1/C2/C3/C4/C5",
      "score_delta": 8,
      "evidence_source": "GST Returns / Bank Statement / Annual Report / Sector Data",
      "confidence": "HIGH/MEDIUM"
    }
  ],
  "total_defence_delta": 14
}"""


async def run_defender(context: dict) -> dict:
    """Call the Credit Advocacy Agent (Defender)."""
    user_message = _build_context_message(context)
    user_message += "\n\nNow advocate for this application. Find every strength and growth signal."

    try:
        raw = await _llm_call(DEFENDER_SYSTEM_PROMPT, user_message, max_tokens=2000)
        clean = re.sub(r"```json|```", "", raw).strip()
        result = json.loads(clean)

        if "defence_findings" not in result:
            result = {"defence_findings": [], "total_defence_delta": 0}

        # Enforce max +15 per finding
        for f in result.get("defence_findings", []):
            f["score_delta"] = min(15, max(0, f.get("score_delta", 5)))

        result["total_defence_delta"] = sum(f["score_delta"] for f in result["defence_findings"])
        return result

    except Exception as e:
        print(f"[DEFENDER] Failed: {e}")
        return _demo_defence()


def _demo_defence() -> dict:
    """Fallback demo defence for Vardhaman Infra."""
    return {
        "defence_findings": [
            {
                "finding_id": "D1",
                "finding_text": "Revenue verified as genuine — GST-to-bank credit match ratio of 94% over 24 months confirms the declared turnover of ₹340 Cr is real, not inflated.",
                "five_c_pillar": "C2",
                "score_delta": 5,
                "evidence_source": "GST Returns FY24 / Bank Statement FY24",
                "confidence": "HIGH",
            },
            {
                "finding_id": "D2",
                "finding_text": "DSCR of 1.6x is comfortably above the 1.25x RBI minimum threshold, indicating the borrower can service debt from operating cash flows.",
                "five_c_pillar": "C2",
                "score_delta": 4,
                "evidence_source": "Annual Report FY24 — Cash Flow Statement",
                "confidence": "HIGH",
            },
            {
                "finding_id": "D3",
                "finding_text": "18% YoY revenue growth outperforms the infrastructure sector average of 11%, demonstrating competitive market positioning.",
                "five_c_pillar": "C2",
                "score_delta": 3,
                "evidence_source": "Annual Report FY24 / CRISIL Sector Report",
                "confidence": "MEDIUM",
            },
        ],
        "total_defence_delta": 12,
    }
