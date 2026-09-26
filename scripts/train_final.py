from __future__ import annotations

import json
import sys
from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.business import theoretical_call_break_even_probability, RECOMMENDED_CALL_THRESHOLD
from src.config import TRAIN_FILE, CUSTOMERS_FILE, PRODUCTS_FILE, MODEL_FILE, LOGISTIC_FILE, METADATA_FILE, ARTIFACTS
from src.data import read_csv, canonicalize_train, load_reference
from src.features import build_features, FEATURES, CAT_FEATURES, LEAKAGE_COLUMNS
from src.model import fit_catboost, fit_logistic, ENSEMBLE_CATBOOST_WEIGHT, CATBOOST_PARAMS


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    train = canonicalize_train(read_csv(TRAIN_FILE))
    customers, products = load_reference(CUSTOMERS_FILE, PRODUCTS_FILE)
    X = build_features(train, customers, products)
    y = train.returned.astype(int)

    cb = fit_catboost(X, y)
    lr = fit_logistic(X, y)
    cb.save_model(str(MODEL_FILE))
    joblib.dump(lr, LOGISTIC_FILE)

    metadata = {
        "model": "50/50 ensemble: CatBoostClassifier + LogisticRegression",
        "ensemble_catboost_weight": ENSEMBLE_CATBOOST_WEIGHT,
        "catboost_params": CATBOOST_PARAMS,
        "training_rows": int(len(train)),
        "training_start": str(train.order_placed_at.min()),
        "training_end": str(train.order_placed_at.max()),
        "return_rate": float(y.mean()),
        "features": FEATURES,
        "categorical_features": CAT_FEATURES,
        "excluded_leakage_columns": LEAKAGE_COLUMNS,
        "theoretical_call_break_even_probability": theoretical_call_break_even_probability(),
        "recommended_call_threshold": RECOMMENDED_CALL_THRESHOLD,
        "recommended_action": "confirmation_call_not_automatic_hold",
    }
    METADATA_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print("Saved", MODEL_FILE)
    print("Saved", LOGISTIC_FILE)
    print("Saved", METADATA_FILE)

if __name__ == "__main__":
    main()
