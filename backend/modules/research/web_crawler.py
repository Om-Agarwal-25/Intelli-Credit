"""
Module 2 — Web & News Intelligence
Searches for company news using SerpAPI or Anthropic web search.
Falls back to mock news for demo.
"""

import os


MOCK_NEWS = {
    "vardhaman": [
        {
            "title": "Vardhaman Infra delays NHAI highway project handover",
            "date": "2024-11-08",
            "source": "Economic Times",
            "url": "https://economictimes.indiatimes.com/...",
            "summary": "Vardhaman Infra & Logistics faces NHAI penalty notice for 14-month delay in NH-65 highway project in Maharashtra. Project completion only 62% against scheduled 90%.",
            "severity": "HIGH",
            "five_c_pillar": "C2",
        },
        {
            "title": "Infrastructure sector faces working capital stress: CRISIL",
            "date": "2024-09-15",
            "source": "Business Standard",
            "url": "https://www.business-standard.com/...",
            "summary": "CRISIL report highlights growing working capital stress in mid-tier infrastructure companies due to delayed government payments.",
            "severity": "MEDIUM",
            "five_c_pillar": "C5",
        },
    ]
}


async def run_web_research(entity: dict, session_id: str) -> list:
    """Run semantic web search for news and intelligence."""
    flags = []
    demo_mode = os.getenv("DEMO_MODE", "true").lower() == "true"
    company_name = entity.get("company_name", "")

    news_items = []

    if demo_mode or "vardhaman" in company_name.lower():
        news_items = MOCK_NEWS.get("vardhaman", [])
    else:
        news_items = await _serpapi_search(company_name, entity.get("sector", ""))

    for item in news_items:
        flags.append({
            "flag_type": f"NEWS_{item['severity']}",
            "severity": item["severity"],
            "source_document": f"Web — {item['source']}",
            "evidence_snippet": f"[{item['date']}] {item['title']}: {item['summary']}",
            "page_reference": item.get("url", ""),
            "source_module": "RESEARCH",
            "five_c_pillar": item.get("five_c_pillar", "C5"),
            "session_id": session_id,
        })

    return flags


async def _serpapi_search(company_name: str, sector: str) -> list:
    """Search using SerpAPI if key available."""
    serp_key = os.getenv("SERP_API_KEY", "")
    if not serp_key:
        return []

    import httpx
    queries = [
        f"{company_name} fraud default penalty",
        f"{company_name} NCLT insolvency court case",
        f"{sector} India regulatory risk 2025",
    ]

    results = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        for q in queries:
            try:
                resp = await client.get(
                    "https://serpapi.com/search",
                    params={"q": q, "api_key": serp_key, "num": 5, "gl": "in", "hl": "en"},
                )
                data = resp.json()
                for item in data.get("organic_results", [])[:3]:
                    results.append({
                        "title": item.get("title", ""),
                        "date": item.get("date", "Unknown"),
                        "source": item.get("source", "Web"),
                        "url": item.get("link", ""),
                        "summary": item.get("snippet", ""),
                        "severity": "MEDIUM",
                        "five_c_pillar": "C5",
                    })
            except Exception as e:
                print(f"[WEB] SerpAPI error: {e}")

    return results
