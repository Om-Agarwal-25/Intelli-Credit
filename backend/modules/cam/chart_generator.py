"""
Module 4 — Chart Generator
Creates matplotlib charts embedded in the CAM .docx report.
"""

import io
import os
from pathlib import Path


def create_gst_bank_chart(monthly_data: dict) -> bytes:
    """Dual bar chart: GST Declared vs Bank Credits over 24 months."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        months = list(monthly_data.get("months", range(1, 13)))
        gst_values = monthly_data.get("gst_values", [280, 295, 310, 150, 140, 300, 315, 320, 330, 340, 305, 290])
        bank_values = monthly_data.get("bank_values", [275, 290, 305, 55, 52, 295, 310, 315, 325, 335, 300, 285])
        month_labels = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]

        x = np.arange(len(month_labels[:len(gst_values)]))
        width = 0.35

        fig, ax = plt.subplots(figsize=(12, 5))

        # Identify anomaly months (discrepancy > 40%)
        anomaly_colors_gst = []
        anomaly_colors_bank = []
        for g, b in zip(gst_values, bank_values):
            if g > 0 and abs(g - b) / g > 0.40:
                anomaly_colors_gst.append("#E53E3E")
                anomaly_colors_bank.append("#FC8181")
            else:
                anomaly_colors_gst.append("#2B6CB0")
                anomaly_colors_bank.append("#4A9DB5")

        bars1 = ax.bar(x - width / 2, gst_values, width, label="GST Declared (₹ Lakhs)",
                       color=anomaly_colors_gst, alpha=0.9)
        bars2 = ax.bar(x + width / 2, bank_values, width, label="Bank Credits (₹ Lakhs)",
                       color=anomaly_colors_bank, alpha=0.9)

        ax.set_xlabel("Month", fontsize=11)
        ax.set_ylabel("Amount (₹ Lakhs)", fontsize=11)
        ax.set_title("GST Declared Revenue vs. Bank Credits — FY2024\n(Red bars = anomaly months >40% discrepancy)", fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(month_labels[:len(gst_values)])
        ax.legend()
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close()
        return buf.getvalue()

    except ImportError:
        return b""


def create_five_cs_radar(five_cs: dict) -> bytes:
    """Radar/spider chart for Five Cs dimensions."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import numpy as np

        categories = ["C1\nCharacter", "C2\nCapacity", "C3\nCapital", "C4\nCollateral", "C5\nConditions"]
        values = [
            five_cs.get("C1", 70),
            five_cs.get("C2", 70),
            five_cs.get("C3", 70),
            five_cs.get("C4", 70),
            five_cs.get("C5", 70),
        ]
        values += values[:1]  # close the polygon

        angles = [n / float(len(categories)) * 2 * np.pi for n in range(len(categories))]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.set_facecolor("#F0F4FF")

        ax.plot(angles, values, "o-", linewidth=2, color="#1B2B4B")
        ax.fill(angles, values, alpha=0.25, color="#4A9DB5")

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(["20", "40", "60", "80", "100"], fontsize=8)
        ax.set_title("Five Cs Credit Assessment", fontsize=14, pad=20)

        # Add score labels
        for angle, val, cat in zip(angles[:-1], values[:-1], categories):
            ax.annotate(f"{val:.0f}", xy=(angle, val), fontsize=9,
                        ha="center", va="center",
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor="gray"))

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close()
        return buf.getvalue()

    except ImportError:
        return b""


def create_score_journey_chart(base_score: float, after_prosecution: float,
                                after_defence: float, jury_score: float) -> bytes:
    """Horizontal bar chart showing score journey."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        stages = ["Base Score\n(XGBoost)", "After\nProsecution", "After\nDefence", "Final\nJury Score"]
        scores = [base_score, after_prosecution, after_defence, jury_score]
        colors = ["#4A9DB5", "#E53E3E", "#38A169", "#1B2B4B"]

        fig, ax = plt.subplots(figsize=(10, 3))
        bars = ax.barh(stages, scores, color=colors, height=0.5, alpha=0.85)

        ax.set_xlim(0, 100)
        ax.axvline(x=65, color="#38A169", linestyle="--", alpha=0.5, label="Approve ≥65")
        ax.axvline(x=50, color="#DD6B20", linestyle="--", alpha=0.5, label="Conditional ≥50")
        ax.set_xlabel("Score / 100", fontsize=11)
        ax.set_title("Credit Score Journey — AI Agent Jury Analysis", fontsize=12)
        ax.legend(fontsize=9)

        for bar, score in zip(bars, scores):
            ax.text(score + 0.5, bar.get_y() + bar.get_height() / 2,
                    f"{score:.1f}", va="center", fontsize=11, fontweight="bold")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close()
        return buf.getvalue()

    except ImportError:
        return b""
