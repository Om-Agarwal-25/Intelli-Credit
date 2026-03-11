"""
Module 3 — Agent 1: Risk Scrutiny Agent (The Prosecutor)
Adversarial LLM agent that finds every reason to REJECT the application.
"""

import os
import json
import re


PROSECUTOR_SYSTEM_PROMPT = """You are an adversarial senior credit risk officer with 20 years of experience 
investigating Indian corporate fraud. You have personally reviewed the NPA files 
of ABG Shipyard, DHFL, IL&FS, Videocon, and Kingfisher Airlines. You know every 
pattern fraudsters use — related party diversion, circular trading, pre-loan cash 
stuffing, nominee directors hiding DIN disqualification, inflated receivables.

Your ONLY job is to find every possible reason this loan application should be 
REJECTED. Assume the borrower is hiding something until proven otherwise. Be 
aggressive. Surface contradictions between data sources. Find the worst-case 
scenario. Do not be fair — the Defender Agent will handle the positive case.

Output ONLY valid JSON in this exact format:
{
  "prosecution_findings": [
    {
      "finding_id": "P1",
      "finding_text": "one clear sentence describing the risk",
      "five_c_pillar": "C1/C2/C3/C4/C5",
      "score_delta": -12,
      "evidence_source": "MCA21 / e-Courts / GSTR-2A / Annual Report p.34 / etc",
      "severity": "HIGH/MEDIUM"
    }
  ],
  "total_prosecution_delta": -27
}"""


async def run_prosecutor(context: dict) -> dict:
    """Call the Risk Scrutiny Agent (Prosecutor)."""
    user_message = _build_context_message(context)

    try:
        raw = await _llm_call(PROSECUTOR_SYSTEM_PROMPT, user_message, max_tokens=2000)
        clean = re.sub(r"```json|```", "", raw).strip()
        result = json.loads(clean)

        # Validate structure
        if "prosecution_findings" not in result:
            result = {"prosecution_findings": [], "total_prosecution_delta": 0}

        # Enforce max -20 per finding
        for f in result.get("prosecution_findings", []):
            f["score_delta"] = max(-20, min(0, f.get("score_delta", -5)))

        result["total_prosecution_delta"] = sum(f["score_delta"] for f in result["prosecution_findings"])
        return result

    except Exception as e:
        print(f"[PROSECUTOR] Failed: {e}")
        return _demo_prosecution()


def _build_context_message(ctx: dict) -> str:
    five_cs = ctx.get("five_cs", {})
    flags = ctx.get("risk_flags", [])[:20]  # top 20 flags
    research = ctx.get("research_flags", [])[:10]
    qualitative = ctx.get("qualitative", {})

    flags_text = "\n".join(
        f"  [{f.get('severity')}] {f.get('flag_type')}: {f.get('evidence_snippet', '')[:200]}"
        for f in flags
    )
    research_text = "\n".join(
        f"  [{r.get('severity')}] {r.get('flag_type')}: {r.get('evidence_snippet', '')[:200]}"
        for r in research
    )

    return f"""LOAN APPLICATION CONTEXT:

FIVE CS SCORES:
C1 Character: {five_cs.get('C1', '?')}/100
C2 Capacity: {five_cs.get('C2', '?')}/100  
C3 Capital: {five_cs.get('C3', '?')}/100
C4 Collateral: {five_cs.get('C4', '?')}/100
C5 Conditions: {five_cs.get('C5', '?')}/100
Composite (Base): {five_cs.get('composite', '?')}/100

RISK FLAGS FROM STRUCTURED ANALYSIS:
{flags_text or 'None'}

RESEARCH INTELLIGENCE FLAGS:
{research_text or 'None'}

QUALITATIVE INPUTS:
Factory Utilisation: {qualitative.get('factory_utilisation', 'N/A')}%
Management Impression: {qualitative.get('management_impression', 'N/A')}
Promoter Reputation: {qualitative.get('promoter_reputation', 'N/A')}
Site Visit Notes: {qualitative.get('site_visit_notes', 'N/A')}

Now prosecute this application aggressively. Find every risk."""


async def _llm_call(system: str, message: str, max_tokens: int = 2000) -> str:
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    primary_model = os.getenv("PRIMARY_MODEL", "claude-sonnet-4-20250514")

    if provider == "anthropic":
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        resp = client.messages.create(
            model=primary_model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": message}],
        )
        return resp.content[0].text
    else:
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o",
            max_tokens=max_tokens,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": message}],
        )
        return resp.choices[0].message.content


def _demo_prosecution() -> dict:
    """Fallback demo prosecution for Vardhaman Infra."""
    return {
        "prosecution_findings": [
            {
                "finding_id": "P1",
                "finding_text": "Director K. Mehta (DIN 07284531) is disqualified under Section 164(2) Companies Act since September 2023 — company is operating under a nominee director, constituting a regulatory violation that the applicant did not disclose.",
                "five_c_pillar": "C1",
                "score_delta": -15,
                "evidence_source": "MCA21 · DIN 07284531",
                "severity": "HIGH",
            },
            {
                "finding_id": "P2",
                "finding_text": "Active NCLT petition (IB/1234/MB/2024) and undisclosed e-Courts litigation (Case 1842/2024) directly contradict the self-declaration of 'no pending litigation' — indicating deliberate concealment.",
                "five_c_pillar": "C1",
                "score_delta": -12,
                "evidence_source": "e-Courts District Court Pune · NCLT Mumbai",
                "severity": "HIGH",
            },
            {
                "finding_id": "P3",
                "finding_text": "Going-concern qualification buried on page 34 of the annual report combined with the contingent liability of ₹8.4 Cr creates significant doubt about financial sustainability of the borrower.",
                "five_c_pillar": "C2",
                "score_delta": -8,
                "evidence_source": "Annual Report FY24 · Note 31",
                "severity": "MEDIUM",
            },
        ],
        "total_prosecution_delta": -35,
    }
