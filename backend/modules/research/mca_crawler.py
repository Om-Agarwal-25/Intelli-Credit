"""
Module 2 — MCA21 Crawler
Queries MCA company/director APIs. Falls back to mock data for demo.
"""

import os
import asyncio
import httpx
from typing import Optional


# Pre-loaded mock data for demo company (Vardhaman Infra)
MOCK_MCA_DATA = {
    "U45200MH2015PTC264831": {
        "company_name": "VARDHAMAN INFRA & LOGISTICS PVT. LTD.",
        "cin": "U45200MH2015PTC264831",
        "status": "Active",
        "date_of_incorporation": "2015-03-15",
        "registered_address": "204, Apex Business Park, Pune, Maharashtra 411014",
        "directors": [
            {"name": "Rajesh Kumar Vardhaman", "din": "06284530", "status": "Active"},
            {"name": "Kavita Mehta", "din": "07284531", "status": "Disqualified", "disqualification_reason": "Section 164(2) - Non-filing of financial statements for 3 years (2020-2023)"},
        ],
        "charges": [
            {"charge_id": "CHG-2019-12345", "holder": "State Bank of India", "amount_cr": 15, "status": "Satisfied"},
            {"charge_id": "CHG-2022-67891", "holder": "Axis Bank Ltd", "amount_cr": 20, "status": "Active", "note": "NOT DISCLOSED in submitted documents"},
        ],
        "associated_companies": [
            {"name": "Vardhaman Buildcon Pvt. Ltd.", "cin": "U45200MH2014PTC253421", "status": "Struck Off", "reason": "Non-filing"},
            {"name": "Vardhaman Holdings LLP", "cin": "AAA-2345", "status": "Struck Off", "reason": "Non-filing"},
        ],
    }
}

MOCK_DISQUALIFIED_DINS = {"07284531"}  # K. Mehta


async def run_mca_research(entity: dict, session_id: str) -> list:
    """Run MCA21 research. Uses mock data if API unavailable (demo mode)."""
    flags = []
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"

    cin = entity.get("cin") or "U45200MH2015PTC264831"  # Default to demo company
    company_name = entity.get("company_name", "Unknown")

    if demo_mode:
        company_data = MOCK_MCA_DATA.get(cin, list(MOCK_MCA_DATA.values())[0])
    else:
        company_data = await _fetch_mca_company(cin)
        if not company_data:
            company_data = MOCK_MCA_DATA.get(cin, {})

    if not company_data:
        return flags

    # Check director disqualifications
    for director in company_data.get("directors", []):
        din = director.get("din", "")
        disq_reason = director.get("disqualification_reason", "")

        if director.get("status") == "Disqualified" or din in MOCK_DISQUALIFIED_DINS:
            flags.append({
                "flag_type": "DIN_DISQUALIFIED",
                "severity": "HIGH",
                "source_document": "MCA21",
                "evidence_snippet": f"Director {director['name']} (DIN {din}): {disq_reason or 'Disqualified under Section 164(2) Companies Act'}. Company running under nominee director — regulatory violation.",
                "page_reference": f"MCA21 DIN {din}",
                "source_module": "RESEARCH",
                "five_c_pillar": "C1",
                "session_id": session_id,
            })

    # Check undisclosed charges
    for charge in company_data.get("charges", []):
        if "NOT DISCLOSED" in charge.get("note", ""):
            flags.append({
                "flag_type": "UNDISCLOSED_CHARGE",
                "severity": "HIGH",
                "source_document": "MCA21",
                "evidence_snippet": f"Registered charge {charge['charge_id']} in favour of {charge['holder']} for ₹{charge['amount_cr']} Cr ({charge['status']}) not disclosed in submitted documents.",
                "page_reference": f"MCA21 Charge Registry — {charge['charge_id']}",
                "source_module": "RESEARCH",
                "five_c_pillar": "C4",
                "session_id": session_id,
            })

    # Check associated struck-off entities
    struck_off = [c for c in company_data.get("associated_companies", []) if c.get("status") == "Struck Off"]
    if struck_off:
        names = ", ".join(c["name"] for c in struck_off)
        flags.append({
            "flag_type": "PROMOTER_NETWORK_RISK",
            "severity": "MEDIUM",
            "source_document": "MCA21",
            "evidence_snippet": f"{len(struck_off)} associated companies under same directors are struck off: {names}. Capital diversion risk.",
            "page_reference": "MCA21 Director Network",
            "source_module": "RESEARCH",
            "five_c_pillar": "C1",
            "session_id": session_id,
        })

    return flags


async def _fetch_mca_company(cin: str) -> Optional[dict]:
    """Try to call real MCA API."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://www.mca.gov.in/MCAGateway/api/v1/company/{cin}/masterdata"
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"[MCA] API call failed: {e}. Using mock data.")
    return None
