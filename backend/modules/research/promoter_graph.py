"""
Module 2 — Promoter Knowledge Graph
Builds director-company relationship graph for visualization and risk scoring.
"""

import os


def build_promoter_graph(entity: dict, session_id: str) -> dict:
    """Build director-company graph from MCA data. Returns JSON for frontend."""
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    company_name = (entity.get("company_name") or "").lower()

    if demo_mode or "vardhaman" in company_name:
        return _vardhaman_demo_graph()

    # Build from entity data
    cin = entity.get("cin", "UNKNOWN")
    directors = entity.get("directors", [])

    nodes = [{"id": cin, "label": entity.get("company_name", "Company"), "type": "company", "status": "active"}]
    edges = []

    for d in directors:
        din = d.get("din", "")
        name = d.get("name", "Director")
        nodes.append({"id": din, "label": name, "type": "director", "status": "active"})
        edges.append({"source": din, "target": cin, "label": "director"})

    return {"nodes": nodes, "edges": edges, "risk_score": 30}


def _vardhaman_demo_graph() -> dict:
    """Pre-built graph for Vardhaman Infra demo showing the risk network."""
    return {
        "nodes": [
            {"id": "U45200MH2015PTC264831", "label": "Vardhaman Infra & Logistics", "type": "company", "status": "active", "group": 1},
            {"id": "U45200MH2014PTC253421", "label": "Vardhaman Buildcon", "type": "company", "status": "struck_off", "group": 2},
            {"id": "AAA-2345", "label": "Vardhaman Holdings LLP", "type": "company", "status": "struck_off", "group": 2},
            {"id": "06284530", "label": "Rajesh Vardhaman", "type": "director", "status": "active", "group": 3},
            {"id": "07284531", "label": "Kavita Mehta ⚠️", "type": "director", "status": "disqualified", "group": 4},
        ],
        "edges": [
            {"source": "06284530", "target": "U45200MH2015PTC264831", "label": "director"},
            {"source": "06284530", "target": "U45200MH2014PTC253421", "label": "director"},
            {"source": "06284530", "target": "AAA-2345", "label": "director"},
            {"source": "07284531", "target": "U45200MH2015PTC264831", "label": "director (disqualified)"},
        ],
        "risk_score": 75,
        "risk_signals": [
            "Director DIN 07284531 disqualified under Section 164(2)",
            "2 associated companies struck off for non-filing",
            "Possible capital diversion through struck-off entities",
        ],
        "company_name": "Vardhaman Infra & Logistics Pvt. Ltd.",
    }
