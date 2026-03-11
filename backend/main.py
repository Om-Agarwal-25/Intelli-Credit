"""
Intelli-Credit — FastAPI Main Application
All routes, WebSocket, and startup lifecycle.
"""

import os
import uuid
import asyncio
import json
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ─── Connection Manager for WebSockets ───────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, session_id: str, ws: WebSocket):
        await ws.accept()
        self.active[session_id] = ws

    def disconnect(self, session_id: str):
        self.active.pop(session_id, None)

    async def send(self, session_id: str, data: dict):
        ws = self.active.get(session_id)
        if ws:
            try:
                await ws.send_json(data)
            except Exception:
                self.disconnect(session_id)

manager = ConnectionManager()


# ─── App Lifespan ─────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[STARTUP] Intelli-Credit API starting up...")
    # Attempt DB init (graceful failure if postgres not running locally)
    try:
        from db.database import init_db
        await init_db()
        print("[STARTUP] Database schema verified.")
    except Exception as e:
        print(f"[STARTUP] DB init skipped (run PostgreSQL or use Docker): {e}")
    yield
    print("[SHUTDOWN] Intelli-Credit API shutting down.")


app = FastAPI(
    title="Intelli-Credit API",
    description="AI-Powered Corporate Credit Appraisal System for Indian Mid-Market Lending",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (for demo without PostgreSQL)
sessions_store: dict[str, dict] = {}

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CAM_DIR = Path("cam_output")
CAM_DIR.mkdir(exist_ok=True)


# ─── Schemas ──────────────────────────────────────────────────────────────────
class QualitativeInput(BaseModel):
    session_id: str
    officer_id: Optional[str] = "officer_001"
    factory_utilisation: int = 70
    management_impression: str = "Confident"
    promoter_reputation: str = "Neutral"
    site_visit_notes: str = ""
    other_observations: str = ""


class SessionCreate(BaseModel):
    borrower_name: Optional[str] = None
    loan_amount_cr: Optional[float] = None
    loan_type: Optional[str] = "Term Loan"


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "Intelli-Credit API", "version": "1.0.0"}


# ─── WebSocket — Live Pipeline Updates ───────────────────────────────────────
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(session_id)


# ─── Session Management ────────────────────────────────────────────────────────
@app.post("/api/sessions")
async def create_session(body: SessionCreate):
    session_id = str(uuid.uuid4())
    sessions_store[session_id] = {
        "session_id": session_id,
        "borrower_name": body.borrower_name,
        "loan_amount_cr": body.loan_amount_cr,
        "loan_type": body.loan_type,
        "status": "INITIATED",
        "files": [],
    }
    return {"session_id": session_id}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    s = sessions_store.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


# ─── File Upload & Classification ─────────────────────────────────────────────
@app.post("/api/sessions/{session_id}/upload")
async def upload_files(session_id: str, files: list[UploadFile] = File(...)):
    if session_id not in sessions_store:
        sessions_store[session_id] = {"session_id": session_id, "files": [], "status": "INITIATED"}

    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    uploaded = []
    for f in files:
        dest = session_dir / f.filename
        content = await f.read()
        dest.write_bytes(content)

        # Quick classification
        try:
            from modules.ingestion.classifier import classify_document
            doc_type = await classify_document(str(dest))
        except Exception as e:
            doc_type = "OTHER"

        file_info = {"filename": f.filename, "path": str(dest), "doc_type": doc_type, "size": len(content)}
        uploaded.append(file_info)
        sessions_store[session_id].setdefault("files", []).append(file_info)

    return {"uploaded": uploaded, "session_id": session_id}


# ─── Demo: Load Vardhaman PDFs directly (no browser file picker needed) ────────
@app.post("/api/demo/load-vardhaman")
async def demo_load_vardhaman():
    """Create a demo session pre-loaded with all 4 Vardhaman PDFs. Returns session_id ready for analysis."""
    import shutil

    DEMO_PDF_DIR = Path(__file__).parent / "demo_data" / "vardhaman"

    session_id = str(uuid.uuid4())
    sessions_store[session_id] = {
        "session_id": session_id,
        "borrower_name": "Vardhaman Infra & Logistics Pvt. Ltd.",
        "loan_amount_cr": 60,
        "loan_type": "Term Loan",
        "status": "INITIATED",
        "files": [],
    }

    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    uploaded = []
    pdf_files = sorted(DEMO_PDF_DIR.glob("*.pdf")) if DEMO_PDF_DIR.exists() else []

    if not pdf_files:
        raise HTTPException(500, f"Demo PDFs not found at {DEMO_PDF_DIR}. Run: py demo_data/generate_demo_pdfs.py")

    for pdf_path in pdf_files:
        dest = session_dir / pdf_path.name
        shutil.copy2(str(pdf_path), str(dest))

        try:
            from modules.ingestion.classifier import classify_document
            doc_type = await classify_document(str(dest))
        except Exception:
            doc_type = "OTHER"

        file_info = {
            "filename": pdf_path.name,
            "path": str(dest),
            "doc_type": doc_type,
            "size": dest.stat().st_size,
        }
        uploaded.append(file_info)
        sessions_store[session_id]["files"].append(file_info)

    print(f"[DEMO] Loaded {len(uploaded)} Vardhaman PDFs into session {session_id}")
    return {"session_id": session_id, "uploaded": uploaded, "borrower_name": "Vardhaman Infra & Logistics Pvt. Ltd.", "loan_amount_cr": 60}


# ─── Full Analysis Pipeline ───────────────────────────────────────────────────
@app.post("/api/sessions/{session_id}/analyze")
async def analyze(session_id: str, background_tasks: BackgroundTasks):
    if session_id not in sessions_store:
        raise HTTPException(status_code=404, detail="Session not found")
    sessions_store[session_id]["status"] = "PROCESSING"
    background_tasks.add_task(run_pipeline, session_id)
    return {"message": "Analysis started", "session_id": session_id}


async def run_pipeline(session_id: str):
    """Main analysis pipeline — sends progress via WebSocket."""
    session = sessions_store.get(session_id, {})
    files = session.get("files", [])

    async def progress(stage: str, status: str, detail: str = "", flags: dict = None):
        payload = {"type": "progress", "stage": stage, "status": status, "detail": detail}
        if flags:
            payload["flags"] = flags
        await manager.send(session_id, payload)
        await asyncio.sleep(0.1)

    try:
        # Stage 1 — Text Extraction
        await progress("EXTRACTION", "running", "Extracting text from documents...")
        all_text = {}
        from modules.ingestion.extractor import extract_text
        for f in files:
            text = extract_text(f["path"])
            all_text[f["filename"]] = text
        await progress("EXTRACTION", "done", f"Extracted from {len(files)} documents")

        # Stage 2 — GST Reconciliation
        await progress("GST_RECON", "running", "Running GST cross-reference checks...")
        from modules.ingestion.gst_reconciler import run_gst_reconciliation
        gst_flags = run_gst_reconciliation(all_text, session_id)
        await progress("GST_RECON", "done", f"{len(gst_flags)} flags raised", {"new_flags": len(gst_flags)})

        # Stage 3 — RAG Pipeline
        await progress("RAG", "running", "Embedding documents and running semantic risk queries...")
        from modules.ingestion.rag_pipeline import run_rag_pipeline
        rag_flags = await run_rag_pipeline(all_text, session_id)
        await progress("RAG", "done", f"{len(rag_flags)} semantic flags")

        # Stage 4 — Research Agent
        await progress("RESEARCH", "running", "Resolving entity and crawling government databases...")
        from modules.research.entity_resolver import resolve_entity
        entity = resolve_entity(all_text)
        sessions_store[session_id]["entity"] = entity

        from modules.research.mca_crawler import run_mca_research
        mca_flags = await run_mca_research(entity, session_id)
        await progress("MCA", "done", f"MCA21: {len(mca_flags)} findings")

        from modules.research.legal_intel import run_legal_research
        legal_flags = await run_legal_research(entity, session_id)
        await progress("LEGAL", "done", f"Legal: {len(legal_flags)} findings")

        from modules.research.web_crawler import run_web_research
        web_flags = await run_web_research(entity, session_id)
        await progress("WEB", "done", f"News: {len(web_flags)} signals")

        from modules.research.promoter_graph import build_promoter_graph
        graph = build_promoter_graph(entity, session_id)
        sessions_store[session_id]["promoter_graph"] = graph

        # Collect all flags
        all_flags = gst_flags + rag_flags + mca_flags + legal_flags + web_flags
        sessions_store[session_id]["risk_flags"] = all_flags
        sessions_store[session_id]["research_flags"] = mca_flags + legal_flags + web_flags

        total_high = sum(1 for f in all_flags if f.get("severity") == "HIGH")
        total_med = sum(1 for f in all_flags if f.get("severity") == "MEDIUM")
        await progress("FLAGS", "done", f"Total: {total_high} HIGH · {total_med} MEDIUM",
                       {"high": total_high, "medium": total_med, "total": len(all_flags)})

        # Compute Five Cs
        await progress("FIVE_CS", "running", "Computing Five Cs scores...")
        from modules.jury.five_cs import compute_five_cs
        five_cs = compute_five_cs(all_flags)
        sessions_store[session_id]["five_cs"] = five_cs

        # Base XGBoost Score
        await progress("BASE_SCORE", "running", "Running XGBoost base scoring model...")
        from modules.jury.base_scorer import compute_base_score
        base_result = compute_base_score(five_cs)
        sessions_store[session_id]["base_score"] = base_result
        await progress("BASE_SCORE", "done", f"Base Score: {base_result['composite']:.1f}/100")

        sessions_store[session_id]["status"] = "AWAITING_QUALITATIVE"
        await manager.send(session_id, {
            "type": "ready_for_qualitative",
            "five_cs": five_cs,
            "base_score": base_result,
            "risk_flags": all_flags[:50],  # send first 50 for UI
            "promoter_graph": graph,
        })

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"[PIPELINE ERROR] {e}\n{tb}")
        await manager.send(session_id, {"type": "error", "message": str(e)})
        sessions_store[session_id]["status"] = "ERROR"


# ─── Qualitative Input ────────────────────────────────────────────────────────
@app.post("/api/sessions/{session_id}/qualitative")
async def submit_qualitative(session_id: str, body: QualitativeInput, background_tasks: BackgroundTasks):
    if session_id not in sessions_store:
        raise HTTPException(404, "Session not found")

    # LLM-parse free text
    try:
        from modules.ingestion.classifier import parse_qualitative_input
        parsed = await parse_qualitative_input(body.site_visit_notes + " " + body.other_observations)
    except Exception:
        parsed = []

    qual_data = body.dict()
    qual_data["parsed_adjustments"] = parsed
    qual_data["total_score_delta"] = min(25, max(-25, sum(p.get("score_delta", 0) for p in parsed)))
    sessions_store[session_id]["qualitative"] = qual_data
    sessions_store[session_id]["status"] = "JURY_PENDING"

    background_tasks.add_task(run_jury, session_id)
    return {"message": "Qualitative input received. Jury deliberation started.", "parsed_adjustments": parsed}


# ─── Jury Deliberation ────────────────────────────────────────────────────────
async def run_jury(session_id: str):
    session = sessions_store[session_id]

    async def progress(stage, status, detail=""):
        await manager.send(session_id, {"type": "jury_progress", "stage": stage, "status": status, "detail": detail})
        await asyncio.sleep(0.2)

    try:
        await progress("JURY_START", "running", "Starting AI Agent Jury deliberation...")

        from modules.jury.jury_engine import run_jury_deliberation
        jury_result = await run_jury_deliberation(
            session_id=session_id,
            five_cs=session.get("five_cs", {}),
            base_score=session.get("base_score", {}).get("composite", 65),
            risk_flags=session.get("risk_flags", []),
            research_flags=session.get("research_flags", []),
            qualitative=session.get("qualitative", {}),
        )

        sessions_store[session_id]["jury_result"] = jury_result
        sessions_store[session_id]["status"] = "COMPLETE"

        await manager.send(session_id, {"type": "jury_complete", "jury_result": jury_result})

    except Exception as e:
        import traceback
        traceback.print_exc()
        await manager.send(session_id, {"type": "error", "message": f"Jury error: {str(e)}"})


# ─── Generate CAM ─────────────────────────────────────────────────────────────
@app.post("/api/sessions/{session_id}/cam")
async def generate_cam(session_id: str):
    session = sessions_store.get(session_id)
    if not session or "jury_result" not in session:
        raise HTTPException(400, "Jury deliberation not complete yet")

    try:
        from modules.cam.cam_generator import generate_cam_document
        cam_path = generate_cam_document(session_id, session)
        return {"cam_path": cam_path, "download_url": f"/api/sessions/{session_id}/cam/download"}
    except Exception as e:
        raise HTTPException(500, f"CAM generation failed: {e}")


@app.get("/api/sessions/{session_id}/cam/download")
async def download_cam(session_id: str):
    cam_path = CAM_DIR / f"CAM_{session_id}.docx"
    if not cam_path.exists():
        raise HTTPException(404, "CAM document not found. Generate it first.")
    return FileResponse(
        path=str(cam_path),
        filename=f"CreditAppraisalMemo_{session_id[:8]}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


# ─── Get Full Session State ───────────────────────────────────────────────────
@app.get("/api/sessions/{session_id}/results")
async def get_results(session_id: str):
    session = sessions_store.get(session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    return session


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("BACKEND_PORT", 8000)), reload=True)
