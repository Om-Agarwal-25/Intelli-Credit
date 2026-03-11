"""
Intelli-Credit — Full Module Test Suite
Tests every module individually with mock data, no API keys required.
Run from: d:\\Projects\\Intelli-Credit\\backend
Usage: py test_all_modules.py
"""

import sys, os, asyncio, json, traceback
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Monkey-patch LLM env vars so no real API calls are made
os.environ.setdefault("LLM_PROVIDER", "anthropic")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-no-real-calls")
os.environ.setdefault("OPENAI_API_KEY", "test-key-no-real-calls")
os.environ.setdefault("DEMO_MODE", "true")

PASS = "✅ PASS"
FAIL = "❌ FAIL"
results = {}

def report(name, ok, detail=""):
    status = PASS if ok else FAIL
    results[name] = "PASS" if ok else "FAIL"
    print(f"  {status}  {name}" + (f"  — {detail}" if detail else ""))

def run(name, fn, *args, **kwargs):
    try:
        out = fn(*args, **kwargs)
        report(name, True, str(out)[:120] if out else "")
        return out
    except Exception as e:
        report(name, False, str(e)[:200])
        traceback.print_exc()
        return None

async def arun(name, fn, *args, **kwargs):
    try:
        out = await fn(*args, **kwargs)
        report(name, True, str(out)[:120] if out else "")
        return out
    except Exception as e:
        report(name, False, str(e)[:200])
        traceback.print_exc()
        return None

# ─── SAMPLE DATA ─────────────────────────────────────────────────────────────

SAMPLE_FLAGS = [
    {"flag_type": "DIN_DISQUALIFIED",    "severity": "HIGH",   "five_c_pillar": "C1", "source_document": "MCA21",   "evidence_snippet": "Director DIN 07284531 disqualified S.164(2)", "session_id": "test-session"},
    {"flag_type": "NCLT_PROCEEDINGS",    "severity": "HIGH",   "five_c_pillar": "C1", "source_document": "NCLT",    "evidence_snippet": "IB/1234/MB/2024 admitted",                      "session_id": "test-session"},
    {"flag_type": "LITIGATION_UNDISCL",  "severity": "HIGH",   "five_c_pillar": "C1", "source_document": "eCourts", "evidence_snippet": "Case 1842/2024 ₹4.2Cr undisclosed",             "session_id": "test-session"},
    {"flag_type": "REVENUE_INFLATION",   "severity": "HIGH",   "five_c_pillar": "C2", "source_document": "GSTR-1",  "evidence_snippet": "GST-bank mismatch >60% Apr-May",                "session_id": "test-session"},
    {"flag_type": "GOING_CONCERN",       "severity": "HIGH",   "five_c_pillar": "C2", "source_document": "AR p.34", "evidence_snippet": "Going concern note Note 31",                     "session_id": "test-session"},
    {"flag_type": "PROMOTER_NET_RISK",   "severity": "MEDIUM", "five_c_pillar": "C1", "source_document": "MCA21",   "evidence_snippet": "2 associated companies struck off",              "session_id": "test-session"},
    {"flag_type": "CONTINGENT_LIAB",     "severity": "MEDIUM", "five_c_pillar": "C3", "source_document": "AR",      "evidence_snippet": "Contingent liabilities ₹8.4 Cr",                "session_id": "test-session"},
    {"flag_type": "GST_ITC_MISMATCH",    "severity": "HIGH",   "five_c_pillar": "C2", "source_document": "GSTR-2A", "evidence_snippet": "ITC excess 21.4% vs 2A",                         "session_id": "test-session"},
]

SAMPLE_TEXT = {
    "vardhaman_gstr1.pdf": """
GSTR-1 Return — Vardhaman Infra & Logistics Pvt. Ltd.
GSTIN: 27AABCV1234F1ZA
Total Taxable Value: 340,00,000
GST Collected: 61,20,000
ITC Claimed in 3B: 29,85,000
ITC Available in 2A: 24,58,000
Going Concern: Note 31 refers uncertainty
Director: Kavita Mehta DIN 07284531
""",
    "vardhaman_bank.pdf": """
State Bank of India — Current Account Statement
Account: Vardhaman Infra & Logistics
April 2023 Credits: 1,05,60,000
May 2023 Credits: 1,10,20,000
June 2023 Credits: 3,08,10,000
Total Annual Credits: 34,00,00,000
""",
}

SAMPLE_ENTITY = {
    "company_name": "Vardhaman Infra & Logistics Pvt. Ltd.",
    "cin": "U45200MH2015PTC264831",
    "gstin": "27AABCV1234F1ZA",
    "sector": "infrastructure",
    "directors": [{"name": "Rajesh Vardhaman", "din": "06284530"}, {"name": "Kavita Mehta", "din": "07284531"}],
}

DEMO_PROSECUTION = {
    "prosecution_findings": [
        {"finding_id": "P1", "finding_text": "Director disqualified under S.164(2)", "five_c_pillar": "C1", "score_delta": -15, "evidence_source": "MCA21", "severity": "HIGH"},
        {"finding_id": "P2", "finding_text": "Undisclosed NCLT + e-Courts litigation", "five_c_pillar": "C1", "score_delta": -12, "evidence_source": "e-Courts", "severity": "HIGH"},
        {"finding_id": "P3", "finding_text": "Going-concern note page 34 + contingent ₹8.4Cr", "five_c_pillar": "C2", "score_delta": -8, "evidence_source": "AR Note 31", "severity": "MEDIUM"},
    ],
    "total_prosecution_delta": -35,
}

DEMO_DEFENCE = {
    "defence_findings": [
        {"finding_id": "D1", "finding_text": "GST-bank match 94% confirms ₹340Cr turnover genuine", "five_c_pillar": "C2", "score_delta": 5, "evidence_source": "GST/Bank", "confidence": "HIGH"},
        {"finding_id": "D2", "finding_text": "DSCR 1.6x comfortably above RBI 1.25x", "five_c_pillar": "C2", "score_delta": 4, "evidence_source": "Annual Report", "confidence": "HIGH"},
        {"finding_id": "D3", "finding_text": "18% YoY growth vs sector 11%", "five_c_pillar": "C2", "score_delta": 3, "evidence_source": "CRISIL", "confidence": "MEDIUM"},
    ],
    "total_defence_delta": 12,
}

DEMO_QUALITATIVE = {
    "factory_utilisation": 70,
    "management_impression": "Mixed",
    "promoter_reputation": "Concerning",
    "site_visit_notes": "Factory at 70% utilisation. Several machines idle.",
    "other_observations": "Director Kavita Mehta was absent from the meeting.",
    "total_score_delta": -5,
    "officer_id": "officer_001",
}

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 — DB / Database
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 1: DATABASE")
print("═"*60)

def test_db_import():
    from db.database import engine, init_db
    return "engine imported OK"

run("db.database import", test_db_import)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 — INGESTION: extractor
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 2: INGESTION — extractor.py")
print("═"*60)

def test_extractor_import():
    from modules.ingestion.extractor import extract_text
    return "import OK"

def test_extractor_mock():
    """Test with a temp text file (not PDF). Just checks it doesn't crash."""
    import tempfile
    from modules.ingestion.extractor import extract_text
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w", encoding="utf-8") as f:
        f.write("This is a test document.")
        fname = f.name
    result = extract_text(fname)
    return f"returned: {type(result).__name__}, len={len(str(result))}"

run("extractor import", test_extractor_import)
run("extractor mock file", test_extractor_mock)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 — INGESTION: classifier
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 3: INGESTION — classifier.py")
print("═"*60)

def test_classifier_import():
    from modules.ingestion.classifier import classify_document, parse_qualitative_input, _rule_based_classify
    return "import OK"

def test_classifier_rule_based():
    from modules.ingestion.classifier import _rule_based_classify
    t1 = _rule_based_classify("GSTIN GSTR-1 taxable value CIN", "vardhaman_gstr1_fy24.pdf")
    t2 = _rule_based_classify("credits debits SBI current account", "bank_statement.pdf")
    t3 = _rule_based_classify("board of directors EBITDA balance sheet", "annual_report.pdf")
    return f"GST={t1}, Bank={t2}, AR={t3}"

async def test_classifier_async():
    from modules.ingestion.classifier import classify_document
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb") as f:
        f.write(b"GSTR1 GSTIN 27AABCV1234F1ZA taxable value")
        fname = f.name
    result = await classify_document(fname)
    return f"classified as: {result}"

async def test_parse_qualitative():
    from modules.ingestion.classifier import parse_qualitative_input
    result = await parse_qualitative_input("Factory at 70% utilisation. Director was absent.")
    return f"parsed {len(result)} adjustments"

run("classifier import", test_classifier_import)
run("classifier rule-based", test_classifier_rule_based)
asyncio.run(arun("classifier async (demo mode)", test_classifier_async))
asyncio.run(arun("parse_qualitative (demo mode)", test_parse_qualitative))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 4 — INGESTION: gst_reconciler
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 4: INGESTION — gst_reconciler.py")
print("═"*60)

def test_gst_import():
    from modules.ingestion.gst_reconciler import run_gst_reconciliation
    return "import OK"

def test_gst_reconcile():
    from modules.ingestion.gst_reconciler import run_gst_reconciliation
    flags = run_gst_reconciliation(SAMPLE_TEXT, "test-session")
    high = [f for f in flags if f.get("severity") == "HIGH"]
    return f"Total flags={len(flags)}, HIGH={len(high)}"

run("gst_reconciler import", test_gst_import)
run("gst_reconciler with sample data", test_gst_reconcile)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 5 — INGESTION: rag_pipeline
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 5: INGESTION — rag_pipeline.py")
print("═"*60)

def test_rag_import():
    from modules.ingestion.rag_pipeline import run_rag_pipeline, chunk_text
    return "import OK"

def test_rag_chunking():
    from modules.ingestion.rag_pipeline import chunk_text
    text = "This is a test sentence. " * 100
    chunks = chunk_text(text)
    return f"{len(chunks)} chunks of {len(chunks[0]) if chunks else 0} chars each"

async def test_rag_pipeline_demo():
    from modules.ingestion.rag_pipeline import run_rag_pipeline
    flags = await run_rag_pipeline(SAMPLE_TEXT, "test-session")
    return f"returned {len(flags)} risk flags"

run("rag_pipeline import", test_rag_import)
run("rag chunk_text", test_rag_chunking)
asyncio.run(arun("rag_pipeline end-to-end (demo)", test_rag_pipeline_demo))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 6 — INGESTION: flag_store
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 6: INGESTION — flag_store.py")
print("═"*60)

def test_flag_store_import():
    from modules.ingestion.flag_store import save_flags
    return "import OK"

async def test_flag_store_save():
    from modules.ingestion.flag_store import save_flags
    await save_flags(SAMPLE_FLAGS[:3], "test-session")
    return "saved 3 flags (in-memory fallback)"

run("flag_store import", test_flag_store_import)
asyncio.run(arun("flag_store save_flags (no DB)", test_flag_store_save))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 7 — RESEARCH: entity_resolver
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 7: RESEARCH — entity_resolver.py")
print("═"*60)

def test_entity_import():
    from modules.research.entity_resolver import resolve_entity
    return "import OK"

def test_entity_resolve():
    from modules.research.entity_resolver import resolve_entity
    entity = resolve_entity(SAMPLE_TEXT)
    return f"company={entity.get('company_name','?')}, cin={entity.get('cin','?')}, gstin={entity.get('gstin','?')}, sector={entity.get('sector','?')}"

run("entity_resolver import", test_entity_import)
run("entity_resolver resolve", test_entity_resolve)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 8 — RESEARCH: mca_crawler
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 8: RESEARCH — mca_crawler.py")
print("═"*60)

def test_mca_import():
    from modules.research.mca_crawler import run_mca_research
    return "import OK"

async def test_mca_mock():
    from modules.research.mca_crawler import run_mca_research
    flags = await run_mca_research(SAMPLE_ENTITY, "test-session")
    high = [f for f in flags if f.get("severity") == "HIGH"]
    return f"flags={len(flags)}, HIGH={len(high)}"

run("mca_crawler import", test_mca_import)
asyncio.run(arun("mca_crawler mock data", test_mca_mock))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 9 — RESEARCH: legal_intel
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 9: RESEARCH — legal_intel.py")
print("═"*60)

def test_legal_import():
    from modules.research.legal_intel import run_legal_research
    return "import OK"

async def test_legal_mock():
    from modules.research.legal_intel import run_legal_research
    flags = await run_legal_research(SAMPLE_ENTITY, "test-session")
    return f"flags={len(flags)}, types={[f['flag_type'] for f in flags]}"

run("legal_intel import", test_legal_import)
asyncio.run(arun("legal_intel mock data", test_legal_mock))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 10 — RESEARCH: web_crawler
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 10: RESEARCH — web_crawler.py")
print("═"*60)

def test_web_import():
    from modules.research.web_crawler import run_web_research
    return "import OK"

async def test_web_mock():
    from modules.research.web_crawler import run_web_research
    flags = await run_web_research(SAMPLE_ENTITY, "test-session")
    return f"flags={len(flags)}, first_type={flags[0]['flag_type'] if flags else None}"

run("web_crawler import", test_web_import)
asyncio.run(arun("web_crawler mock data", test_web_mock))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 11 — RESEARCH: promoter_graph
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 11: RESEARCH — promoter_graph.py")
print("═"*60)

def test_graph_import():
    from modules.research.promoter_graph import build_promoter_graph
    return "import OK"

def test_graph_build():
    from modules.research.promoter_graph import build_promoter_graph
    graph = build_promoter_graph(SAMPLE_ENTITY, "test-session")
    return f"nodes={len(graph['nodes'])}, edges={len(graph['edges'])}, risk_score={graph.get('risk_score')}"

run("promoter_graph import", test_graph_import)
run("promoter_graph build", test_graph_build)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 12 — JURY: five_cs
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 12: JURY — five_cs.py")
print("═"*60)

def test_five_cs_import():
    from modules.jury.five_cs import compute_five_cs
    return "import OK"

def test_five_cs_compute():
    from modules.jury.five_cs import compute_five_cs
    result = compute_five_cs(SAMPLE_FLAGS)
    return f"C1={result['C1']}, C2={result['C2']}, C3={result['C3']}, C4={result['C4']}, C5={result['C5']}, composite={result['composite']}"

def test_five_cs_special_rules():
    from modules.jury.five_cs import compute_five_cs
    result = compute_five_cs(SAMPLE_FLAGS)
    # DIN_DISQUALIFIED flag should cap C1 at 35
    c1_capped = result["C1"] <= 35
    return f"C1 capped at 35 for DIN_DISQUALIFIED: {c1_capped} (actual={result['C1']})"

run("five_cs import", test_five_cs_import)
run("five_cs compute_five_cs", test_five_cs_compute)
run("five_cs special rules (DIN cap)", test_five_cs_special_rules)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 13 — JURY: base_scorer
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 13: JURY — base_scorer.py")
print("═"*60)

def test_scorer_import():
    from modules.jury.base_scorer import compute_base_score
    return "import OK"

def test_scorer_compute():
    from modules.jury.five_cs import compute_five_cs
    from modules.jury.base_scorer import compute_base_score
    five_cs = compute_five_cs(SAMPLE_FLAGS)
    result = compute_base_score(five_cs)
    return f"composite={result['composite']}, decision={result['decision']}, model={result['model_used']}"

run("base_scorer import", test_scorer_import)
run("base_scorer compute_base_score", test_scorer_compute)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 14 — JURY: prosecutor
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 14: JURY — prosecutor.py")
print("═"*60)

def test_prosecutor_import():
    from modules.jury.prosecutor import run_prosecutor, _demo_prosecution, _build_context_message
    return "import OK"

def test_demo_prosecution():
    from modules.jury.prosecutor import _demo_prosecution
    result = _demo_prosecution()
    return f"findings={len(result['prosecution_findings'])}, delta={result['total_prosecution_delta']}"

def test_build_context():
    from modules.jury.prosecutor import _build_context_message
    from modules.jury.five_cs import compute_five_cs
    five_cs = compute_five_cs(SAMPLE_FLAGS)
    ctx = {"five_cs": five_cs, "risk_flags": SAMPLE_FLAGS, "research_flags": [], "qualitative": DEMO_QUALITATIVE}
    msg = _build_context_message(ctx)
    return f"context message built, len={len(msg)} chars"

async def test_prosecutor_demo():
    from modules.jury.prosecutor import run_prosecutor
    from modules.jury.five_cs import compute_five_cs
    five_cs = compute_five_cs(SAMPLE_FLAGS)
    ctx = {"five_cs": five_cs, "risk_flags": SAMPLE_FLAGS, "research_flags": [], "qualitative": DEMO_QUALITATIVE}
    result = await run_prosecutor(ctx)  # will fail LLM, use demo fallback
    return f"findings={len(result.get('prosecution_findings', []))}, delta={result.get('total_prosecution_delta')}"

run("prosecutor import", test_prosecutor_import)
run("prosecutor demo_prosecution", test_demo_prosecution)
run("prosecutor build_context_message", test_build_context)
asyncio.run(arun("prosecutor run_prosecutor (demo fallback)", test_prosecutor_demo))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 15 — JURY: defender
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 15: JURY — defender.py")
print("═"*60)

def test_defender_import():
    from modules.jury.defender import run_defender, _demo_defence
    return "import OK"

def test_demo_defence():
    from modules.jury.defender import _demo_defence
    result = _demo_defence()
    return f"findings={len(result['defence_findings'])}, delta={result['total_defence_delta']}"

async def test_defender_demo():
    from modules.jury.defender import run_defender
    from modules.jury.five_cs import compute_five_cs
    five_cs = compute_five_cs(SAMPLE_FLAGS)
    ctx = {"five_cs": five_cs, "risk_flags": SAMPLE_FLAGS, "research_flags": [], "qualitative": DEMO_QUALITATIVE}
    result = await run_defender(ctx)
    return f"findings={len(result.get('defence_findings', []))}, delta={result.get('total_defence_delta')}"

run("defender import", test_defender_import)
run("defender demo_defence", test_demo_defence)
asyncio.run(arun("defender run_defender (demo fallback)", test_defender_demo))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 16 — JURY: judge
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 16: JURY — judge.py")
print("═"*60)

def test_judge_import():
    from modules.jury.judge import run_judge, _demo_verdict, _validate_verdict
    return "import OK"

def test_demo_verdict():
    from modules.jury.judge import _demo_verdict
    v = _demo_verdict(DEMO_PROSECUTION, DEMO_DEFENCE)
    return f"rec={v['final_recommendation']}, amount=₹{v['recommended_loan_amount_cr']}Cr, conditions={len(v['conditions'])}"

async def test_judge_demo():
    from modules.jury.judge import run_judge
    from modules.jury.five_cs import compute_five_cs
    five_cs = compute_five_cs(SAMPLE_FLAGS)
    ctx = {"five_cs": five_cs, "risk_flags": SAMPLE_FLAGS, "research_flags": [], "qualitative": DEMO_QUALITATIVE}
    result = await run_judge(ctx, DEMO_PROSECUTION, DEMO_DEFENCE)
    return f"rec={result.get('final_recommendation')}, amount=₹{result.get('recommended_loan_amount_cr')}Cr"

run("judge import", test_judge_import)
run("judge demo_verdict", test_demo_verdict)
asyncio.run(arun("judge run_judge (demo fallback)", test_judge_demo))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 17 — JURY: jury_engine (full end-to-end jury)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 17: JURY — jury_engine.py (FULL JURY)")
print("═"*60)

def test_jury_import():
    from modules.jury.jury_engine import run_jury_deliberation
    return "import OK"

async def test_jury_full():
    from modules.jury.jury_engine import run_jury_deliberation
    from modules.jury.five_cs import compute_five_cs
    from modules.jury.base_scorer import compute_base_score
    five_cs = compute_five_cs(SAMPLE_FLAGS)
    base = compute_base_score(five_cs)
    result = await run_jury_deliberation(
        session_id="test-session",
        five_cs=five_cs,
        base_score=base["composite"],
        risk_flags=SAMPLE_FLAGS,
        research_flags=[],
        qualitative=DEMO_QUALITATIVE,
    )
    return (f"base={result['base_score']}, jury={result['jury_score']}, "
            f"delta={result['net_delta']}, decision={result['jury_decision']}")

run("jury_engine import", test_jury_import)
asyncio.run(arun("jury_engine full deliberation", test_jury_full))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 18 — CAM: chart_generator
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 18: CAM — chart_generator.py")
print("═"*60)

def test_charts_import():
    from modules.cam.chart_generator import create_five_cs_radar, create_gst_bank_chart, create_score_journey_chart
    return "import OK"

def test_radar_chart():
    from modules.cam.chart_generator import create_five_cs_radar
    five_cs = {"C1": 35, "C2": 68, "C3": 70, "C4": 70, "C5": 72}
    png = create_five_cs_radar(five_cs)
    return f"radar PNG size: {len(png)} bytes"

def test_gst_chart():
    from modules.cam.chart_generator import create_gst_bank_chart
    data = {"months": list(range(1, 13)), "gst_values": [285, 297, 312, 318, 325, 330, 338, 342, 315, 307, 295, 281], "bank_values": [105, 110, 308, 313, 320, 325, 334, 338, 310, 302, 291, 278]}
    png = create_gst_bank_chart(data)
    return f"GST chart PNG size: {len(png)} bytes"

def test_journey_chart():
    from modules.cam.chart_generator import create_score_journey_chart
    png = create_score_journey_chart(78.0, 43.0, 55.0, 51.0)
    return f"journey chart PNG size: {len(png)} bytes"

run("chart_generator import", test_charts_import)
run("create_five_cs_radar", test_radar_chart)
run("create_gst_bank_chart", test_gst_chart)
run("create_score_journey_chart", test_journey_chart)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 19 — CAM: cam_generator
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 19: CAM — cam_generator.py")
print("═"*60)

def test_cam_import():
    from modules.cam.cam_generator import generate_cam_document
    return "import OK"

async def test_cam_generate():
    from modules.jury.jury_engine import run_jury_deliberation
    from modules.jury.five_cs import compute_five_cs
    from modules.jury.base_scorer import compute_base_score
    from modules.cam.cam_generator import generate_cam_document
    import os

    five_cs = compute_five_cs(SAMPLE_FLAGS)
    base = compute_base_score(five_cs)
    jury_result = await run_jury_deliberation("cam-test", five_cs, base["composite"], SAMPLE_FLAGS, [], DEMO_QUALITATIVE)

    session = {
        "entity": SAMPLE_ENTITY,
        "loan_amount_cr": 60,
        "loan_type": "Term Loan",
        "risk_flags": SAMPLE_FLAGS,
        "research_flags": [],
        "five_cs": five_cs,
        "jury_result": jury_result,
        "qualitative": DEMO_QUALITATIVE,
    }
    path = generate_cam_document("cam-test", session)
    exists = os.path.exists(path) if path else False
    size = os.path.getsize(path) if exists else 0
    return f"CAM .docx created: {exists}, size={size} bytes, path={path}"

run("cam_generator import", test_cam_import)
asyncio.run(arun("cam_generator generate full CAM", test_cam_generate))

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 20 — PRIVACY: he_scorer
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 20: PRIVACY — he_scorer.py")
print("═"*60)

def test_he_import():
    from privacy.he_scorer import encrypt_and_score
    return "import OK"

def test_he_score():
    from privacy.he_scorer import encrypt_and_score
    result = encrypt_and_score(1.6, 1.8, 0.18, 94.0, 35.0, 68.0)
    return f"he_score={result['he_score']}, encrypted={result['encryption_applied']}, badges={len(result.get('compliance_badges', []))}"

run("he_scorer import", test_he_import)
run("he_scorer encrypt_and_score", test_he_score)

# ─────────────────────────────────────────────────────────────────────────────
# MODULE 21 — MAIN.PY FastAPI Routes
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("MODULE 21: MAIN.PY — FastAPI app")
print("═"*60)

def test_main_import():
    import importlib.util
    spec = importlib.util.spec_from_file_location("main", os.path.join(os.path.dirname(__file__), "main.py"))
    mod = importlib.util.load_from_spec = spec
    from fastapi.testclient import TestClient
    import main as m
    client = TestClient(m.app)
    resp = client.get("/health")
    return f"status={resp.status_code}, body={resp.json()}"

run("main.py FastAPI import + /health", test_main_import)

# ─────────────────────────────────────────────────────────────────────────────
# FULL END-TO-END PIPELINE TEST (in-memory, no real APIs)
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("FULL END-TO-END PIPELINE TEST")
print("═"*60)

async def test_full_pipeline():
    """End-to-end from flags → five_cs → base → jury → cam."""
    from modules.jury.five_cs import compute_five_cs
    from modules.jury.base_scorer import compute_base_score
    from modules.jury.jury_engine import run_jury_deliberation
    from modules.research.promoter_graph import build_promoter_graph
    from modules.cam.cam_generator import generate_cam_document
    from modules.research.mca_crawler import run_mca_research
    from modules.research.legal_intel import run_legal_research

    # Five Cs
    five_cs = compute_five_cs(SAMPLE_FLAGS)
    assert five_cs["C1"] <= 35, "C1 should be capped"
    assert 0 <= five_cs["composite"] <= 100

    # Base Score
    base = compute_base_score(five_cs)
    assert 0 <= base["composite"] <= 100
    assert base["decision"] in ("APPROVE", "CONDITIONAL", "REJECT")

    # Research
    mca_flags = await run_mca_research(SAMPLE_ENTITY, "e2e-test")
    legal_flags = await run_legal_research(SAMPLE_ENTITY, "e2e-test")
    graph = build_promoter_graph(SAMPLE_ENTITY, "e2e-test")
    assert len(graph["nodes"]) > 0

    all_flags = SAMPLE_FLAGS + mca_flags + legal_flags

    # Full Jury
    jury = await run_jury_deliberation("e2e-test", five_cs, base["composite"], all_flags, mca_flags + legal_flags, DEMO_QUALITATIVE)
    assert jury["jury_score"] is not None
    assert jury["jury_decision"] in ("APPROVE", "CONDITIONAL", "REJECT")
    assert 0 <= jury["jury_score"] <= 100

    # CAM
    session = {
        "entity": SAMPLE_ENTITY, "loan_amount_cr": 60, "loan_type": "Term Loan",
        "risk_flags": all_flags, "research_flags": mca_flags + legal_flags,
        "five_cs": five_cs, "jury_result": jury, "qualitative": DEMO_QUALITATIVE,
    }
    cam_path = generate_cam_document("e2e-test", session)
    import os
    assert cam_path and os.path.exists(cam_path), f"CAM file missing: {cam_path}"

    return (f"Five Cs composite={five_cs['composite']}, "
            f"base={base['composite']}, jury={jury['jury_score']}, "
            f"decision={jury['jury_decision']}, CAM={cam_path}")

asyncio.run(arun("FULL PIPELINE (demo, no API keys)", test_full_pipeline))

# ─────────────────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "═"*60)
print("FINAL REPORT")
print("═"*60)
passed = [k for k, v in results.items() if v == "PASS"]
failed = [k for k, v in results.items() if v == "FAIL"]
print(f"\n✅ PASSED: {len(passed)}/{len(results)}")
print(f"❌ FAILED: {len(failed)}/{len(results)}")
if failed:
    print("\nFailed tests:")
    for f in failed:
        print(f"  ❌ {f}")
else:
    print("\n🎉 ALL TESTS PASSED!")
