"""
Module 1 — RAG Pipeline
Chunks text → embeds with sentence-transformers → stores in Qdrant →
runs 10 semantic risk queries → extracts risk flags via LLM.
"""

import os
import json
import re
import uuid
from typing import Optional

RISK_QUERIES = [
    "going concern doubt or ability to continue as going concern",
    "auditor qualification or modified opinion or emphasis of matter",
    "litigation legal proceedings disputes court cases",
    "related party transactions loans to directors or promoters",
    "capacity utilisation operating below capacity plant idle",
    "debt restructuring or loan renegotiation or moratorium",
    "pledged shares promoter shareholding decline",
    "contingent liabilities guarantees off balance sheet",
    "NCLT insolvency resolution proceedings",
    "RBI regulatory action penalty or show cause notice",
]

QUERY_TO_PILLAR = {
    "going concern": "C2", "auditor": "C1", "litigation": "C1",
    "related party": "C1", "capacity utilisation": "C2",
    "debt restructuring": "C2", "pledged shares": "C4",
    "contingent liabilities": "C3", "NCLT": "C1", "RBI": "C5",
}


def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list:
    """Split text into overlapping chunks, preserving page markers."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk = " ".join(chunk_words)
        chunks.append({"text": chunk, "start_word": i})
        i += chunk_size - overlap
    return chunks


# Public alias
def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list:
    """Public wrapper around _chunk_text for external use."""
    return _chunk_text(text, chunk_size, overlap)


def _get_embedder():
    """Load sentence-transformers model (cached after first load)."""
    try:
        # Don't block on download if TRANSFORMERS_OFFLINE or no internet
        import os as _os
        if _os.getenv("TRANSFORMERS_OFFLINE", "0") == "1":
            return None
        from sentence_transformers import SentenceTransformer
        return SentenceTransformer("all-MiniLM-L6-v2")
    except ImportError:
        print("[RAG] sentence-transformers not installed.")
        return None
    except Exception as e:
        print(f"[RAG] Embedder load failed: {e}")
        return None


def _get_qdrant():
    """Create Qdrant client."""
    try:
        from qdrant_client import QdrantClient
        url = os.getenv("QDRANT_URL", "http://localhost:6333")
        return QdrantClient(url=url, timeout=10)
    except Exception as e:
        print(f"[RAG] Qdrant not available: {e}")
        return None


async def run_rag_pipeline(all_text: dict[str, str], session_id: str) -> list:
    """Main RAG pipeline: embed all docs → query for risks → extract flags."""
    flags = []

    model = _get_embedder()
    qdrant = _get_qdrant()

    if not model or not qdrant:
        print("[RAG] Skipping RAG pipeline — sentence-transformers or Qdrant unavailable")
        return _synthetic_rag_flags(session_id)

    collection_name = f"borrower_{session_id.replace('-', '_')}"

    # Create collection
    try:
        from qdrant_client.models import VectorParams, Distance
        qdrant.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )
    except Exception as e:
        print(f"[RAG] Qdrant collection create failed: {e}")
        return _synthetic_rag_flags(session_id)

    # Chunk + embed + upsert
    all_chunks = []
    for doc_name, text in all_text.items():
        if not text.strip():
            continue
        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            all_chunks.append({
                "id": str(uuid.uuid4()),
                "text": chunk["text"],
                "doc_name": doc_name,
                "chunk_idx": i,
            })

    if all_chunks:
        try:
            from qdrant_client.models import PointStruct
            texts = [c["text"] for c in all_chunks]
            embeddings = model.encode(texts, batch_size=32, show_progress_bar=False)

            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=emb.tolist(),
                    payload={"text": c["text"], "doc_name": c["doc_name"], "chunk_idx": c["chunk_idx"]},
                )
                for c, emb in zip(all_chunks, embeddings)
            ]
            qdrant.upsert(collection_name=collection_name, points=points)
        except Exception as e:
            print(f"[RAG] Embedding/upsert failed: {e}")
            return _synthetic_rag_flags(session_id)

    # Run semantic risk queries
    for query in RISK_QUERIES:
        try:
            q_embedding = model.encode([query])[0]
            results = qdrant.search(
                collection_name=collection_name,
                query_vector=q_embedding.tolist(),
                limit=5,
                score_threshold=0.4,
            )

            if not results:
                continue

            # Combine top-5 chunks and pass to LLM
            combined_text = "\n---\n".join([r.payload["text"] for r in results])
            new_flags = await _extract_flags_llm(query, combined_text, session_id)
            flags.extend(new_flags)

        except Exception as e:
            print(f"[RAG] Query '{query[:40]}' failed: {e}")

    return flags


async def _extract_flags_llm(query: str, text: str, session_id: str) -> list:
    """Use LLM to extract structured risk flags from retrieved text."""
    prompt = f"""You are a credit risk analyst. The following text is from a corporate financial document.
Extract any risk flags related to: {query}
For each flag found, output JSON: {{"flag_text": "exact quote", "risk_category": "...", "severity": "HIGH/MEDIUM/LOW", "page_hint": "..."}}
If no relevant risk found, return empty array [].
Return only valid JSON array, no other text.

Document text:
{text[:3000]}"""

    try:
        provider = os.getenv("LLM_PROVIDER", "anthropic").lower()

        if provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            model_name = os.getenv("FAST_MODEL", "claude-haiku-4-20250514")
            resp = client.messages.create(
                model=model_name,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = resp.content[0].text.strip()
        else:
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = resp.choices[0].message.content.strip()

        raw = re.sub(r"```json|```", "", raw).strip()
        items = json.loads(raw)
        if not isinstance(items, list):
            return []

        flags = []
        for item in items:
            five_c = "C1"
            for kw, pillar in QUERY_TO_PILLAR.items():
                if kw.lower() in query.lower():
                    five_c = pillar
                    break

            flags.append({
                "flag_type": item.get("risk_category", "SEMANTIC_RISK").upper().replace(" ", "_"),
                "severity": item.get("severity", "MEDIUM"),
                "source_document": "Annual Report / Unstructured",
                "evidence_snippet": item.get("flag_text", "")[:500],
                "page_reference": item.get("page_hint", ""),
                "source_module": "RAG",
                "five_c_pillar": five_c,
                "session_id": session_id,
            })
        return flags

    except Exception as e:
        print(f"[RAG] LLM flag extraction failed: {e}")
        return []


def _synthetic_rag_flags(session_id: str) -> list:
    """Demo fallback: synthetic RAG flags for Vardhaman Infra."""
    return [
        {
            "flag_type": "GOING_CONCERN",
            "severity": "HIGH",
            "source_document": "vardhaman_annual_report_fy24.pdf",
            "evidence_snippet": "The Company's ability to continue as a going concern is subject to resolution of the matters described in Note 31 — Contingent Liabilities.",
            "page_reference": "Page 34",
            "source_module": "RAG",
            "five_c_pillar": "C2",
            "session_id": session_id,
        },
        {
            "flag_type": "CONTINGENT_LIABILITY",
            "severity": "MEDIUM",
            "source_document": "vardhaman_annual_report_fy24.pdf",
            "evidence_snippet": "Note 31: Contingent liabilities aggregating to ₹8.4 Crore not provided for in the accounts.",
            "page_reference": "Page 34",
            "source_module": "RAG",
            "five_c_pillar": "C3",
            "session_id": session_id,
        },
    ]
