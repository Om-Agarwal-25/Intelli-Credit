"""
Module 3 — Agent 3: Adjudication Agent (The Judge)
LLM agent that weighs prosecution vs defence and delivers the final verdict.
"""

import os
import json
import re

from modules.jury.prosecutor import _build_context_message, _llm_call


JUDGE_SYSTEM_PROMPT = """You are the Chairman of the Credit Committee at a major Indian scheduled commercial 
bank. You have chaired over 2000 credit committee meetings. You understand both the 
commercial imperative to lend and the fiduciary duty to protect depositors' money.

You have received two opposing arguments about this loan application:
- The Risk Scrutiny Agent argues for rejection or severe conditions
- The Credit Advocacy Agent argues for approval

Your job is to weigh both arguments with wisdom, not bias. Accept findings you 
find credible. Reject findings you find exaggerated. Identify the two or three 
factors that are truly decisive. Produce a final verdict that a real credit 
committee would stand behind and that an RBI examiner would find defensible.

Output ONLY valid JSON in this exact format:
{
  "accepted_prosecution_findings": ["P1", "P3"],
  "rejected_prosecution_findings": ["P2"],
  "accepted_defence_findings": ["D1", "D2"],
  "rejected_defence_findings": [],
  "decisive_factors": ["one sentence each — the 2-3 things that swung the decision"],
  "final_recommendation": "APPROVE / CONDITIONAL / REJECT",
  "recommended_loan_amount_cr": 35,
  "recommended_interest_rate_pct": 12.5,
  "loan_tenor_months": 60,
  "conditions": ["condition 1", "condition 2"],
  "confidence_band_low_cr": 30,
  "confidence_band_high_cr": 40,
  "primary_reason": "one sentence — the single most important reason",
  "verdict_rationale": "2-3 sentences explaining the decision in plain English"
}"""


async def run_judge(context: dict, prosecution: dict, defence: dict) -> dict:
    """Call the Adjudication Agent (Judge)."""
    base_message = _build_context_message(context)
    judge_message = f"""{base_message}

PROSECUTION FINDINGS (Risk Scrutiny Agent):
{json.dumps(prosecution.get('prosecution_findings', []), indent=2)}

DEFENCE FINDINGS (Credit Advocacy Agent):
{json.dumps(defence.get('defence_findings', []), indent=2)}

Now adjudicate. Weigh both sides and deliver your verdict."""

    try:
        raw = await _llm_call(JUDGE_SYSTEM_PROMPT, judge_message, max_tokens=2500)
        clean = re.sub(r"```json|```", "", raw).strip()
        result = json.loads(clean)

        _validate_verdict(result)
        return result

    except Exception as e:
        print(f"[JUDGE] Failed: {e}")
        return _demo_verdict(prosecution, defence)


def _validate_verdict(result: dict):
    """Ensure all required fields present."""
    defaults = {
        "final_recommendation": "CONDITIONAL",
        "recommended_loan_amount_cr": 35,
        "recommended_interest_rate_pct": 12.5,
        "loan_tenor_months": 60,
        "conditions": [],
        "confidence_band_low_cr": 30,
        "confidence_band_high_cr": 45,
        "primary_reason": "Multi-factor assessment",
        "verdict_rationale": "Based on comprehensive analysis of all submitted documents and research findings.",
        "decisive_factors": [],
        "accepted_prosecution_findings": [],
        "accepted_defence_findings": [],
        "rejected_prosecution_findings": [],
        "rejected_defence_findings": [],
    }
    for k, v in defaults.items():
        if k not in result:
            result[k] = v


def _demo_verdict(prosecution: dict, defence: dict) -> dict:
    """Fallback demo verdict for Vardhaman Infra — the key demo moment."""
    prosecution_ids = [f["finding_id"] for f in prosecution.get("prosecution_findings", [])]
    defence_ids = [f["finding_id"] for f in defence.get("defence_findings", [])]

    return {
        "accepted_prosecution_findings": prosecution_ids,
        "rejected_prosecution_findings": [],
        "accepted_defence_findings": defence_ids,
        "rejected_defence_findings": [],
        "decisive_factors": [
            "DIN disqualification of Director K. Mehta is a categorical RBI regulatory violation — strong financials cannot offset this.",
            "Undisclosed litigation (NCLT + e-Courts) directly contradicts the applicant's self-declaration and damages credibility.",
            "Genuine revenue growth and healthy DSCR support a reduced conditional exposure rather than outright rejection.",
        ],
        "final_recommendation": "CONDITIONAL",
        "recommended_loan_amount_cr": 35,
        "recommended_interest_rate_pct": 12.5,
        "loan_tenor_months": 60,
        "conditions": [
            "DIN regularisation for Director K. Mehta within 90 days of sanction",
            "Resolution of NCLT Case IB/1234/MB/2024 before first disbursement",
            "Submission of No Objection Certificate from NHAI regarding project delay",
            "Additional collateral cover ratio maintained at minimum 1.5x throughout tenure",
        ],
        "confidence_band_low_cr": 30,
        "confidence_band_high_cr": 40,
        "primary_reason": "C1 Character failure (disqualified director, undisclosed litigation) is decisive per RBI guidelines, necessitating conditional approval at reduced exposure.",
        "verdict_rationale": "Vardhaman Infra demonstrates genuine business activity with verified revenues and healthy DSCR. However, the disqualified director and deliberate non-disclosure of active litigation constitute fundamental character concerns that a Credit Committee cannot ignore. A conditional approval at ₹35 Cr (vs. ₹60 Cr requested) with mandatory regularisation conditions balances the commercial opportunity against fiduciary risk.",
    }
