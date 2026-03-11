"""
Module 3 — Jury Engine
Orchestrates all three agents: Prosecutor → Defender → Judge → Final Score.
"""

import asyncio
from typing import Optional


async def run_jury_deliberation(
    session_id: str,
    five_cs: dict,
    base_score: float,
    risk_flags: list,
    research_flags: list,
    qualitative: dict,
) -> dict:
    """Orchestrate the full AI Agent Jury deliberation."""

    context = {
        "session_id": session_id,
        "five_cs": five_cs,
        "base_score": base_score,
        "risk_flags": risk_flags,
        "research_flags": research_flags,
        "qualitative": qualitative,
    }

    # Run prosecutor and defender in parallel for speed
    from modules.jury.prosecutor import run_prosecutor
    from modules.jury.defender import run_defender

    prosecution, defence = await asyncio.gather(
        run_prosecutor(context),
        run_defender(context),
    )

    # Judge deliberates with both arguments
    from modules.jury.judge import run_judge
    verdict = await run_judge(context, prosecution, defence)

    # Calculate final jury score
    accepted_p_ids = set(verdict.get("accepted_prosecution_findings", []))
    accepted_d_ids = set(verdict.get("accepted_defence_findings", []))

    prose_findings = prosecution.get("prosecution_findings", [])
    def_findings = defence.get("defence_findings", [])

    prosecution_delta = sum(
        f["score_delta"] for f in prose_findings if f["finding_id"] in accepted_p_ids
    )
    defence_delta = sum(
        f["score_delta"] for f in def_findings if f["finding_id"] in accepted_d_ids
    )
    qualitative_delta = qualitative.get("total_score_delta", 0)

    # Cap net delta at ±30
    net_delta = max(-30, min(30, prosecution_delta + defence_delta + qualitative_delta))
    jury_score = round(max(0, min(100, base_score + net_delta)), 1)

    # Decision thresholds
    if jury_score >= 65:
        jury_decision = "APPROVE"
    elif jury_score >= 50:
        jury_decision = "CONDITIONAL"
    else:
        jury_decision = "REJECT"

    return {
        "base_score": round(base_score, 1),
        "jury_score": jury_score,
        "net_delta": round(net_delta, 1),
        "prosecution_delta": prosecution_delta,
        "defence_delta": defence_delta,
        "qualitative_delta": qualitative_delta,
        "jury_decision": jury_decision,
        "five_cs": five_cs,
        "prosecution": prosecution,
        "defence": defence,
        "verdict": verdict,
        "final_recommendation": verdict.get("final_recommendation", jury_decision),
        "recommended_loan_amount_cr": verdict.get("recommended_loan_amount_cr", 35),
        "recommended_interest_rate_pct": verdict.get("recommended_interest_rate_pct", 12.5),
        "loan_tenor_months": verdict.get("loan_tenor_months", 60),
        "conditions": verdict.get("conditions", []),
        "confidence_band": {
            "low": verdict.get("confidence_band_low_cr"),
            "high": verdict.get("confidence_band_high_cr"),
        },
        "primary_reason": verdict.get("primary_reason", ""),
        "verdict_rationale": verdict.get("verdict_rationale", ""),
        "decisive_factors": verdict.get("decisive_factors", []),
    }
