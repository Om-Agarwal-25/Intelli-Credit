# Intelli-Credit — Master Build Prompt
### AI-Powered Corporate Credit Appraisal System for Indian Mid-Market Lending
### National Hackathon Prototype — End-to-End Build Instructions

---

## OVERVIEW & CONTEXT

You are building **Intelli-Credit** — a complete AI-powered Corporate Credit Decisioning System for Indian banks evaluating mid-sized corporate loan applications. This is a national hackathon prototype. The goal is a fully working, demonstrable end-to-end pipeline that a judge can run live.

### The Problem Being Solved
Indian credit managers face a "Data Paradox" — more data than ever, but appraisals take 2–4 weeks because data is scattered across incompatible sources, unstructured documents, and external intelligence that must be manually gathered. The current process is slow, biased, and routinely misses early warning signals buried in unstructured text. India's largest banking frauds (ABG Shipyard ₹22,000 Cr, DHFL, IL&FS, Videocon) all contained detectable signals that were never connected.

### What Intelli-Credit Does
Ingests raw, multi-format financial documents → autonomously researches the borrower across Indian government databases → runs a multi-agent adversarial jury deliberation → outputs a professional Credit Appraisal Memo (CAM) with a lending decision, loan amount, interest rate, and full plain-English reasoning — in under 5 minutes.

### The Novel Feature (Most Important)
The **AI Agent Jury** is the core differentiator. Instead of a single AI making a credit recommendation (which can be confidently wrong), three specialist agents debate the application adversarially. Their disagreement is itself information — it surfaces exactly where uncertainty lives and prevents both over-approval and over-rejection. No existing credit system does this.

### Evaluation Criteria Alignment (Judges Will Score On These 4 Axes)
1. **Extraction Accuracy** — How well does the system extract data from messy, scanned Indian-context PDFs?
2. **Research Depth** — Does the engine find relevant local news, MCA filings, court records not in the submitted documents?
3. **Explainability** — Can the AI walk a judge through its reasoning step by step, or is it a black box?
4. **Indian Context Sensitivity** — Does it understand GSTR-2A vs 3B reconciliation, CIBIL Commercial, MCA filings, e-Courts?

Every module below must visibly serve at least one of these four criteria.

---

## SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        INTELLI-CREDIT                           │
│                                                                 │
│  [Document Upload]                                              │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │           MODULE 1: DATA INGESTION ENGINE               │   │
│  │  Upload & Classify → Extract → Cross-Reference →        │   │
│  │  RAG Pipeline → Risk Flag Store                         │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                             │ risk_flags table                  │
│       ┌─────────────────────┼──────────────────────┐           │
│       │                     │                      │           │
│       ▼                     ▼                      │           │
│  ┌──────────────┐   ┌───────────────────┐          │           │
│  │  MODULE 2:   │   │   HUMAN-IN-LOOP   │          │           │
│  │  AI RESEARCH │   │  Credit Officer   │          │           │
│  │  AGENT       │   │  Qualitative Input│          │           │
│  └──────┬───────┘   └────────┬──────────┘          │           │
│         │ research_flags     │ qualitative_flags    │           │
│         └──────────┬─────────┘                      │           │
│                    ▼                                │           │
│  ┌─────────────────────────────────────────────┐   │           │
│  │         MODULE 3: AI AGENT JURY             │   │           │
│  │  Base XGBoost Score                         │   │           │
│  │       ↓                                     │   │           │
│  │  Risk Scrutiny Agent (Prosecutor)           │   │           │
│  │  Credit Advocacy Agent (Defender)           │   │           │
│  │  Adjudication Agent (Judge)                 │   │           │
│  │       ↓                                     │   │           │
│  │  Jury Consensus Score + Verdict             │   │           │
│  └──────────────────┬──────────────────────────┘   │           │
│                     │                               │           │
│                     ▼                               │           │
│  ┌─────────────────────────────────────────────┐   │           │
│  │       MODULE 4: CAM GENERATOR               │   │           │
│  │  Five Cs Report + Decision + .docx Output   │   │           │
│  └─────────────────────────────────────────────┘   │           │
│                                                     │           │
│  ┌──────────────────────────────────────────────┐  │           │
│  │   PRIVACY LAYER: Homomorphic Encryption      │◄─┘           │
│  │   Structured scoring on encrypted data       │              │
│  └──────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

---

## TECH STACK

```
Backend Framework:    Python 3.11, FastAPI
Document Parsing:     PyMuPDF (fitz), EasyOCR, pytesseract, Camelot-py
ML & Scoring:         XGBoost, scikit-learn, SHAP
LLM (Primary):        Anthropic Claude claude-sonnet-4-20250514 via API
                      OR OpenAI GPT-4o — make provider configurable via env var
LLM (Classification): GPT-4o-mini or Claude Haiku (fast, cheap calls)
Embeddings:           sentence-transformers (all-MiniLM-L6-v2)
Vector Database:      Qdrant (run locally via Docker)
Relational Database:  PostgreSQL (risk_flags, research_flags, borrower, sessions)
Data Platform:        Databricks (for feature store and ML pipeline — integrate
                      via Databricks SDK, use Unity Catalog for data governance)
CAM Document Output:  python-docx, matplotlib (charts embedded in .docx)
Frontend:             React 18, Tailwind CSS, Recharts (for score visualisations)
Real-time Updates:    WebSockets (FastAPI native) for live pipeline progress
Containerisation:     Docker Compose (all services: API, Qdrant, PostgreSQL, frontend)
Privacy Layer:        Microsoft SEAL via Python bindings (tenseal) — apply to
                      structured scoring layer only, not LLM layer
Environment:          All API keys via .env — never hardcoded
```

---

## MODULE 1 — DATA INGESTION ENGINE

### Purpose
Convert raw, heterogeneous Indian financial documents into a structured, auditable risk flag store that every downstream module reads from.

### Stage 1 — Upload & Classify

Accept multi-file PDF upload. For each file:
- Extract first-page text using PyMuPDF
- Send to LLM (Claude Haiku or GPT-4o-mini) with prompt:
  ```
  Classify this document into exactly one of these categories based on the text:
  GST_RETURN, BANK_STATEMENT, ANNUAL_REPORT, LEGAL_DOC, ITR, RATING_REPORT, OTHER
  Return only the category label, nothing else.
  ```
- Display classification badge per file in the UI before processing begins
- Route each file to its dedicated sub-processor based on classification

### Stage 2 — Text Extraction

Handle three document types:
- **Clean digital PDFs** → PyMuPDF (`fitz.open()`) — fast, preserves layout
- **Scanned / image-based PDFs** → EasyOCR with `['en', 'hi']` language support (Hindi-English code-mixed documents are common in Indian corporate filings)
- **Complex financial tables** (GST schedules, P&L, balance sheets with merged cells, borderless tables) → Camelot with `flavor='lattice'` first, fall back to `flavor='stream'`

Detection logic: if PyMuPDF extracts fewer than 100 characters from a page, treat it as scanned and route to OCR.

### Stage 3 — Structured Financial Cross-Reference (Indian Context Critical)

This stage specifically addresses the Indian fraud patterns judges will test for.

**GSTR-1 vs Bank Statement Reconciliation:**
- Extract monthly turnover figures from GSTR-1 (Table 4 — taxable outward supplies)
- Extract monthly credit totals from bank statement for the same period
- For each month: `discrepancy_ratio = (gst_declared - bank_credits) / gst_declared`
- Flag `REVENUE_INFLATION` if discrepancy_ratio > 0.60 for 2+ consecutive months
- Flag `PRE_LOAN_CASH_STUFFING` if bank credits spike >40% in the 1–2 months immediately before the application date with no corresponding GST increase

**GSTR-2A vs GSTR-3B Reconciliation (India-Specific, Judges Will Test This):**
- GSTR-2A = what your vendors actually filed (auto-populated from vendor filings)
- GSTR-3B = what you claimed as Input Tax Credit (self-declared)
- Extract ITC claimed from GSTR-3B (Table 4A)
- Extract ITC available from GSTR-2A
- If GSTR-3B ITC claimed > GSTR-2A ITC available by >15% → flag `FAKE_ITC_CLAIM`
- This is the single most common GST fraud signal in India — judges from banking background will specifically look for this

**Round-Tripping Detection:**
- Parse bank statement for transactions: if the same amount (±2%) appears as both credit and debit within 48 hours → flag `ROUND_TRIPPING`
- Apply to amounts >₹10 lakh only to avoid noise

**Circular Trading Detection:**
- Extract vendor GSTINs from GST input schedule
- Check if any vendor GSTIN also appears as a customer GSTIN in the output schedule
- Flag `CIRCULAR_TRADING` if same GSTIN appears on both sides

### Stage 4 — RAG Pipeline (Semantic Risk Extraction from Unstructured Documents)

For annual reports, board minutes, rating reports, legal notices:

**Chunking:**
- Split text into 512-token chunks with 50-token overlap (overlap prevents context loss at section boundaries)
- Preserve document name and page number as metadata per chunk

**Embedding:**
- Embed all chunks using `sentence-transformers/all-MiniLM-L6-v2`
- Store vectors + metadata in Qdrant collection named `borrower_{session_id}`

**Semantic Risk Queries (run all, not keyword search):**
```python
risk_queries = [
    "going concern doubt or ability to continue as going concern",
    "auditor qualification or modified opinion or emphasis of matter",
    "litigation legal proceedings disputes court cases",
    "related party transactions loans to directors or promoters",
    "capacity utilisation operating below capacity plant idle",
    "debt restructuring or loan renegotiation or moratorium",
    "pledged shares promoter shareholding decline",
    "contingent liabilities guarantees off balance sheet",
    "NCLT insolvency resolution proceedings",
    "RBI regulatory action penalty or show cause notice"
]
```

For each query:
- Retrieve top-5 matching chunks via cosine similarity
- Pass to Claude/GPT-4o with prompt:
  ```
  You are a credit risk analyst. The following text is from a corporate financial document.
  Extract any risk flags related to: {query}
  For each flag found, output JSON: {"flag_text": "exact quote", "risk_category": "...",
  "severity": "HIGH/MEDIUM/LOW", "page_hint": "..."}
  If no relevant risk found, return empty array [].
  Return only valid JSON, no other text.
  ```

### Stage 5 — Risk Flag Consolidation

Write all flags to PostgreSQL `risk_flags` table:
```sql
CREATE TABLE risk_flags (
    flag_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL,
    flag_type VARCHAR(50) NOT NULL,
    severity VARCHAR(10) CHECK (severity IN ('HIGH', 'MEDIUM', 'LOW')),
    source_document VARCHAR(255),
    evidence_snippet TEXT,
    page_reference VARCHAR(50),
    source_module VARCHAR(50), -- 'STRUCTURED', 'RAG', 'RESEARCH', 'QUALITATIVE'
    created_at TIMESTAMP DEFAULT NOW()
);
```

Every downstream module — scoring, jury, CAM — reads exclusively from this table. Nothing is passed directly between modules.

---

## MODULE 2 — AI RESEARCH AGENT

### Purpose
Find what the borrower didn't disclose. Go beyond submitted documents to crawl Indian government databases, court records, and web sources autonomously.

### Why This Is Different From Standard Search
Standard search does keyword matching — searching "Reliance" returns everything about every Reliance entity. Our agent does entity-level semantic search — it first resolves the exact legal entity (CIN, DIN numbers) and then searches using those identifiers, not just names. It reads court dockets and MCA filing histories, not just news headlines.

### Entity Resolution (Always Run First)

Extract from uploaded documents:
- Company name (exact legal name as per MCA)
- CIN if present in any document
- GSTIN if present
- Director names if present in annual report

If CIN not found: call MCA API `/api/v1/company/search?companyName={name}` to resolve to canonical CIN. This is the anchor identity for all subsequent searches.

### Research Task 1 — MCA21 Intelligence

Using resolved CIN and director DINs, call MCA public APIs:

```python
# Company master data
GET https://www.mca.gov.in/MCAGateway/api/v1/company/{cin}/masterdata

# Director list
GET https://www.mca.gov.in/MCAGateway/api/v1/company/{cin}/directors

# For each director DIN — check disqualification
GET https://www.mca.gov.in/MCAGateway/api/v1/director/{din}/disqualification

# Charge registry (existing loans registered against company assets)
GET https://www.mca.gov.in/MCAGateway/api/v1/company/{cin}/charges

# Companies where same director appears (promoter network)
GET https://www.mca.gov.in/MCAGateway/api/v1/director/{din}/companies
```

Flag if:
- Any director DIN is disqualified under Section 164(2) Companies Act → `HIGH` severity
- Any linked company (same director) is struck off, under NCLT, or has active charges → `MEDIUM`
- Company has undisclosed registered charges (loans) not mentioned in submitted documents → `HIGH`
- Company address matches a struck-off entity's address → `MEDIUM`

Note: If MCA APIs are rate-limited during demo, implement a mock layer that returns realistic synthetic data for the demo company (Vardhaman Infra).

### Research Task 2 — Legal Intelligence

**e-Courts Portal:**
- Search `https://ecourts.gov.in/ecourts_home/` for cases by company name and CIN
- Extract: case number, filing date, petitioner/respondent, claim amount, current status
- Flag any case where company or director is respondent/defendant → severity based on claim amount (>₹1 Cr = HIGH, ₹10L–₹1 Cr = MEDIUM)

**NCLT/NCLAT:**
- Search National Company Law Tribunal cause list for company name
- Flag any insolvency petition, winding-up petition, or Section 7/9/10 IBC filing

**RBI Defaulter Lists:**
- Check against RBI published wilful defaulter list (publicly available PDF — parse and index it once at startup)
- Check CIBIL Commercial proxy: if CIBIL Commercial score data available via API, fetch it; else note as "requires manual verification"

### Research Task 3 — Web & News Intelligence

Run semantic web searches using the Anthropic API's web search tool or SerpAPI:

```python
search_queries = [
    f"{company_name} fraud default penalty",
    f"{company_name} NHAI NCLT insolvency",
    f"{promoter_name} CBI ED arrest case",
    f"{company_name} GST notice tax evasion",
    f"{sector} RBI regulation 2024 2025",  # sector-level regulatory risk
    f"{sector} India headwinds outlook 2025"
]
```

For each result:
- Extract article title, date, source, summary
- Pass to LLM to assess relevance and severity
- Only flag articles from last 36 months
- Weight recent articles (last 6 months) higher

### Research Task 4 — Promoter Knowledge Graph

Build a simple graph using the MCA director data:

```python
# Nodes: companies and directors
# Edges: directorship relationships

graph = {
    "nodes": [
        {"id": cin, "type": "company", "status": "active/struck_off/under_nclt"},
        {"id": din, "type": "director", "status": "active/disqualified"}
    ],
    "edges": [
        {"from": din, "to": cin, "relationship": "director"}
    ]
}

# Risk scoring for graph:
# - Direct NPA connection (1 hop) → HIGH
# - Struck-off company in network → MEDIUM  
# - 10+ companies under one promoter → flag for investigation
```

Display as a simple visual graph in the UI (use React Flow or D3 force layout).

### Human-in-the-Loop Qualitative Input

After research completes, present the Credit Officer with an input form:

```
Factory Utilisation Observed: [__]% (slider 0–100)
Management Interview Impression: [Confident / Mixed / Evasive] (dropdown)
Promoter Reputation Assessment: [Strong / Neutral / Concerning] (dropdown)  
Site Visit Notes: [free text area]
Any Other Observations: [free text area]
```

**LLM Parsing of Free Text:**
Send free-text inputs to LLM with prompt:
```
You are a credit risk system. Parse this site visit observation and map it to credit risk adjustments.
Observation: "{text}"
Output JSON: [{"observation": "...", "five_c_pillar": "C1/C2/C3/C4/C5",
"score_delta": number_between_-15_and_+15, "reasoning": "one sentence"}]
Return only valid JSON.
```

**Score Cap:** Total qualitative adjustment capped at ±25 points across all inputs combined. Show the officer each adjustment before they confirm. Log all qualitative inputs with officer ID and timestamp for audit trail.

---

## MODULE 3 — AI AGENT JURY

### Purpose
The core novel feature. After the base model scores the borrower, three specialist AI agents independently challenge the score from opposing perspectives. Their structured debate produces a more robust, explainable, and auditable final recommendation than any single model could.

### Why This Beats a Single AI
| Single AI Model | AI Agent Jury |
|---|---|
| One perspective — can be confidently wrong | Three views — disagreement is visible |
| Black box score with no reasoning | Full auditable argument trail in CAM |
| Bias baked into one model's training | Adversarial prompting structurally cancels bias |
| Binary: approve or reject | Confidence band: uncertainty zones explicitly flagged |

### Step 1 — Base Score (XGBoost)

Compute Five Cs scores from all flags in `risk_flags` table:

**C1 — Character (weight: 25%)**
- Inputs: litigation flags, DIN disqualification status, promoter graph risk, news sentiment score, years in business, auditor qualification flags
- Score 0–100 (100 = excellent character, 0 = severe red flags)

**C2 — Capacity (weight: 30%)**
- Inputs: revenue trend (3yr CAGR), EBITDA margin, DSCR (Debt Service Coverage Ratio), working capital cycle, GST-bank match percentage
- DSCR formula: `Net Operating Income / Total Debt Service`
- Score 0–100

**C3 — Capital (weight: 15%)**
- Inputs: net worth, gearing ratio (debt/equity), equity buffer vs loan amount, promoter contribution
- Score 0–100

**C4 — Collateral (weight: 20%)**
- Inputs: asset type (immovable property > plant & machinery > stock), estimated market value, haircut percentage, ROC charge registration status
- Score 0–100

**C5 — Conditions (weight: 10%)**
- Inputs: sector outlook score (from news/regulatory research), active RBI circulars affecting sector, macro environment signals, PLI scheme eligibility
- Score 0–100

**Composite Formula:**
```python
composite = (C1*0.25) + (C2*0.30) + (C3*0.15) + (C4*0.20) + (C5*0.10)
```

Train XGBoost on synthetic Indian NPA dataset (generate 1000 synthetic samples with realistic distributions — include known NPA patterns: DSCR < 1.0, high litigation, DIN disqualification, GST mismatch). Use SHAP to explain every prediction.

### Step 2 — Agent 1: Risk Scrutiny Agent (The Prosecutor)

**System Prompt:**
```
You are an adversarial senior credit risk officer with 20 years of experience 
investigating Indian corporate fraud. You have personally reviewed the NPA files 
of ABG Shipyard, DHFL, IL&FS, Videocon, and Kingfisher Airlines. You know every 
pattern fraudsters use — related party diversion, circular trading, pre-loan cash 
stuffing, nominee directors hiding DIN disqualification, inflated receivables.

Your ONLY job is to find every possible reason this loan application should be 
REJECTED. Assume the borrower is hiding something until proven otherwise. Be 
aggressive. Surface contradictions between data sources. Find the worst-case 
scenario. Do not be fair — the Defender Agent will handle the positive case.

You will receive: Five Cs scores, all risk flags with evidence, research findings, 
financial summary, and qualitative inputs.

Output ONLY valid JSON in this exact format:
{
  "prosecution_findings": [
    {
      "finding_id": "P1",
      "finding_text": "one clear sentence describing the risk",
      "five_c_pillar": "C1/C2/C3/C4/C5",
      "score_delta": -12,  // negative number, max -20 per finding
      "evidence_source": "MCA21 / e-Courts / GSTR-2A / Annual Report p.34 / etc",
      "severity": "HIGH/MEDIUM"
    }
  ],
  "total_prosecution_delta": -27  // sum of all score_deltas
}
```

**Pass to Agent 1:**
- Five Cs individual scores and composite
- All entries from `risk_flags` table (full evidence_snippet included)
- All entries from `research_flags` table
- Financial summary: revenue, DSCR, gearing ratio, GST match %
- Qualitative inputs from Credit Officer

### Step 3 — Agent 2: Credit Advocacy Agent (The Defender)

**System Prompt:**
```
You are a relationship manager and credit advocate at a leading Indian private bank. 
You deeply believe in supporting Indian businesses and the growth story of the 
Indian economy. You understand that numbers alone don't tell the full story.

Your ONLY job is to find every legitimate reason this loan application should be 
APPROVED. Find the strengths. Find the growth narrative. Compare favourably against 
sector benchmarks. Provide context that makes concerning signals less alarming — 
if the sector is under stress, a single company's stress is not a character flaw. 
Do not be cautious — the Risk Scrutiny Agent will handle the negative case.

Output ONLY valid JSON in this exact format:
{
  "defence_findings": [
    {
      "finding_id": "D1",
      "finding_text": "one clear sentence describing the strength",
      "five_c_pillar": "C1/C2/C3/C4/C5",
      "score_delta": +8,  // positive number, max +15 per finding
      "evidence_source": "GST Returns / Bank Statement / Annual Report / Sector Data",
      "confidence": "HIGH/MEDIUM"
    }
  ],
  "total_defence_delta": +14
}
```

**Pass to Agent 2:** Same data as Agent 1.

### Step 4 — Agent 3: Adjudication Agent (The Judge)

**System Prompt:**
```
You are the Chairman of the Credit Committee at a major Indian scheduled commercial 
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
  "accepted_prosecution_findings": ["P1", "P3"],  // finding_ids you accept
  "rejected_prosecution_findings": ["P2"],         // with brief reason
  "accepted_defence_findings": ["D1", "D2"],
  "rejected_defence_findings": [],
  "decisive_factors": ["one sentence each — the 2-3 things that swung the decision"],
  "final_recommendation": "APPROVE / CONDITIONAL / REJECT",
  "recommended_loan_amount_cr": 35,
  "recommended_interest_rate_pct": 12.5,
  "loan_tenor_months": 60,
  "conditions": [
    "DIN regularisation for Director K. Mehta within 90 days",
    "Resolution of NCLT Case No. 1842/2024 before first disbursement"
  ],
  "confidence_band_low_cr": 30,
  "confidence_band_high_cr": 40,
  "primary_reason": "one sentence — the single most important reason for this decision",
  "verdict_rationale": "2-3 sentences explaining the decision in plain English"
}
```

**Pass to Agent 3:**
- All data passed to Agents 1 and 2
- Agent 1's complete prosecution_findings JSON
- Agent 2's complete defence_findings JSON

### Step 5 — Final Jury Score Calculation

```python
base_score = xgboost_composite_score  # 0-100

# Apply accepted prosecution deltas only (Judge accepted findings)
prosecution_delta = sum(f.score_delta for f in accepted_prosecution_findings)

# Apply accepted defence deltas only
defence_delta = sum(f.score_delta for f in accepted_defence_findings)

# Apply qualitative officer input delta
qualitative_delta = sum of officer input score adjustments (capped at ±25)

# Net delta capped at ±30 to prevent extreme swings
net_delta = max(-30, min(30, prosecution_delta + defence_delta + qualitative_delta))

jury_score = base_score + net_delta

# Decision thresholds
if jury_score >= 65:    decision = "APPROVE"
elif jury_score >= 50:  decision = "CONDITIONAL"
else:                   decision = "REJECT"
```

### Step 6 — Jury Deliberation Log Display

Render in the frontend as a clean table:

```
┌─────────────────────────────────────────────────────────────────────┐
│ JURY DELIBERATION LOG — Vardhaman Infra & Logistics Pvt. Ltd.       │
├──────────────────────┬──────────────────────────────┬───────────────┤
│ [pale red bg]        │                              │               │
│ 🔴 Risk Scrutiny    │ Director DIN disqualified —  │ − 15 pts · C1 │
│    Agent            │ company running under nominee │               │
│                     │ MCA21 · DIN 07284531 · Not   │               │
│                     │ disclosed                    │               │
├──────────────────────┼──────────────────────────────┼───────────────┤
│ [pale red bg]        │                              │               │
│ 🔴 Risk Scrutiny    │ 4 NCLT cases undisclosed —   │ − 12 pts · C1 │
│    Agent            │ self-declared "no litigation"│               │
├──────────────────────┼──────────────────────────────┼───────────────┤
│ [pale green bg]      │                              │               │
│ 🟢 Credit Advocacy  │ Revenue verified — GST-bank  │ Confirmed · C2│
│    Agent            │ match 94% over 24 months     │               │
├──────────────────────┼──────────────────────────────┼───────────────┤
│ [pale blue bg]       │                              │               │
│ ⚖️ Adjudication     │ C1 failure decisive —        │ VERDICT       │
│    Agent            │ conditional at reduced limit │               │
├──────────────────────┴──────────────────────────────┴───────────────┤
│ [dark navy bar]                                                      │
│ Final Verdict → CAM Section 6    ✓ Conditional — ₹35 Cr @ 12.5%   │
└─────────────────────────────────────────────────────────────────────┘
```

Row colours: Risk Scrutiny = `#FFF4F4`, Credit Advocacy = `#F2FBF5`, Adjudication = `#F0F4FF`

---

## MODULE 4 — CAM GENERATOR

### Purpose
Produce a professional, structured Credit Appraisal Memo in Word format (.docx) that a real Indian bank credit committee would recognise as credible. Every claim must be sourced.

### CAM Structure (generate using python-docx)

```
CREDIT APPRAISAL MEMO
Intelli-Credit Automated Analysis System
Date: {date} | Session ID: {session_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 1 — BORROWER PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Company Name:        {legal_name}
CIN:                 {cin}
Sector / Industry:   {sector}
Registered Address:  {address}
Loan Amount Applied: ₹{amount} Crore
Loan Type:           {type}
Date of Application: {date}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 2 — EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RECOMMENDATION: {APPROVE / CONDITIONAL APPROVAL / REJECT}
• {decisive_factor_1}
• {decisive_factor_2}  
• {decisive_factor_3}
{verdict_rationale from Adjudication Agent}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 3 — FIVE Cs ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[One subsection per C with: score out of 100, key inputs, flags raised, evidence]

C1 CHARACTER — Score: {c1_score}/100
  Promoter Background: {summary}
  Litigation Status:   {summary}
  CIBIL Commercial:    {score or "Manual Verification Required"}
  Key Flags:           {list of C1 flags with severity}

C2 CAPACITY — Score: {c2_score}/100
  Revenue (3yr):  {table}
  EBITDA Margin:  {value}
  DSCR:           {value}
  GST-Bank Match: {percentage}%
  [Embed matplotlib bar chart: GST Declared vs Bank Credits, 24-month window]

C3 CAPITAL — Score: {c3_score}/100
  Net Worth:      ₹{value} Cr
  Gearing Ratio:  {value}
  Equity Buffer:  {value}

C4 COLLATERAL — Score: {c4_score}/100
  Primary Security:    {asset description}
  Estimated Value:     ₹{value} Cr
  Haircut Applied:     {percentage}%
  ROC Charge Status:   {registered/unregistered}
  Coverage Ratio:      {loan_amount / collateral_value}x

C5 CONDITIONS — Score: {c5_score}/100
  Sector Outlook:      {summary from research agent}
  Regulatory Risk:     {any active RBI circulars affecting sector}
  Macro Environment:   {brief note}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 4 — RESEARCH INTELLIGENCE FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Table: Source | Finding | Severity | Date Discovered]
{all research_flags rows where severity = HIGH or MEDIUM}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 5 — AI AGENT JURY DELIBERATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Base Model Score (XGBoost): {base_score}/100 → {base_decision}
Jury Consensus Score:       {jury_score}/100 → {jury_decision}
Score Movement:             {net_delta} points

PROSECUTION FINDINGS (Risk Scrutiny Agent):
[Table of accepted prosecution findings with score deltas]

DEFENCE FINDINGS (Credit Advocacy Agent):
[Table of accepted defence findings with score deltas]

ADJUDICATION RATIONALE:
{judge_verdict_rationale}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 6 — FINAL DECISION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Decision:              {CONDITIONAL APPROVAL}
Recommended Amount:    ₹{recommended_loan_amount_cr} Crore
                       (Applied: ₹{applied_amount_cr} Crore)
Confidence Band:       ₹{confidence_band_low}–{confidence_band_high} Crore
Interest Rate:         {recommended_interest_rate_pct}% p.a.
Tenor:                 {loan_tenor_months} months
Risk Premium Applied:  {rate - base_rate}% above base rate

CONDITIONS PRECEDENT:
1. {condition_1}
2. {condition_2}

COVENANTS (if any):
1. {covenant_1}

NEXT STEPS:
1. Credit Officer to verify conditions with borrower
2. Legal team to review collateral documentation  
3. Final sanction subject to Credit Committee ratification

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SECTION 7 — AUDIT TRAIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session ID:           {session_id}
Analysis Timestamp:   {timestamp}
Credit Officer ID:    {officer_id}
Documents Processed:  {list of uploaded files with hash}
AI Models Used:       {model names and versions}
Officer Overrides:    {any qualitative inputs with their score impact}

Note: This CAM was generated by Intelli-Credit AI system. All findings are 
traceable to source documents. Final credit decision requires authorised 
Credit Officer sign-off. AI recommendation is advisory only.
```

### Chart Generation

Use matplotlib to generate and embed in the .docx:
1. **GST vs Bank Credits bar chart** — 24-month dual bar, highlight anomaly months in red
2. **Five Cs radar/spider chart** — pentagon showing all 5 dimension scores
3. **Score journey chart** — horizontal bar: Base Score → After Prosecution → After Defence → Final Jury Score

---

## FRONTEND UI

### Design Language
Match the Intelli-Credit visual identity: white background, dark navy `#1B2B4B` headers, teal `#4A9DB5` accents, light blue `#EBF7FA` card backgrounds, Nunito font. Clean, professional, banking-grade.

### View 1 — Upload Portal

```
┌─────────────────────────────────────────────────┐
│  🏦 Intelli-Credit                              │
│  AI-Powered Credit Appraisal                    │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │     Drop documents here or click        │   │
│  │     to upload                           │   │
│  │                                         │   │
│  │  Accepted: PDF, scanned PDFs            │   │
│  │  Types: GST Returns, Bank Statements,   │   │
│  │  Annual Reports, Legal Docs, ITRs       │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  Uploaded Files:                                │
│  [filename.pdf]  [GST_RETURN ✓]   [Remove]     │
│  [filename.pdf]  [Classifying...] [Remove]      │
│  [filename.pdf]  [ANNUAL_REPORT ✓][Remove]      │
│                                                 │
│  [Begin Analysis →]                             │
└─────────────────────────────────────────────────┘
```

### View 2 — Live Processing Dashboard

Show real-time pipeline progress via WebSocket updates:

```
INGESTION PIPELINE                    RESEARCH AGENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━        ━━━━━━━━━━━━━━━━━━━━━
✅ Upload & Classify    0.8s          ✅ Entity Resolution  1.2s
✅ Text Extraction      3.2s          ✅ MCA21 Crawl        4.1s
✅ GST Cross-Reference  2.1s          🔄 Legal Intelligence  ...
   └ 2 flags raised                  ⏳ Promoter Graph
🔄 RAG Pipeline...                   ⏳ Web & News Crawl
⏳ Risk Consolidation

FLAGS FOUND SO FAR: 3 HIGH  ·  2 MEDIUM  ·  1 LOW
```

### View 3 — Review & Credit Officer Input

Three-panel layout:
- **Left:** Five Cs score gauges (circular progress per dimension)
- **Centre:** Risk flags table (colour-coded by severity, filterable)
- **Right:** Qualitative input form with live score preview

Show: "AI Base Score: 78/100 — APPROVE (before officer input and jury)"

### View 4 — Jury & Final Decision

```
BEFORE JURY                    AFTER JURY
Base Model Score               Jury Consensus Score
[78]  → APPROVE                [51]  → CONDITIONAL
                   
Without Jury: ₹60 Cr disbursed at full risk
With Jury: ₹35 Cr conditional · DIN regularisation required

JURY DELIBERATION LOG
[colour-coded table as described in Module 3]

[Download CAM as .docx]  [New Application]
```

---

## DEMO DATA — VARDHAMAN INFRA & LOGISTICS PVT. LTD.

Create synthetic demo documents that showcase the system catching a fraudulent-looking application. This is what runs during the live hackathon demo.

**Company Profile:**
- Name: Vardhaman Infra & Logistics Pvt. Ltd.
- CIN: U45200MH2015PTC264831 (synthetic)
- Sector: Infrastructure / Road Construction
- Location: Pune, Maharashtra
- Loan Applied: ₹60 Crore Term Loan for equipment purchase

**What the Submitted Documents Show (Clean on Surface):**
- Revenue ₹340 Cr (FY24), growing 18% YoY
- DSCR: 1.6x (healthy)
- GST-bank match: 94% (good) — except April and May where it drops to 37% (flag this)
- Audited financials — clean opinion (but going-concern footnote buried on page 34)
- Self-declared: no pending litigation

**What the Research Agent Finds (The Reveal):**
- Director K. Mehta, DIN 07284531 → DIN disqualified since September 2023 under Section 164(2) Companies Act → company running under nominee director → regulatory violation
- e-Courts District Court Pune: Case No. 1842/2024 → fraud complaint filed October 2024 by operational creditor → ₹4.2 Cr disputed → 3 hearings completed → never disclosed
- MCA21: Vardhaman Buildcon Pvt. Ltd. and Vardhaman Holdings LLP → same registered address → same directors → struck off for non-filing → capital diversion risk
- Economic Times November 2024: "Vardhaman Infra delays NHAI highway project handover" → NHAI penalty notice issued → project 14 months behind schedule

**The Demo's Key Moment:**
- Base XGBoost score: **78/100 → APPROVE** (loan would have been disbursed)
- Risk Scrutiny Agent: finds DIN disqualification (−15 pts, C1) + NCLT cases (−12 pts, C1)
- Credit Advocacy Agent: confirms revenue is real (+0 additional, already priced in)
- Adjudication Agent: "C1 failure is decisive per RBI guidelines — strong financials cannot offset disqualified director"
- Final Jury Score: **51/100 → CONDITIONAL**
- Verdict: ₹35 Cr (vs ₹60 Cr requested) at 12.5%, conditional on DIN regularisation within 90 days

**Files to Create for Demo:**
1. `vardhaman_gstr1_fy24.pdf` — synthetic GST return with April/May anomaly
2. `vardhaman_bank_statement_fy24.pdf` — synthetic bank statement
3. `vardhaman_annual_report_fy24.pdf` — synthetic annual report with going-concern footnote on page 34
4. `vardhaman_itr_fy24.pdf` — synthetic ITR

Generate these as realistic-looking PDFs using `reportlab` or similar. The going-concern footnote should say: *"The Company's ability to continue as a going concern is subject to resolution of the matters described in Note 31 — Contingent Liabilities."*

---

## PRIVACY & SECURITY LAYER

### Homomorphic Encryption (Apply to Structured Scoring Layer)

Apply Microsoft SEAL via `tenseal` Python library to the Five Cs numerical scoring:

```python
import tenseal as ts

# Create TenSEAL context
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=8192,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.generate_galois_keys()
context.global_scale = 2**40

# Encrypt financial ratios before scoring
plain_ratios = [dscr, gearing_ratio, revenue_growth, gst_match_pct]
encrypted_ratios = ts.ckks_vector(context, plain_ratios)

# XGBoost scoring happens on encrypted representation
# Only the final score is decrypted for output
```

**Important limitation to communicate:** HE is applied to the structured numerical scoring layer only. LLM inference (RAG, research, jury agents) cannot run on encrypted text — this is a known limitation of current HE technology. The HE layer protects the most sensitive financial ratios from being exposed in plaintext to the scoring model.

**Compliance badges to display in UI:**
- ✓ RBI Data Localisation (all processing on-premise capable)
- ✓ Structured data encrypted before ML scoring
- ✓ Zero raw financial data exposure in scoring layer
- ✓ Full audit trail for RBI inspection

---

## ERROR HANDLING & FALLBACKS

Build graceful fallbacks for every external dependency — the demo must not fail:

```python
# MCA API fallback
try:
    result = mca_api.get_company(cin)
except (APIError, TimeoutError):
    result = mock_mca_data[cin]  # pre-loaded synthetic data for demo companies

# OCR fallback  
try:
    text = extract_with_pymupdf(pdf)
    if len(text) < 100:
        raise InsufficientTextError
except InsufficientTextError:
    text = extract_with_easyocr(pdf)

# LLM fallback
try:
    response = anthropic_client.messages.create(...)
except anthropic.APIError:
    response = openai_client.chat.completions.create(...)  # fallback provider

# Camelot table extraction fallback
try:
    tables = camelot.read_pdf(path, flavor='lattice')
except:
    tables = camelot.read_pdf(path, flavor='stream')
```

---

## DATABRICKS INTEGRATION

The problem statement explicitly mentions Databricks. Integrate as the data platform layer:

```python
from databricks.sdk import WorkspaceClient

# Use Databricks Unity Catalog as feature store
w = WorkspaceClient()

# Register financial features in Unity Catalog
feature_table = w.feature_store.create_table(
    name="intelli_credit.features.borrower_financial",
    primary_keys=["session_id"],
    schema=feature_schema
)

# Use Databricks for batch processing of multiple applications
# Use Delta Lake for versioned storage of risk_flags
# Use MLflow (native to Databricks) for XGBoost model tracking
```

Even if running locally for demo, show the Databricks integration path and use MLflow for model versioning.

---

## PROJECT STRUCTURE

```
intelli-credit/
├── README.md
├── docker-compose.yml
├── .env.example
│
├── backend/
│   ├── main.py                    # FastAPI app, all routes
│   ├── requirements.txt
│   │
│   ├── modules/
│   │   ├── ingestion/
│   │   │   ├── classifier.py      # LLM document classification
│   │   │   ├── extractor.py       # PyMuPDF + OCR + Camelot
│   │   │   ├── gst_reconciler.py  # GST cross-reference logic
│   │   │   ├── rag_pipeline.py    # Chunking + embedding + Qdrant
│   │   │   └── flag_store.py      # Write to risk_flags table
│   │   │
│   │   ├── research/
│   │   │   ├── entity_resolver.py # CIN/DIN resolution
│   │   │   ├── mca_crawler.py     # MCA21 API calls
│   │   │   ├── legal_intel.py     # e-Courts + NCLT
│   │   │   ├── web_crawler.py     # Semantic web search
│   │   │   └── promoter_graph.py  # Knowledge graph builder
│   │   │
│   │   ├── jury/
│   │   │   ├── base_scorer.py     # XGBoost + SHAP
│   │   │   ├── five_cs.py         # Five Cs computation
│   │   │   ├── prosecutor.py      # Agent 1 prompt + call
│   │   │   ├── defender.py        # Agent 2 prompt + call
│   │   │   ├── judge.py           # Agent 3 prompt + call
│   │   │   └── jury_engine.py     # Orchestrate all agents
│   │   │
│   │   └── cam/
│   │       ├── cam_generator.py   # python-docx CAM builder
│   │       └── chart_generator.py # matplotlib chart builder
│   │
│   ├── models/
│   │   ├── xgboost_model.pkl      # Trained model
│   │   └── train_synthetic.py     # Script to generate training data
│   │
│   ├── privacy/
│   │   └── he_scorer.py           # TenSEAL homomorphic encryption
│   │
│   └── demo_data/
│       ├── generate_demo_pdfs.py  # Creates Vardhaman synthetic PDFs
│       └── vardhaman/             # Pre-generated demo PDFs
│
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx
│   │   ├── views/
│   │   │   ├── UploadPortal.jsx
│   │   │   ├── ProcessingDashboard.jsx
│   │   │   ├── ReviewInput.jsx
│   │   │   └── JuryDecision.jsx
│   │   └── components/
│   │       ├── FiveCsGauges.jsx
│   │       ├── RiskFlagsTable.jsx
│   │       ├── JuryDeliberationLog.jsx
│   │       └── ScoreJourney.jsx
│
└── notebooks/
    └── databricks_feature_store.ipynb
```

---

## SETUP & RUNNING

```bash
# 1. Clone and configure
git clone <repo>
cd intelli-credit
cp .env.example .env
# Fill in: ANTHROPIC_API_KEY or OPENAI_API_KEY, DATABASE_URL, QDRANT_URL

# 2. Generate demo data
cd backend
python demo_data/generate_demo_pdfs.py

# 3. Train synthetic XGBoost model
python models/train_synthetic.py

# 4. Start all services
docker-compose up --build

# 5. Access
# Frontend: http://localhost:3000
# API docs: http://localhost:8000/docs
# Qdrant UI: http://localhost:6333/dashboard

# 6. Run demo
# Upload files from backend/demo_data/vardhaman/
# Watch the pipeline process Vardhaman Infra
# Key moment: base score 78 → jury score 51
```

---

## REFERENCES

1. Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *NeurIPS 2020.*
2. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of KDD 2016.* ACM.
3. Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. *NeurIPS 2020.*
4. Reserve Bank of India. (2023). *Master Circular — Prudential Norms on Income Recognition, Asset Classification and Provisioning.* RBI/2023-24/53.
5. Gentry, C. (2009). Fully homomorphic encryption using ideal lattices. *Proceedings of STOC 2009.* ACM.
6. Goods and Services Tax Network. (2023). *GSTR-1, GSTR-2A and GSTR-3B: Filing Framework and Reconciliation Guidelines.* GSTN.
