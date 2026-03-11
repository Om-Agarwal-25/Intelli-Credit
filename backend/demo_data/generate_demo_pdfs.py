"""
Demo Data Generator — Vardhaman Infra & Logistics Pvt. Ltd.
Creates 4 realistic synthetic PDFs using reportlab for the hackathon demo.
"""

import os
from pathlib import Path
from datetime import datetime, date

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.platypus import PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("[DEMO] reportlab not installed. Run: pip install reportlab")


OUTPUT_DIR = Path(__file__).parent / "vardhaman"


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("ICTableCell", fontSize=9, leading=11))
    styles.add(ParagraphStyle("ICSmallNote", fontSize=7, leading=9, textColor=colors.gray))
    styles.add(ParagraphStyle("ICTitle", fontSize=16, leading=20, alignment=TA_CENTER, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle("ICSubtitle", fontSize=11, leading=14, alignment=TA_CENTER))
    styles.add(ParagraphStyle("ICBold", fontSize=10, leading=13, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle("ICWarning", fontSize=9, leading=11, textColor=colors.red, fontName="Helvetica-Bold"))
    return styles


def generate_gstr1():
    """GSTR-1 with April/May anomaly — GST declared vs bank mismatch."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "vardhaman_gstr1_fy24.pdf"

    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = _styles()
    story = []

    story.append(Paragraph("GOODS AND SERVICES TAX RETURN — GSTR-1", styles["ICTitle"]))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Return of Outward Supplies — Financial Year 2023-24", styles["ICSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
    story.append(Spacer(1, 10))

    info = [
        ["Legal Name of Taxpayer:", "Vardhaman Infra & Logistics Pvt. Ltd."],
        ["GSTIN:", "27AABCV1234F1ZA"],
        ["Period:", "April 2023 to March 2024"],
        ["Filing Date:", "15 May 2024"],
        ["ARN:", "AA2705225478329"],
    ]
    t = Table(info, colWidths=[6 * cm, 10 * cm])
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 3)]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("TABLE 4 — TAXABLE OUTWARD SUPPLIES (₹ in Lakhs)", styles["ICBold"]))
    story.append(Spacer(1, 5))

    months = ["Apr-23", "May-23", "Jun-23", "Jul-23", "Aug-23", "Sep-23",
              "Oct-23", "Nov-23", "Dec-23", "Jan-24", "Feb-24", "Mar-24"]
    # April & May have inflated GST but bank shows much lower credits
    gst_declared = [285.4, 297.8, 312.5, 318.0, 325.2, 330.7,
                    338.4, 342.1, 315.0, 307.8, 295.3, 281.6]

    headers = ["Month", "Taxable Value (₹L)", "CGST (₹L)", "SGST (₹L)", "Total Tax (₹L)"]
    table_data = [headers]
    for m, gst in zip(months, gst_declared):
        cgst = round(gst * 0.09, 1)
        sgst = round(gst * 0.09, 1)
        table_data.append([m, f"{gst:,.1f}", f"{cgst:,.1f}", f"{sgst:,.1f}", f"{cgst+sgst:,.1f}"])

    table_data.append(["TOTAL", f"{sum(gst_declared):,.1f}", f"{sum(gst_declared)*0.09:,.1f}",
                        f"{sum(gst_declared)*0.09:,.1f}", f"{sum(gst_declared)*0.18:,.1f}"])

    t = Table(table_data, colWidths=[3 * cm, 3.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightblue),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("GSTR-2A ITC RECONCILIATION SUMMARY", styles["ICBold"]))
    story.append(Spacer(1, 5))

    itc_data = [
        ["", "Amount (₹ Lakhs)"],
        ["ITC Available as per GSTR-2A (auto-populated from vendor filings):", "245.80"],
        ["ITC Claimed in GSTR-3B (Table 4A — self-declared):", "298.50"],  # >15% over
        ["Excess ITC Claimed:", "52.70"],
        ["Excess as % of Available:", "21.4%"],
    ]
    t = Table(itc_data, colWidths=[12 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, -1), (-1, -1), colors.red),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(Paragraph("* Note: ITC claimed exceeds ITC available by 21.4%. Document filed in compliance with applicable GST regulations.", styles["ICSmallNote"]))

    doc.build(story)
    print(f"[DEMO] Generated: {path}")
    return str(path)


def generate_bank_statement():
    """Bank Statement with April/May low credits (only 37% of GST declared)."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "vardhaman_bank_statement_fy24.pdf"

    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = _styles()
    story = []

    story.append(Paragraph("STATE BANK OF INDIA — ACCOUNT STATEMENT", styles["ICTitle"]))
    story.append(Paragraph("Branch: Corporate Banking Branch, Pune | IFSC: SBIN0020175", styles["ICSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
    story.append(Spacer(1, 10))

    info = [
        ["Account Name:", "Vardhaman Infra & Logistics Pvt. Ltd."],
        ["Account Number:", "XXXX XXXX 5847"],
        ["Account Type:", "Current Account"],
        ["Period:", "01 Apr 2023 to 31 Mar 2024"],
        ["Statement Generated:", "05 Jun 2024"],
    ]
    t = Table(info, colWidths=[6 * cm, 10 * cm])
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 3)]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("MONTHLY SUMMARY", styles["ICBold"]))
    story.append(Spacer(1, 5))

    months = ["Apr-23", "May-23", "Jun-23", "Jul-23", "Aug-23", "Sep-23",
              "Oct-23", "Nov-23", "Dec-23", "Jan-24", "Feb-24", "Mar-24"]
    # April & May credits are only 37% of GST declared (anomaly)
    credits = [105.6, 110.2, 308.1, 313.5, 320.8, 325.4,
               334.2, 338.9, 310.8, 302.9, 291.6, 278.3]
    debits = [98.3, 102.4, 285.6, 290.1, 298.7, 302.3,
              310.8, 315.2, 288.9, 281.4, 270.3, 258.8]

    headers = ["Month", "Total Credits (₹L)", "Total Debits (₹L)", "Net Flow (₹L)", "Closing Balance (₹L)"]
    table_data = [headers]
    balance = 150.0
    for m, cr, db in zip(months, credits, debits):
        balance = balance + cr - db
        net = cr - db
        row = [m, f"{cr:,.1f}", f"{db:,.1f}", f"{net:,.1f}", f"{balance:,.1f}"]
        table_data.append(row)

    t = Table(table_data, colWidths=[2.5 * cm, 3.5 * cm, 3.5 * cm, 3 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        # Highlight anomaly months
        ("BACKGROUND", (0, 1), (-1, 2), colors.lightyellow),
        ("TEXTCOLOR", (1, 1), (1, 2), colors.red),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))
    story.append(Paragraph("NOTE: April and May 2023 figures represent partial credit collections due to system migration period. GST returns for these months reflect accrual-basis figures.", styles["ICSmallNote"]))

    doc.build(story)
    print(f"[DEMO] Generated: {path}")
    return str(path)


def generate_annual_report():
    """Annual report with going-concern footnote buried on page 34."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "vardhaman_annual_report_fy24.pdf"

    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = _styles()
    story = []

    # Page 1: Cover
    story.append(Spacer(1, 2 * cm))
    story.append(Paragraph("VARDHAMAN INFRA & LOGISTICS PVT. LTD.", styles["ICTitle"]))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Annual Report 2023-24", styles["ICSubtitle"]))
    story.append(Spacer(1, 5))
    story.append(Paragraph("CIN: U45200MH2015PTC264831", styles["ICSubtitle"]))
    story.append(PageBreak())

    # Pages 2-5: Director's Report
    story.append(Paragraph("BOARD OF DIRECTORS", styles["ICBold"]))
    story.append(Spacer(1, 8))
    directors = [
        ["Name", "Designation", "DIN"],
        ["Mr. Rajesh Kumar Vardhaman", "Managing Director", "06284530"],
        ["Ms. Kavita Mehta", "Executive Director", "07284531"],
    ]
    t = Table(directors, colWidths=[8 * cm, 5 * cm, 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("MANAGEMENT DISCUSSION AND ANALYSIS", styles["ICBold"]))
    story.append(Paragraph(
        "The Company achieved a revenue of ₹340.2 crore in FY2024, representing an 18.3% growth over the previous year. "
        "Our EBITDA margins expanded to 14.2% driven by operational efficiencies. Our order book stands at ₹620 crore "
        "providing strong revenue visibility for FY2025. We have successfully executed 12 NHAI highway projects worth ₹1,200 crore.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 10))

    # Financial highlights
    fin_table = [
        ["FINANCIAL HIGHLIGHTS (₹ in Crores)", "FY2024", "FY2023", "YoY Growth"],
        ["Revenue from Operations", "340.2", "287.5", "+18.3%"],
        ["EBITDA", "48.3", "38.6", "+25.1%"],
        ["EBITDA Margin", "14.2%", "13.4%", "+80 bps"],
        ["Net Worth", "142.8", "118.6", "+20.4%"],
        ["Debt Service Coverage Ratio", "1.6x", "1.4x", "+"],
        ["Gearing Ratio", "1.8x", "2.1x", "Improving"],
    ]
    t = Table(fin_table, colWidths=[7 * cm, 3 * cm, 3 * cm, 3 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))
    story.append(t)

    # Add many pages of content to push the going-concern note to page 34
    for i in range(28):
        story.append(PageBreak())
        if i == 0:
            story.append(Paragraph("STATUTORY AUDITORS' REPORT", styles["ICBold"]))
            story.append(Paragraph(
                "To the Members of Vardhaman Infra & Logistics Pvt. Ltd.\n\n"
                "Report on the Standalone Financial Statements\n\n"
                "We have audited the accompanying standalone financial statements of Vardhaman Infra & Logistics "
                "Private Limited (the Company) which comprise the Balance Sheet as at 31 March 2024, "
                "the Statement of Profit and Loss and the Cash Flow Statement for the year then ended.\n\n"
                "Opinion: In our opinion and to the best of our information and according to the explanations "
                "given to us, the aforesaid standalone financial statements give a true and fair view in conformity "
                "with the Indian Accounting Standards...\n\n"
                "Emphasis of Matter: Without modifying our opinion, we draw attention to Note 31 of the financial "
                "statements regarding going concern uncertainties.",
                styles["Normal"]
            ))
        else:
            story.append(Paragraph(f"NOTES TO FINANCIAL STATEMENTS — CONTINUED (Page {i + 6})", styles["ICBold"]))
            if i < 5:
                story.append(Paragraph(f"Note {i + 1}: Accounting Policies and Basis of Preparation\n\nThe financial statements have been prepared in accordance with Indian Accounting Standards (Ind AS) prescribed under the Companies Act 2013. All figures are in Indian Rupees unless stated otherwise.", styles["Normal"]))

    # Page 34: Going-concern footnote (buried!)
    story.append(PageBreak())
    story.append(Paragraph("NOTE 31 — CONTINGENT LIABILITIES AND GOING CONCERN", styles["ICBold"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "31.1 Contingent Liabilities:",
        styles["ICBold"]
    ))
    story.append(Paragraph(
        "The Company has the following contingent liabilities not provided for in these financial statements:\n"
        "a) Claims/disputes against the Company pending before various courts/tribunals: ₹8.4 crore\n"
        "b) Disputed tax demands under Income Tax Act: ₹1.2 crore\n"
        "c) Performance bank guarantees issued: ₹24.6 crore",
        styles["Normal"]
    ))
    story.append(Spacer(1, 8))

    story.append(Paragraph("31.2 Going Concern:", styles["ICWarning"]))
    story.append(Paragraph(
        "The Company's ability to continue as a going concern is subject to resolution of the matters described "
        "in Note 31 — Contingent Liabilities. The NHAI has issued a penalty notice of ₹6.8 crore regarding "
        "delay in completion of the NH-65 highway project (14 months behind schedule). Management believes "
        "that the matter will be resolved through negotiation, however the outcome cannot be determined with "
        "certainty at this stage. These factors, along with the matters set forth in Note 31.1, raise substantial "
        "doubt about the Company's ability to continue as a going concern.",
        styles["Normal"]
    ))
    story.append(Spacer(1, 5))
    story.append(Paragraph("Management's Assessment: Management has prepared these financial statements on a going concern basis, as it is confident the above matters will be resolved favourably. The assessment is based on business projections and ongoing negotiations.", styles["ICSmallNote"]))

    doc.build(story)
    print(f"[DEMO] Generated: {path} (going-concern note on final page = ~p.34)")
    return str(path)


def generate_itr():
    """Synthetic ITR for Vardhaman Infra."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / "vardhaman_itr_fy24.pdf"

    doc = SimpleDocTemplate(str(path), pagesize=A4)
    styles = _styles()
    story = []

    story.append(Paragraph("INCOME TAX RETURN — ITR-6", styles["ICTitle"]))
    story.append(Paragraph("Assessment Year 2024-25 | Filing for FY 2023-24", styles["ICSubtitle"]))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
    story.append(Spacer(1, 10))

    info = [
        ["Company Name:", "Vardhaman Infra & Logistics Pvt. Ltd."],
        ["PAN:", "AABCV1234F"],
        ["CIN:", "U45200MH2015PTC264831"],
        ["Assessment Year:", "2024-25"],
        ["Date of Filing:", "30 October 2024"],
        ["ITR Acknowledgement No.:", "325810890241024"],
    ]
    t = Table(info, colWidths=[6 * cm, 10 * cm])
    t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9), ("TOPPADDING", (0, 0), (-1, -1), 3)]))
    story.append(t)
    story.append(Spacer(1, 15))

    story.append(Paragraph("PART B-TI — COMPUTATION OF TOTAL INCOME", styles["ICBold"]))
    income_data = [
        ["Particulars", "Amount (₹)"],
        ["Revenue from Operations", "34,02,00,000"],
        ["Other Income", "48,50,000"],
        ["Total Income", "34,50,50,000"],
        ["Cost of Materials Consumed", "21,35,40,000"],
        ["Employee Benefit Expenses", "3,24,80,000"],
        ["Finance Costs", "2,18,60,000"],
        ["Depreciation & Amortisation", "1,42,70,000"],
        ["Other Expenses", "4,81,00,000"],
        ["Total Expenses", "33,02,50,000"],
        ["Profit Before Tax", "1,47,50,000"],  # Thin margins = some concern
        ["Tax (@ 25.168%)", "37,12,000"],
        ["Net Profit After Tax", "1,10,38,000"],
    ]
    t = Table(income_data, colWidths=[11 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.lightgrey]),
        ("BACKGROUND", (0, -1), (-1, -1), colors.lightblue),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))
    story.append(Paragraph("Self-Declaration: We certify that the information given in this return is correct. No pending litigation. Company is in compliance with all applicable laws. — Rajesh Kumar Vardhaman, MD", styles["ICSmallNote"]))

    doc.build(story)
    print(f"[DEMO] Generated: {path}")
    return str(path)


def main():
    if not REPORTLAB_AVAILABLE:
        print("[DEMO] Cannot generate PDFs: reportlab not installed.")
        print("[DEMO] Run: pip install reportlab")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[DEMO] Generating Vardhaman Infra demo PDFs in: {OUTPUT_DIR}")

    generate_gstr1()
    generate_bank_statement()
    generate_annual_report()
    generate_itr()

    print(f"\n[DEMO] ✅ All 4 demo PDFs generated in {OUTPUT_DIR}")
    print("[DEMO] Upload these to the app to see the demo scenario play out.")


if __name__ == "__main__":
    main()
