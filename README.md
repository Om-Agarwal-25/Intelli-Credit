<div align="center">

# 🏦 Intelli-Credit
### AI-Powered Corporate Credit Appraisal for Indian Banks
> From raw documents to Credit Appraisal Memo in under 5 minutes

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![XGBoost](https://img.shields.io/badge/XGBoost-2.1-FF6600?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Hackathon_Prototype-blueviolet?style=for-the-badge)

**AI-powered corporate credit appraisal system for Indian banks — from raw documents to Credit Appraisal Memo in under 5 minutes.**

[🚀 Quick Start](#-getting-started) · [🏛️ Architecture](#-system-architecture) · [🎯 Live Demo](#-live-demo-scenario--vardhaman-infra) · [📚 API Docs](#-api-reference)

</div>

---

## 🏦 The Problem We Solve

India's banking system faces a **data paradox**: banks drown in documents but still miss fraud. The ABG Shipyard scam (₹22,842 Cr), DHFL collapse (₹34,000 Cr), IL&FS crisis (₹99,000 Cr), and Videocon default all shared one horrifying trait — the warning signals existed in publicly available records, but no one connected the dots before sanction.

Current credit appraisals take **2–4 weeks** because a credit officer manually reads 200+ pages of PDFs, cross-checks GST portals, calls MCA21, and Googles the promoters — all in sequence, all by hand. The result is slow, expensive, inconsistent, and vulnerable to a determined fraudster who submits clean-looking numbers.

**Intelli-Credit automates the entire pipeline in under 5 minutes**, connecting signals that a human would miss.

---

## ⚙️ What Intelli-Credit Does

1. **Ingests raw PDFs** — GST returns, bank statements, annual reports, ITRs, legal documents, and rating reports
2. **Extracts text from even scanned Hindi-English PDFs** using PyMuPDF + EasyOCR with automatic fallback
3. **Cross-checks GSTR-1 vs bank credits** to detect revenue inflation — round numbers and suspiciously near-identical figures
4. **Reconciles GSTR-2A vs GSTR-3B** to catch fake Input Tax Credit claims before they become irrecoverable losses
5. **Detects round-tripping and circular trading** from bank statement patterns using graph-based analysis
6. **Searches MCA21, e-Courts, NCLT and news** for undisclosed director disqualifications, pending litigation, and regulatory penalties
7. **Builds a promoter knowledge graph** across all linked companies, directors, and family members to surface hidden exposure
8. **Runs a 3-agent AI jury** — Prosecutor, Defender, Judge — who debate the risk in writing, with every argument stored in the audit trail
9. **Scores across Five Cs of Credit** using XGBoost with SHAP explainability — every point deduction is traceable to a specific document
10. **Auto-generates a professional Credit Appraisal Memo** as a Word document, ready for the Credit Committee

---

## ⚖️ The AI Agent Jury — Key Differentiator

Most AI credit tools give you one score from one model. We think that's the wrong architecture for a decision that could expose a bank to ₹50 Cr of loss.

**The Problem with a Single AI Model:**
A single model trained on historical data inherits historical biases, cannot catch its own blind spots, and produces a score with no visible reasoning chain. When it's wrong, you can't tell *why* it was wrong.

**Our Solution — Adversarial Jury:**

| Single AI Model | AI Agent Jury |
|---|---|
| One perspective — confidently wrong | Three views — disagreement is visible |
| Black box score with no audit trail | Full argument trail embedded in the CAM |
| Bias baked into one model's weights | Adversarial prompting actively cancels bias |
| Binary approve or reject | Confidence band with explicit uncertainty zones |
| Can't be cross-examined by RBI | Every finding citable in regulatory review |

The **Risk Scrutiny Agent (Prosecutor)** argues for rejection. The **Credit Advocacy Agent (Defender)** argues for approval. The **Adjudication Agent (Judge)** weighs both sides with the wisdom of a 2,000-meeting credit committee chairman and delivers a written verdict. This is how real credit committees work — we just run it in 30 seconds instead of 3 hours.

---

## 🎯 Live Demo Scenario — Vardhaman Infra

> **Company:** Vardhaman Infra & Logistics Pvt. Ltd.  
> **Loan Request:** ₹60 Crore Term Loan  
> **Submitted Documents:** 4 PDFs — GST Returns, Bank Statement, Annual Report FY24, ITR FY24

### What the documents say (clean on the surface):
- Revenue: ₹340 Cr (18% YoY growth)
- DSCR: 1.6x (above RBI minimum of 1.25x)
- GST compliance: regular filer, no defaults

### ✅ Base XGBoost Score: **78/100 → APPROVE**

### 🔍 What our Research Agent then finds:
| Finding | Source | Severity |
|---|---|---|
| Director Kavita Mehta (DIN 07284531) disqualified since Sept 2023 — Section 164(2) | MCA21 | 🔴 HIGH |
| 4 NCLT cases IB/234/MB — not disclosed in application | e-Courts | 🔴 HIGH |
| Active Axis Bank charge (₹20 Cr) not mentioned in submitted docs | MCA21 Charge Registry | 🔴 HIGH |
| 2 sister companies struck off for non-filing under same directors | MCA21 | 🟡 MEDIUM |
| NHAI penalty notice reported in Business Standard | News/Web | 🟡 MEDIUM |
| GST-bank credit mismatch: 12% discrepancy in Q3 FY24 | GSTR-1 vs Bank | 🔴 HIGH |

### ⚠️ After Jury Deliberation: **51/100 → CONDITIONAL APPROVAL**

**Final Verdict:**
- **Recommended Amount:** ₹35 Cr (vs ₹60 Cr requested)
- **Interest Rate:** 12.5% p.a.
- **Tenor:** 60 months
- **Conditions:**
  1. DIN regularisation for Director K. Mehta within 90 days of sanction
  2. Resolution of NCLT Case IB/1234/MB/2024 before first disbursement
  3. NOC from NHAI regarding project delay penalty
  4. Additional collateral cover ratio maintained at minimum 1.5x

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTELLI-CREDIT PIPELINE                     │
└─────────────────────────────────────────────────────────────────────┘

  📄 DOCUMENTS                   🔍 INGESTION ENGINE
  ┌──────────────┐               ┌──────────────────────────────────┐
  │ GST Returns  │──────────────▶│  PyMuPDF + EasyOCR + Camelot    │
  │ Bank Stmts   │               │  Text Extraction & OCR           │
  │ Annual Rpts  │               ├──────────────────────────────────┤
  │ ITR, Legal   │               │  LLM Document Classifier         │
  └──────────────┘               ├──────────────────────────────────┤
                                 │  GST Reconciler (GSTR-1 vs Bank) │
                                 ├──────────────────────────────────┤
                                 │  RAG Pipeline (Qdrant + MiniLM)  │
                                 └────────────────┬─────────────────┘
                                                  │
                                                  ▼
  🌐 RESEARCH AGENT                      🔎 External Intelligence
  ┌──────────────────────────────────────────────────────────────┐
  │  MCA21 Crawler     → Director DINs, charges, struck-off cos  │
  │  Legal Intel       → e-Courts, NCLT, DRT case search         │
  │  Web Crawler       → News, SEBI orders, regulatory notices    │
  │  Promoter Graph    → Director network across all companies    │
  └────────────────────────────────┬─────────────────────────────┘
                                   │
                                   ▼
  👤 HUMAN IN THE LOOP          📋 Credit Officer Review
  ┌──────────────────────────────────────────────────────────────┐
  │  Risk Flags Dashboard   → Colour-coded by severity           │
  │  Five Cs Gauges         → Visual score breakdown             │
  │  Qualitative Input Form → Site visit / RCU findings          │
  └────────────────────────────────┬─────────────────────────────┘
                                   │
                                   ▼
  ⚖️  AI AGENT JURY                        Adversarial Deliberation
  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────┐
  │ PROSECUTOR  │  │  DEFENDER   │  │         JUDGE            │
  │ Risk Agent  │  │ Advocacy Ag.│  │  Adjudication Agent      │
  │ Max -25 pts │  │ Max +15 pts │  │  Weighs both sides       │
  └──────┬──────┘  └──────┬──────┘  └────────────┬─────────────┘
         └────────────────┴──────────────────────┘
                                   │
                                   ▼
  📊 SCORING ENGINE             XGBoost + SHAP
  ┌──────────────────────────────────────────────────────────────┐
  │  Five Cs Feature Vector  →  XGBoost Model  →  SHAP Values    │
  │  Base Score + Jury Delta → Final Score → Decision Threshold  │
  └────────────────────────────────┬─────────────────────────────┘
                                   │
                                   ▼
  📝 CAM GENERATOR              Credit Appraisal Memo
  ┌──────────────────────────────────────────────────────────────┐
  │  python-docx Word Report  +  Matplotlib Charts               │
  │  Radar Chart · Score Journey · GST vs Bank Credits           │
  └──────────────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────────────┐
  │  🔐 PRIVACY LAYER (Optional)                                 │
  │  TenSEAL CKKS Homomorphic Encryption on financial ratios     │
  │  Scoring model never receives plaintext financial data        │
  └──────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology | Purpose |
|---|---|---|
| **Backend** | Python 3.13, FastAPI | API server, WebSocket pipeline, orchestration |
| **Document Parsing** | PyMuPDF, EasyOCR, Camelot | PDF text extraction, OCR for scanned docs, table parsing |
| **ML & Scoring** | XGBoost 2.1, SHAP | Credit scoring with per-feature explainability |
| **LLM** | Anthropic Claude Sonnet 4 | Jury agents, risk extraction, document classification |
| **Embeddings** | all-MiniLM-L6-v2 | Semantic search over document chunks |
| **Vector DB** | Qdrant | RAG pipeline storage and retrieval |
| **Database** | PostgreSQL / SQLite | Risk flags, sessions, full audit trail |
| **Frontend** | React 18, Recharts | Dashboard, live pipeline progress, visualisations |
| **Privacy** | TenSEAL CKKS | Homomorphic encryption on the scoring layer |
| **Containers** | Docker Compose | One-command service orchestration |

---

## 📋 Prerequisites — What to Install First

Before you begin, install the following. Click each link to download:

| Tool | Version | Download | Notes |
|---|---|---|---|
| **Python** | 3.11+ | [python.org/downloads](https://www.python.org/downloads/) | ⚠️ **Tick "Add Python to PATH"** during install or nothing will work |
| **Node.js** | 20+ | [nodejs.org](https://nodejs.org) | Includes npm automatically |
| **Docker Desktop** | Latest | [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) | Required for Qdrant vector database |
| **Git** | Latest | [git-scm.com](https://git-scm.com) | For cloning the repo |
| **VS Code** (recommended) | Latest | [code.visualstudio.com](https://code.visualstudio.com) | Best editor for this project |

> 💡 **After installing Python**, open a new terminal and run `python --version` to confirm it works. You should see `Python 3.11.x` or higher.

---

## 🚀 Getting Started

Follow these steps exactly, in order. Every step is numbered. Don't skip any.

### Step 1 — Clone the Repository

Open a terminal (Command Prompt or PowerShell on Windows, Terminal on Mac/Linux) and run:

```bash
git clone https://github.com/Om-Agarwal-25/Intelli-Credit.git
cd Intelli-Credit
```

### Step 2 — Create a Python Virtual Environment

A virtual environment keeps this project's packages separate from everything else on your computer.

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> ✅ **How do you know it worked?** You'll see `(venv)` at the start of your terminal line, like this: `(venv) C:\Projects\Intelli-Credit>`

> ⚠️ **Windows only — if `activate` fails** with a permissions error, run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

### Step 3 — Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

> ⏳ This takes **5–10 minutes**. You'll see many packages downloading. Let it run — do not close the terminal.

### Step 4 — Install Frontend Dependencies

Open a **new terminal window** (keep the backend one open), then:

```bash
cd Intelli-Credit/frontend
npm install
```

> ⏳ This takes **2–3 minutes**. Again, let it run.

### Step 5 — Configure Environment Variables

```bash
# From the project root (Intelli-Credit/)
cp .env.example .env
```

Now open the `.env` file in VS Code and fill in these values:

```env
# REQUIRED — Get your key at https://console.anthropic.com
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Set to anthropic (or openai if you prefer GPT-4)
LLM_PROVIDER=anthropic

# Leave everything below as-is for local development
DEMO_MODE=true
DATABASE_URL=sqlite:///./intelli_credit.db
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

> 🔑 **Where do I get an API key?**
> - Anthropic: [console.anthropic.com](https://console.anthropic.com) → Create account → API Keys → Create Key
> - OpenAI: [platform.openai.com](https://platform.openai.com) → API Keys → Create new secret key

### Step 6 — Start Qdrant Vector Database

Qdrant stores the document embeddings for semantic search. Make sure Docker Desktop is running, then:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

> 🔴 **Leave this terminal running.** Open a new terminal for the next steps. If you close this, the RAG pipeline won't work (the app will fall back to rule-based analysis automatically).

### Step 7 — Generate Demo Documents

```bash
# From the backend/ directory (with venv active)
python demo_data/generate_demo_pdfs.py
```

> This creates the 4 synthetic Vardhaman Infra PDFs used in the demo. Takes about 10 seconds.

### Step 8 — Train the Scoring Model

```bash
# From the backend/ directory
python models/train_synthetic.py
```

> This generates synthetic credit data and trains the XGBoost model. Takes about 1 minute. You'll see `[MODEL] Saved to models/credit_scorer.pkl` when it's done.

### Step 9 — Start the Backend API

```bash
# From the backend/ directory (with venv active)
uvicorn main:app --reload --port 8000
```

> 🔴 **Leave this terminal running.** You'll see `Uvicorn running on http://0.0.0.0:8000`. Open a new terminal for the next step.

### Step 10 — Start the Frontend

```bash
# From the frontend/ directory
npm run dev
```

> ✅ The app will open automatically at **http://localhost:3000**

### Step 11 — Run the Demo

1. Go to **http://localhost:3000** in your browser
2. Click **"🎯 Load Vardhaman Infra Demo (4 PDFs)"** — this loads all demo documents instantly without a file picker
3. Watch the live pipeline run through all 10 stages
4. Click **"Proceed to Credit Review & Officer Input"** when the pipeline finishes
5. Fill in the qualitative input (or leave as-is) and click **"Submit & Start AI Jury Deliberation"**
6. Watch the Prosecutor, Defender, and Judge agents debate
7. See the final verdict and click **"Download CAM (.docx)"**

---

## 🐳 Running with Docker Compose (Easier Method)

If you want to start everything with a single command:

```bash
# 1. Copy and configure your environment file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Start everything
docker-compose up --build
```

The app will be available at **http://localhost:3000**. Qdrant, the backend, and the frontend all start automatically.

---

## 📁 Project Folder Structure

```
intelli-credit/
│
├── backend/
│   ├── main.py                         # FastAPI app — all API routes and WebSocket pipeline
│   ├── requirements.txt                # All Python dependencies (pip install -r this)
│   ├── test_all_modules.py             # Comprehensive unit tests — run with: py test_all_modules.py
│   │
│   ├── modules/
│   │   ├── ingestion/
│   │   │   ├── classifier.py           # LLM document type classifier (GST/Bank/Annual/etc.)
│   │   │   ├── extractor.py            # PyMuPDF + EasyOCR + Camelot PDF text extraction
│   │   │   ├── gst_reconciler.py       # GST fraud detection: GSTR-1 vs Bank, GSTR-2A vs 3B, round-tripping
│   │   │   ├── rag_pipeline.py         # Chunk documents, embed with MiniLM, store in Qdrant, semantic search
│   │   │   └── flag_store.py           # Persist risk flags to PostgreSQL with in-memory fallback
│   │   │
│   │   ├── research/
│   │   │   ├── entity_resolver.py      # Extract CIN, DIN, GSTIN from document text
│   │   │   ├── mca_crawler.py          # MCA21 API queries for company/director data (demo mock included)
│   │   │   ├── legal_intel.py          # e-Courts and NCLT case search (demo mock included)
│   │   │   ├── web_crawler.py          # News and web risk intelligence (demo mock included)
│   │   │   └── promoter_graph.py       # Build NetworkX director network graph across companies
│   │   │
│   │   ├── jury/
│   │   │   ├── five_cs.py              # Compute Five Cs (Character, Capacity, Capital, Collateral, Conditions)
│   │   │   ├── base_scorer.py          # XGBoost scoring + SHAP feature importance
│   │   │   ├── prosecutor.py           # Risk Scrutiny Agent — argues for rejection
│   │   │   ├── defender.py             # Credit Advocacy Agent — argues for approval
│   │   │   ├── judge.py                # Adjudication Agent — weighs both sides, delivers verdict
│   │   │   └── jury_engine.py          # Orchestrates Prosecutor + Defender (parallel) → Judge
│   │   │
│   │   └── cam/
│   │       ├── cam_generator.py        # python-docx Word document CAM builder
│   │       └── chart_generator.py      # Matplotlib: radar chart, GST vs Bank bar, score journey line
│   │
│   ├── models/
│   │   └── train_synthetic.py          # Generate synthetic Indian credit data + train XGBoost model
│   │
│   ├── privacy/
│   │   └── he_scorer.py                # TenSEAL CKKS homomorphic encryption scoring layer
│   │
│   ├── db/
│   │   ├── database.py                 # SQLAlchemy engine setup and session management
│   │   └── models.py                   # ORM models: Session, RiskFlag, AuditLog
│   │
│   └── demo_data/
│       ├── generate_demo_pdfs.py       # Creates all 4 Vardhaman Infra synthetic PDFs
│       └── vardhaman/                  # Pre-generated demo PDF documents
│           ├── vardhaman_annual_report_fy24.pdf
│           ├── vardhaman_bank_statement_fy24.pdf
│           ├── vardhaman_gstr1_fy24.pdf
│           └── vardhaman_itr_fy24.pdf
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                     # Main React app with React Router routing
│   │   ├── index.css                   # Global styles and design system tokens
│   │   │
│   │   ├── views/
│   │   │   ├── UploadPortal.jsx        # File upload screen with drag-and-drop and demo button
│   │   │   ├── ProcessingDashboard.jsx # Live pipeline progress with WebSocket updates
│   │   │   ├── ReviewInput.jsx         # Credit officer qualitative input form
│   │   │   └── JuryDecision.jsx        # Jury results, verdict display, and CAM download
│   │   │
│   │   └── components/
│   │       ├── FiveCsGauges.jsx        # Five Cs circular gauge visualisations
│   │       ├── RiskFlagsTable.jsx      # Colour-coded risk flags table by severity
│   │       ├── JuryDeliberationLog.jsx # Prosecutor vs Defender findings comparison table
│   │       └── ScoreJourney.jsx        # Line chart: Base Score → After Jury adjustment
│   │
│   ├── package.json                    # Frontend dependencies and npm scripts
│   └── vite.config.js                  # Vite build config with API proxy to backend
│
├── docker-compose.yml                  # One-command startup: Qdrant + Backend + Frontend
├── .env.example                        # Template for all environment variables
├── .gitignore                          # Files excluded from Git (venv, .env, models, etc.)
└── README.md                           # This file
```

---

## 📡 API Reference

All endpoints are prefixed with `/api`. Explore them interactively at **http://localhost:8000/docs**

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `POST` | `/api/sessions` | Create a new analysis session | `{ borrower_name, loan_amount_cr, loan_type }` |
| `POST` | `/api/sessions/{id}/upload` | Upload PDF documents to a session | `multipart/form-data` with `files[]` |
| `POST` | `/api/sessions/{id}/analyze` | Start the full analysis pipeline | — |
| `GET` | `/api/sessions/{id}` | Get session state and results | — |
| `POST` | `/api/sessions/{id}/qualitative` | Submit credit officer qualitative input | `{ observations: [...] }` |
| `POST` | `/api/sessions/{id}/jury` | Trigger AI Jury deliberation | — |
| `GET` | `/api/sessions/{id}/cam` | Download the CAM Word document | — |
| `POST` | `/api/demo/load-vardhaman` | Load all 4 demo PDFs instantly (no file picker) | — |
| `GET` | `/health` | System health check | — |
| `WS` | `/ws/{session_id}` | WebSocket: live pipeline stage updates | — |

---

## 📊 The Five Cs of Credit — How Scoring Works

The Five Cs is the standard framework used by Indian banks for credit appraisal, mandated in RBI guidelines. We compute each C from the extracted document data:

| Pillar | Weight | What we measure |
|---|---|---|
| **C1 — Character** | 25% | Promoter background, DIN disqualification status, disclosed vs undisclosed litigation, CIBIL/credit history signals |
| **C2 — Capacity** | 30% | Revenue trends (3-year CAGR), EBITDA margin, Debt Service Coverage Ratio, GST-to-bank credit match percentage |
| **C3 — Capital** | 15% | Net worth, gearing ratio (debt/equity), tangible equity buffer, retained earnings trend |
| **C4 — Collateral** | 20% | Type and quality of security offered, coverage ratio, Registrar of Companies charge status, mortgage validity |
| **C5 — Conditions** | 10% | Sector outlook, RBI regulatory signals, macro headwinds, government policy impact on the borrower's industry |

**Decision Thresholds (combined Base + Jury score):**

```
Score ≥ 65  →  ✅ APPROVE
Score 50–64 →  ⚠️ CONDITIONAL APPROVAL (with specific conditions)
Score < 50  →  ❌ REJECT
```

Each flag raised deducts points from the relevant C. A DIN disqualification, for example, caps C1 (Character) at 10/100 regardless of other indicators — consistent with RBI's stance that regulatory compliance is non-negotiable.

---

## 🔐 Privacy & Security

### Homomorphic Encryption Layer (TenSEAL CKKS)

One of the hardest problems in AI-assisted banking is **data sovereignty**: banks cannot legally send sensitive corporate financials to a third-party cloud model. Our homomorphic encryption layer solves this.

**In plain English:** The financial ratios (DSCR, gearing, revenue growth, GST match) are encrypted *before* they reach the scoring model. The model performs arithmetic on the encrypted numbers and returns an encrypted score, which is decrypted only on your local server. The model *never* sees the raw numbers.

**Technical details:**
- **Scheme:** CKKS (Cheon-Kim-Kim-Song) — designed for approximate arithmetic on real numbers
- **Library:** Microsoft TenSEAL (Python bindings for SEAL)
- **Polynomial modulus:** 8192 degree, 60-40-40-60 coefficient modulus
- **Fallback:** If TenSEAL is not installed, scoring runs in plaintext with a compliance badge showing the difference

**Compliance benefits:**
- ✅ RBI Data Localisation — all processing stays on-premise
- ✅ GDPR compliant — no raw financial data sent to external APIs
- ✅ Full audit trail for RBI inspection
- ✅ Zero raw financial data exposure to the AI scoring layer

---

## 🔧 Environment Variables Reference

| Variable | Required | Description | Where to get it |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | **Yes** | Claude API key for all LLM calls | [console.anthropic.com](https://console.anthropic.com) |
| `OPENAI_API_KEY` | Optional | OpenAI fallback if no Anthropic key | [platform.openai.com](https://platform.openai.com) |
| `LLM_PROVIDER` | **Yes** | Set to `anthropic` or `openai` | Set manually |
| `PRIMARY_MODEL` | Optional | Claude model for jury agents | Default: `claude-sonnet-4-20250514` |
| `FAST_MODEL` | Optional | Claude model for classification | Default: `claude-haiku-4-20250514` |
| `DEMO_MODE` | Optional | Use mock MCA/legal data | Default: `true` — set to `false` for live API calls |
| `DATABASE_URL` | **Yes** | Database connection string | Default: `sqlite:///./intelli_credit.db` |
| `QDRANT_URL` | **Yes** | Qdrant vector DB URL | Default: `http://localhost:6333` |
| `SERP_API_KEY` | Optional | SerpAPI for live news search | [serpapi.com](https://serpapi.com) |
| `SECRET_KEY` | **Yes** | App secret for sessions | Change to any random string |

---

## 🛠️ Troubleshooting

<details>
<summary><b>❌ venv\Scripts\activate is not recognized (Windows)</b></summary>

Run this in PowerShell as Administrator, then try again:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
</details>

<details>
<summary><b>❌ pip install fails on camelot-py</b></summary>

Camelot needs Ghostscript for PDF table extraction. Install it first:
1. Download Ghostscript from [ghostscript.com](https://ghostscript.com/releases/gsdnld.html)
2. Install it, then restart your terminal
3. Then run: `pip install camelot-py[cv]`
</details>

<details>
<summary><b>❌ EasyOCR installation fails</b></summary>

EasyOCR requires PyTorch. Install them separately:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install easyocr
```
</details>

<details>
<summary><b>❌ Docker not found / Docker daemon not running</b></summary>

1. Install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)
2. **Restart your computer** after installation
3. Open Docker Desktop and wait for it to show "Engine running"
4. Then try `docker run ...` again
</details>

<details>
<summary><b>❌ Port 8000 already in use</b></summary>

Either stop the other process using port 8000, or run the backend on a different port:
```bash
uvicorn main:app --reload --port 8001
```
Then update `vite.config.js` to proxy to `http://localhost:8001`.
</details>

<details>
<summary><b>❌ Qdrant connection refused</b></summary>

Make sure the Qdrant Docker container is running in a separate terminal:
```bash
docker run -p 6333:6333 qdrant/qdrant
```
The app will work without Qdrant (falls back to rule-based flag extraction), but semantic search won't be available.
</details>

<details>
<summary><b>❌ Anthropic/OpenAI API error — 401 Unauthorized</b></summary>

Check your `.env` file:
1. There should be **no spaces** around the `=` sign: `ANTHROPIC_API_KEY=sk-ant-...` ✅ not `ANTHROPIC_API_KEY = sk-ant-...` ❌
2. The key should start with `sk-ant-` for Anthropic or `sk-` for OpenAI
3. Make sure you restarted the backend after editing `.env`
</details>

<details>
<summary><b>❌ XGBoost model not found</b></summary>

The scoring model needs to be trained first:
```bash
cd backend
python models/train_synthetic.py
```
You should see `[MODEL] Saved to models/credit_scorer.pkl` when it completes.
</details>

<details>
<summary><b>❌ "Demo PDFs not found" error when clicking the demo button</b></summary>

Generate the demo PDFs first:
```bash
cd backend
python demo_data/generate_demo_pdfs.py
```
</details>

---

## 👤 Team

Presented at **National Hackathon — IIT Hyderabad, March 2026**

| Name | Role |
|---|---|
| **Trupti Mahajan** | Research Module + GST Reconciliation Engine |
| **Aditya Kale** | AI Agent Jury + LLM Prompt Engineering |
| **Om Agarwal** | Backend Architecture + ML Pipeline |
| **Parth Pagare** | Frontend + UX + System Integration |

---

## 📚 References

1. Lundberg, S. M., & Lee, S. I. (2017). **A unified approach to interpreting model predictions.** *NeurIPS 2017.* — SHAP values for XGBoost explainability
2. Chen, T., & Guestrin, C. (2016). **XGBoost: A scalable tree boosting system.** *KDD 2016.* — Core scoring model
3. Lewis, P., et al. (2020). **Retrieval-Augmented Generation for knowledge-intensive NLP tasks.** *NeurIPS 2020.* — RAG pipeline architecture
4. Reserve Bank of India. (2023). **Master Circular — Income Recognition, Asset Classification and Provisioning.** *RBI/2023-24/09.* — Five Cs thresholds and DIN compliance rules
5. Gentry, C. (2009). **Fully homomorphic encryption using ideal lattices.** *STOC 2009.* — Theoretical basis for the HE scoring layer
6. GSTN. (2023). **GSTR-1, GSTR-2A and GSTR-3B Filing Framework and ITC Reconciliation Guidelines.** — GST reconciliation logic
7. Fan, J., & Vercauteren, F. (2012). **Somewhat Practical Fully Homomorphic Encryption.** — CKKS scheme implemented via TenSEAL

---

## 📄 License

```
MIT License

Copyright (c) 2026 Intelli-Credit Team — IIT Hyderabad Hackathon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

<div align="center">

**Built with ❤️ for Indian banking — because fraud is expensive and time matters.**

*Intelli-Credit is a research prototype. It is not a licensed financial advisory tool and should not be used as the sole basis for credit decisions.*

</div>