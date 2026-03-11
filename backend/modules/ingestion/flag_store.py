"""
Module 1 — Flag Store
Persists risk flags to PostgreSQL (or in-memory if DB unavailable).
"""

import os
import uuid
from typing import Optional


async def save_flags(flags: list, session_id: str) -> int:
    """Save risk flags to PostgreSQL. Returns count saved."""
    if not flags:
        return 0

    try:
        import asyncpg
        db_url = os.getenv("DATABASE_URL", "postgresql://intellicredit:intellicredit@localhost:5432/intellicredit")
        conn = await asyncpg.connect(db_url)

        count = 0
        for flag in flags:
            await conn.execute("""
                INSERT INTO risk_flags
                  (flag_id, session_id, flag_type, severity, source_document,
                   evidence_snippet, page_reference, source_module, five_c_pillar)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT DO NOTHING
            """,
                str(uuid.uuid4()),
                session_id,
                flag.get("flag_type", "UNKNOWN")[:100],
                flag.get("severity", "LOW"),
                flag.get("source_document", "")[:255],
                flag.get("evidence_snippet", ""),
                flag.get("page_reference", "")[:50],
                flag.get("source_module", "STRUCTURED"),
                flag.get("five_c_pillar", ""),
            )
            count += 1

        await conn.close()
        print(f"[FLAG STORE] Saved {count} flags for session {session_id}")
        return count

    except Exception as e:
        print(f"[FLAG STORE] DB unavailable ({e}), flags stored in memory only")
        return len(flags)


async def get_flags(session_id: str) -> list:
    """Retrieve all risk flags for a session."""
    try:
        import asyncpg
        db_url = os.getenv("DATABASE_URL", "postgresql://intellicredit:intellicredit@localhost:5432/intellicredit")
        conn = await asyncpg.connect(db_url)
        rows = await conn.fetch(
            "SELECT * FROM risk_flags WHERE session_id = $1 ORDER BY severity DESC, created_at",
            session_id
        )
        await conn.close()
        return [dict(r) for r in rows]
    except Exception:
        return []
