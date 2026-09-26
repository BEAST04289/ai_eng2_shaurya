from __future__ import annotations

import sys
from pathlib import Path
import joblib
import numpy as np
from catboost import CatBoostClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import TEST_FILE, CUSTOMERS_FILE, PRODUCTS_FILE, SAMPLE_FILE, MODEL_FILE, LOGISTIC_FILE, PREDICTIONS_FILE
from src.data import read_csv, canonicalize_test, load_reference
from src.features import build_features
from src.model import predict_ensemble


def main() -> None:
    if not MODEL_FILE.exists() or not LOGISTIC_FILE.exists():
        raise FileNotFoundError("Run python scripts/train_final.py first")

    test_raw = read_csv(TEST_FILE)
    test = canonicalize_test(test_raw)
    sample = read_csv(SAMPLE_FILE)
    customers, products = load_reference(CUSTOMERS_FILE, PRODUCTS_FILE)

    cb = CatBoostClassifier(); cb.load_model(str(MODEL_FILE))
    lr = joblib.load(LOGISTIC_FILE)
    X = build_features(test, customers, products)
    score = predict_ensemble(cb, lr, X)

    if len(sample) != len(test):
        raise ValueError(f"sample rows={len(sample)} but test rows={len(test)}")
    if sample["order_id"].tolist() != test["order_id"].tolist():
        raise ValueError("sample_submission order_id order does not exactly match test_unlabelled")
    if not np.isfinite(score).all():
        raise ValueError("Non-finite prediction score")
    if not ((score >= 0) & (score <= 1)).all():
        raise ValueError("Prediction score outside [0,1]")

    out = sample.copy(); out["score"] = score.astype(float)
    if list(out.columns) != list(sample.columns): raise AssertionError("Submission columns changed")
    if out["order_id"].duplicated().any(): raise AssertionError("Duplicate order_id in predictions")
    out.to_csv(PREDICTIONS_FILE, index=False)
    print("Wrote", PREDICTIONS_FILE, "rows=", len(out))
    print("score min/mean/max=", float(out.score.min()), float(out.score.mean()), float(out.score.max()))

if __name__ == "__main__":
    main()
