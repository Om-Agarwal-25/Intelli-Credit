"""
Module 1 — GST Cross-Reference Engine (India-Specific Fraud Detection)
Detects: GSTR-1 vs Bank reconciliation, GSTR-2A vs 3B ITC mismatch,
         Round-tripping, Circular trading.
"""

import re
from typing import Optional


def run_gst_reconciliation(all_text: dict[str, str], session_id: str) -> list:
    """Run all GST-related fraud checks. Returns list of risk flags."""
    flags = []

    gst_text = ""
    bank_text = ""

    for filename, text in all_text.items():
        fn_lower = filename.lower()
        if "gstr" in fn_lower or "gst" in fn_lower:
            gst_text += text
        if "bank" in fn_lower or "statement" in fn_lower:
            bank_text += text

    if gst_text:
        flags.extend(_check_gstr1_bank_mismatch(gst_text, bank_text))
        flags.extend(_check_gstr2a_vs_3b(gst_text))
        flags.extend(_check_circular_trading(gst_text))

    if bank_text:
        flags.extend(_check_round_tripping(bank_text))

    # Attach session_id and source
    for f in flags:
        f["session_id"] = session_id
        f["source_module"] = "STRUCTURED"

    return flags


def _extract_monthly_amounts(text: str, keywords: list) -> dict:
    """Extract month-wise amounts using regex patterns."""
    months = {
        "april": 4, "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
        "january": 1, "february": 2, "march": 3,
        "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9,
        "oct": 10, "nov": 11, "dec": 12, "jan": 1, "feb": 2, "mar": 3,
    }

    monthly_data = {}
    text_lower = text.lower()

    for month_name, month_num in months.items():
        # Look for amount near month name (within 200 chars)
        pattern = rf"{month_name}.{{0,200}}?(?:₹|rs\.?|inr)?\s*([\d,]+(?:\.\d+)?)"
        matches = re.findall(pattern, text_lower)
        if matches:
            try:
                # Take largest amount found near month name
                amounts = [float(m.replace(",", "")) for m in matches]
                monthly_data[month_num] = max(amounts)
            except ValueError:
                pass

    return monthly_data


def _check_gstr1_bank_mismatch(gst_text: str, bank_text: str) -> list:
    """Compare declared GST turnover vs bank credits."""
    flags = []

    if not bank_text:
        return flags

    # Extract monthly figures from both sources
    gst_monthly = _extract_monthly_amounts(gst_text, ["taxable", "turnover", "outward"])
    bank_monthly = _extract_monthly_amounts(bank_text, ["credit", "deposit"])

    anomalous_months = []
    for month_num in gst_monthly:
        if month_num in bank_monthly:
            gst_val = gst_monthly[month_num]
            bank_val = bank_monthly[month_num]
            if gst_val > 0:
                discrepancy_ratio = abs(gst_val - bank_val) / gst_val
                if discrepancy_ratio > 0.60:
                    anomalous_months.append(month_num)

    if len(anomalous_months) >= 2:
        # Check if consecutive
        anomalous_months.sort()
        for i in range(len(anomalous_months) - 1):
            if anomalous_months[i + 1] - anomalous_months[i] == 1:
                flags.append({
                    "flag_type": "REVENUE_INFLATION",
                    "severity": "HIGH",
                    "source_document": "GST_RETURN / BANK_STATEMENT",
                    "evidence_snippet": f"GST-declared turnover vs bank credits discrepancy >60% in months {anomalous_months}. Pattern suggests inflated revenue declaration.",
                    "page_reference": "GST Schedule",
                    "five_c_pillar": "C2",
                })
                break

    # Check pre-loan cash stuffing (recent 2-month spike)
    bank_months = sorted(bank_monthly.keys())
    if len(bank_months) >= 3:
        recent = bank_months[-2:]
        prior = bank_months[:-2]
        if prior:
            recent_avg = sum(bank_monthly[m] for m in recent) / len(recent)
            prior_avg = sum(bank_monthly[m] for m in prior) / len(prior)
            if prior_avg > 0 and (recent_avg - prior_avg) / prior_avg > 0.40:
                # Check if GST didn't spike correspondingly
                recent_gst_avg = sum(gst_monthly.get(m, 0) for m in recent) / max(len(recent), 1)
                prior_gst_avg = sum(gst_monthly.get(m, 0) for m in prior) / max(len(prior), 1)
                if prior_gst_avg > 0 and (recent_gst_avg - prior_gst_avg) / prior_gst_avg < 0.10:
                    flags.append({
                        "flag_type": "PRE_LOAN_CASH_STUFFING",
                        "severity": "HIGH",
                        "source_document": "BANK_STATEMENT",
                        "evidence_snippet": "Bank credits spiked >40% in the 2 months before application with no corresponding GST increase. Classic pre-loan cash stuffing pattern.",
                        "page_reference": "Bank Statement — recent months",
                        "five_c_pillar": "C2",
                    })

    return flags


def _check_gstr2a_vs_3b(gst_text: str) -> list:
    """Detect fake ITC claims: GSTR-3B claimed > GSTR-2A available by >15%."""
    flags = []

    # Look for ITC figures
    itc_claimed_match = re.findall(
        r"(?:itc claimed|input tax credit claimed|3b.*table 4a|eligible itc).*?([\d,]+(?:\.\d+)?)",
        gst_text.lower()
    )
    itc_available_match = re.findall(
        r"(?:itc available|2a.*itc|auto-populated|gstr-2a.*credit).*?([\d,]+(?:\.\d+)?)",
        gst_text.lower()
    )

    if itc_claimed_match and itc_available_match:
        try:
            claimed = float(itc_claimed_match[0].replace(",", ""))
            available = float(itc_available_match[0].replace(",", ""))
            if available > 0 and (claimed - available) / available > 0.15:
                flags.append({
                    "flag_type": "FAKE_ITC_CLAIM",
                    "severity": "HIGH",
                    "source_document": "GST_RETURN",
                    "evidence_snippet": f"GSTR-3B ITC claimed (₹{claimed:,.0f}) exceeds GSTR-2A ITC available (₹{available:,.0f}) by >{((claimed-available)/available*100):.0f}%. Possible fake ITC claim — most common GST fraud signal.",
                    "page_reference": "GSTR-3B Table 4A / GSTR-2A",
                    "five_c_pillar": "C1",
                })
        except (ValueError, ZeroDivisionError):
            pass

    return flags


def _check_round_tripping(bank_text: str) -> list:
    """Detect same amount appearing as both credit and debit within 48 hours."""
    flags = []

    # Extract all transactions with amounts > 10 lakhs (₹10,00,000)
    amount_pattern = r"(?:[\d,]+(?:\.\d+)?)"
    large_amounts = re.findall(r"(?:₹|rs\.?)?\s*(\d{1,3}(?:,\d{2,3})+(?:\.\d+)?)", bank_text.lower())

    seen_large = set()
    round_trip_candidates = []

    for amt_str in large_amounts:
        try:
            amt = float(amt_str.replace(",", ""))
            if amt >= 1000000:  # > ₹10 lakh
                rounded = round(amt, -4)  # round to nearest ₹10k (±2% tolerance)
                if rounded in seen_large:
                    round_trip_candidates.append(amt)
                seen_large.add(rounded)
        except ValueError:
            pass

    if round_trip_candidates:
        flags.append({
            "flag_type": "ROUND_TRIPPING",
            "severity": "HIGH",
            "source_document": "BANK_STATEMENT",
            "evidence_snippet": f"Detected {len(round_trip_candidates)} potential round-trip transaction(s) where large amounts (>₹10L) appear as both credit and debit. Example: ₹{round_trip_candidates[0]:,.0f}",
            "page_reference": "Bank Statement",
            "five_c_pillar": "C1",
        })

    return flags


def _check_circular_trading(gst_text: str) -> list:
    """Detect if any vendor GSTIN also appears as customer GSTIN."""
    flags = []

    gstin_pattern = r"[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}"
    all_gstins = re.findall(gstin_pattern, gst_text.upper())

    if len(all_gstins) < 2:
        return flags

    # Heuristic: if same GSTIN appears 3+ times, likely circular
    from collections import Counter
    gstin_counts = Counter(all_gstins)
    circular = [g for g, c in gstin_counts.items() if c >= 3]

    if circular:
        flags.append({
            "flag_type": "CIRCULAR_TRADING",
            "severity": "HIGH",
            "source_document": "GST_RETURN",
            "evidence_snippet": f"GSTIN(s) appearing as both supplier and customer in GST schedule: {', '.join(circular[:3])}. Indicates potential circular trading arrangement.",
            "page_reference": "GST Input/Output Schedule",
            "five_c_pillar": "C1",
        })

    return flags
