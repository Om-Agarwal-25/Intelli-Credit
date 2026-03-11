"""
XGBoost Model Training on Synthetic Indian NPA Dataset
Generates 1000 synthetic loan samples with realistic Indian NPA patterns,
trains XGBoost, saves model, and logs to MLflow.

Run once: python models/train_synthetic.py
"""

import numpy as np
import pandas as pd
import pickle
import os
from pathlib import Path


def generate_synthetic_dataset(n_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Generate realistic synthetic Indian corporate loan dataset."""
    rng = np.random.default_rng(seed)

    data = []
    for _ in range(n_samples):
        # Randomly decide if this is an NPA case (35% NPA rate — realistic for India)
        is_npa = rng.random() < 0.35

        if is_npa:
            # NPA pattern: weaknesses across multiple dimensions
            c1 = rng.uniform(10, 55)   # Poor character (litigation, disqualification)
            c2 = rng.uniform(15, 55)   # Weak capacity (DSCR < 1)
            c3 = rng.uniform(20, 60)   # Thin capital
            c4 = rng.uniform(25, 65)   # Questionable collateral
            c5 = rng.uniform(20, 65)   # Poor conditions

            # Specific NPA markers
            dscr = rng.uniform(0.5, 1.25)           # Below safe threshold
            gearing = rng.uniform(2.0, 5.0)         # High leverage
            gst_bank_match = rng.uniform(30, 75)    # Low match (suspicious)
            revenue_growth = rng.uniform(-0.20, 0.05)  # Declining revenue
            has_din_disq = rng.random() < 0.45      # 45% have disqualified director
            has_litigation = rng.random() < 0.60    # 60% undisclosed litigation
            has_going_concern = rng.random() < 0.40
        else:
            # Good borrower
            c1 = rng.uniform(55, 95)
            c2 = rng.uniform(55, 95)
            c3 = rng.uniform(50, 90)
            c4 = rng.uniform(55, 90)
            c5 = rng.uniform(55, 90)

            dscr = rng.uniform(1.25, 3.5)
            gearing = rng.uniform(0.3, 2.0)
            gst_bank_match = rng.uniform(75, 100)
            revenue_growth = rng.uniform(0.05, 0.35)
            has_din_disq = rng.random() < 0.05   # 5% good borrowers have minor issues
            has_litigation = rng.random() < 0.10
            has_going_concern = rng.random() < 0.05

        composite = c1 * 0.25 + c2 * 0.30 + c3 * 0.15 + c4 * 0.20 + c5 * 0.10

        # Add noise to composite
        composite += rng.normal(0, 3)
        composite = max(0, min(100, composite))

        data.append({
            "c1_character": c1,
            "c2_capacity": c2,
            "c3_capital": c3,
            "c4_collateral": c4,
            "c5_conditions": c5,
            "composite_score": composite,
            "c1_flag_count": int(has_din_disq) + int(has_litigation),
            "c2_flag_count": int(has_going_concern),
            "dscr": dscr,
            "gearing_ratio": gearing,
            "gst_bank_match_pct": gst_bank_match,
            "revenue_growth_3yr": revenue_growth,
            "has_din_disqualification": int(has_din_disq),
            "has_undisclosed_litigation": int(has_litigation),
            "has_going_concern": int(has_going_concern),
            "is_npa": int(is_npa),
        })

    return pd.DataFrame(data)


def train_model(df: pd.DataFrame):
    """Train XGBoost classifier and return model."""
    from xgboost import XGBClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, roc_auc_score

    feature_cols = [
        "c1_character", "c2_capacity", "c3_capital", "c4_collateral", "c5_conditions",
        "composite_score", "c1_flag_count", "c2_flag_count",
    ]

    X = df[feature_cols]
    y = df["is_npa"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, y_prob)

    print("\n[TRAIN] XGBoost Training Complete")
    print(f"[TRAIN] AUC-ROC: {auc:.4f}")
    print("[TRAIN] Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Non-NPA", "NPA"]))

    return model, auc


def main():
    print("[TRAIN] Generating 1000 synthetic Indian NPA samples...")
    df = generate_synthetic_dataset(1000)
    print(f"[TRAIN] Dataset: {len(df)} samples, {df['is_npa'].sum()} NPAs ({df['is_npa'].mean()*100:.1f}%)")

    # Save dataset
    out_dir = Path(__file__).parent
    out_dir.mkdir(exist_ok=True)
    df.to_csv(out_dir / "synthetic_npa_dataset.csv", index=False)
    print("[TRAIN] Dataset saved to models/synthetic_npa_dataset.csv")

    # Train
    model, auc = train_model(df)

    # Save model
    model_path = out_dir / "xgboost_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    print(f"[TRAIN] Model saved to {model_path}")

    # MLflow logging (optional)
    try:
        import mlflow

        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "./mlruns")
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment("intelli_credit_xgboost")

        with mlflow.start_run(run_name="synthetic_npa_v1"):
            mlflow.log_params({
                "n_samples": 1000,
                "n_estimators": 200,
                "max_depth": 5,
                "learning_rate": 0.1,
            })
            mlflow.log_metrics({"auc_roc": auc})
            mlflow.sklearn.log_model(model, "xgboost_model")
            print(f"[TRAIN] MLflow run logged. View at: {tracking_uri}")
    except Exception as e:
        print(f"[TRAIN] MLflow logging skipped: {e}")

    print("\n[TRAIN] ✅ Done! XGBoost model ready.")
    return model


if __name__ == "__main__":
    main()
