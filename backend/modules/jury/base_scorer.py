"""
Module 3 — XGBoost Base Scorer
Loads trained model, computes composite score, generates SHAP explanation.
Falls back to rule-based scoring if model file not found.
"""

import os
import pickle
import numpy as np
from pathlib import Path

MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "xgboost_model.pkl"


def _features_from_five_cs(five_cs: dict) -> np.ndarray:
    """Convert Five Cs dict to feature vector for XGBoost."""
    return np.array([[
        five_cs.get("C1", 70),
        five_cs.get("C2", 70),
        five_cs.get("C3", 70),
        five_cs.get("C4", 70),
        five_cs.get("C5", 70),
        five_cs.get("composite", 70),
        five_cs.get("flag_counts", {}).get("C1", 0),
        five_cs.get("flag_counts", {}).get("C2", 0),
    ]])


def compute_base_score(five_cs: dict) -> dict:
    """Compute XGBoost base score. Returns score dict with SHAP values."""
    composite = five_cs.get("composite", 65.0)

    model = _load_model()
    shap_values = None
    model_used = "rule_based"

    if model:
        try:
            features = _features_from_five_cs(five_cs)
            # Model outputs probability of non-NPA (good credit)
            prob = float(model.predict_proba(features)[0][1])
            xgb_score = round(prob * 100, 1)
            # Blend XGBoost score with Five Cs composite (50/50)
            composite = round((xgb_score * 0.5 + composite * 0.5), 1)
            model_used = "xgboost"

            # SHAP explanation
            try:
                import shap
                explainer = shap.TreeExplainer(model)
                sv = explainer.shap_values(features)
                feature_names = ["C1_char", "C2_cap", "C3_capital", "C4_col", "C5_cond", "composite", "c1_flags", "c2_flags"]
                # Binary XGBoost: sv may be a plain 2D array or list-of-2
                if isinstance(sv, list) and len(sv) == 2:
                    sv_vals = sv[1][0]  # positive class shap values for first sample
                elif isinstance(sv, list) and len(sv) == 1:
                    sv_vals = sv[0][0]
                else:
                    sv_vals = sv[0]  # single array
                shap_values = [
                    {"feature": feature_names[i], "shap": round(float(sv_vals[i]), 3)}
                    for i in range(min(len(feature_names), len(sv_vals)))
                ]
                shap_values.sort(key=lambda x: abs(x["shap"]), reverse=True)
            except Exception as e:
                print(f"[SCORER] SHAP failed: {e}")

        except Exception as e:
            print(f"[SCORER] XGBoost predict failed: {e}")

    # Decision mapping
    if composite >= 65:
        decision = "APPROVE"
    elif composite >= 50:
        decision = "CONDITIONAL"
    else:
        decision = "REJECT"

    return {
        "composite": composite,
        "decision": decision,
        "model_used": model_used,
        "shap_values": shap_values or [],
        "five_cs": five_cs,
    }


def _load_model():
    """Load XGBoost model from disk."""
    if MODEL_PATH.exists():
        try:
            with open(MODEL_PATH, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"[SCORER] Model load failed: {e}")
    else:
        print(f"[SCORER] Model not found at {MODEL_PATH}. Run: python models/train_synthetic.py")
    return None
