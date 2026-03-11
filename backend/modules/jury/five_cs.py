"""
Module 3 — Five Cs Score Computation
Computes C1 Character, C2 Capacity, C3 Capital, C4 Collateral, C5 Conditions
from all risk flags in the session.
"""

from typing import Optional


FIVE_CS_WEIGHTS = {"C1": 0.25, "C2": 0.30, "C3": 0.15, "C4": 0.20, "C5": 0.10}

SEVERITY_PENALTY = {"HIGH": -20, "MEDIUM": -10, "LOW": -4}

C_DEFAULTS = {"C1": 80, "C2": 75, "C3": 70, "C4": 70, "C5": 72}


def compute_five_cs(risk_flags: list) -> dict:
    """Compute Five Cs scores from risk flags. Each C starts at a base and takes deductions."""

    # Group flags by pillar
    pillars = {"C1": [], "C2": [], "C3": [], "C4": [], "C5": []}
    for flag in risk_flags:
        pillar = flag.get("five_c_pillar", "C1")
        if pillar in pillars:
            pillars[pillar].append(flag)

    scores = {}
    for c_key, c_flags in pillars.items():
        base = C_DEFAULTS[c_key]
        deduction = 0
        for flag in c_flags:
            sev = flag.get("severity", "LOW")
            deduction += abs(SEVERITY_PENALTY.get(sev, -4))
        scores[c_key] = max(0, min(100, base - deduction))

    # Special rules
    # C1: If DIN disqualified → min cap at 30 (regulatory violation)
    has_din_disq = any("DIN_DISQUALIFIED" in f.get("flag_type", "") for f in risk_flags)
    if has_din_disq:
        scores["C1"] = min(scores["C1"], 35)

    # C2: Going concern → strong negative
    has_going_concern = any("GOING_CONCERN" in f.get("flag_type", "") for f in risk_flags)
    if has_going_concern:
        scores["C2"] = min(scores["C2"], 45)

    # Composite
    composite = sum(scores[c] * w for c, w in FIVE_CS_WEIGHTS.items())

    return {
        "C1": round(scores["C1"], 1),
        "C2": round(scores["C2"], 1),
        "C3": round(scores["C3"], 1),
        "C4": round(scores["C4"], 1),
        "C5": round(scores["C5"], 1),
        "composite": round(composite, 1),
        "flag_counts": {c: len(f) for c, f in pillars.items()},
    }
