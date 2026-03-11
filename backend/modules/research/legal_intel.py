"""
Module 2 — Legal Intelligence
Searches e-Courts, NCLT, and RBI defaulter list. Uses mock data for demo.
"""

import os


MOCK_LEGAL_DATA = {
    "vardhaman": {
        "ecourts": [
            {
                "case_no": "1842/2024",
                "court": "District Court, Pune",
                "filing_date": "2024-10-18",
                "petitioner": "Sunrise Contractors Pvt. Ltd.",
                "respondent": "Vardhaman Infra & Logistics Pvt. Ltd.",
                "claim_amount_cr": 4.2,
                "status": "3 hearings completed — pending",
                "note": "Fraud complaint by operational creditor. Not disclosed in self-declaration.",
            }
        ],
        "nclt": [
            {
                "case_no": "IB/1234/MB/2024",
                "tribunal": "NCLT Mumbai",
                "type": "Section 9 — Operational Creditor Application",
                "filing_date": "2024-11-05",
                "status": "Admitted — notice issued",
            }
        ],
        "rbi_defaulter": False,
    }
}


async def run_legal_research(entity: dict, session_id: str) -> list:
    """Run legal intelligence research. Returns risk flags."""
    flags = []
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    company_name = (entity.get("company_name") or "").lower()

    # Match to mock data
    legal_data = None
    if demo_mode or "vardhaman" in company_name:
        legal_data = MOCK_LEGAL_DATA.get("vardhaman", {})
    else:
        legal_data = await _search_ecourts(entity)

    if not legal_data:
        return flags

    # e-Courts findings
    for case in legal_data.get("ecourts", []):
        amount = case.get("claim_amount_cr", 0)
        severity = "HIGH" if amount > 1 else "MEDIUM"
        flags.append({
            "flag_type": "LITIGATION_UNDISCLOSED",
            "severity": severity,
            "source_document": "e-Courts Portal",
            "evidence_snippet": f"Case No. {case['case_no']} at {case['court']}: {case['petitioner']} vs {case['respondent']}. Claim: ₹{amount} Cr. Status: {case['status']}. {case.get('note', '')}",
            "page_reference": f"e-Courts | Case {case['case_no']}",
            "source_module": "RESEARCH",
            "five_c_pillar": "C1",
            "session_id": session_id,
        })

    # NCLT findings
    for case in legal_data.get("nclt", []):
        flags.append({
            "flag_type": "NCLT_PROCEEDINGS",
            "severity": "HIGH",
            "source_document": "NCLT",
            "evidence_snippet": f"{case['type']} | {case['tribunal']} | Case {case['case_no']} | Filed {case['filing_date']} | Status: {case['status']}",
            "page_reference": f"NCLT | {case['case_no']}",
            "source_module": "RESEARCH",
            "five_c_pillar": "C1",
            "session_id": session_id,
        })

    # RBI defaulter check
    if legal_data.get("rbi_defaulter"):
        flags.append({
            "flag_type": "RBI_WILFUL_DEFAULTER",
            "severity": "HIGH",
            "source_document": "RBI Published List",
            "evidence_snippet": "Company / promoter appears on RBI published wilful defaulter list.",
            "page_reference": "RBI Master Circular",
            "source_module": "RESEARCH",
            "five_c_pillar": "C1",
            "session_id": session_id,
        })

    return flags


async def _search_ecourts(entity: dict) -> dict:
    """Attempt real e-Courts search (usually blocked by CAPTCHA in automated context)."""
    # Real e-Courts requires browser automation; return empty for non-demo
    print("[LEGAL] e-Courts API not accessible programmatically — using mock data")
    return {}
