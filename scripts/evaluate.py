from __future__ import annotations

import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, average_precision_score, brier_score_loss, precision_score, recall_score, roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.business import find_best_call_threshold, theoretical_call_break_even_probability, call_policy_metrics
from src.config import TRAIN_FILE, CUSTOMERS_FILE, PRODUCTS_FILE, EVAL_FILE, ARTIFACTS
from src.data import read_csv, canonicalize_train, load_reference
from src.features import build_features
from src.model import fit_catboost, fit_logistic, predict_catboost, predict_logistic, ENSEMBLE_CATBOOST_WEIGHT, CATBOOST_PARAMS

FOLDS = [
    ("2025Q4", pd.Timestamp("2025-10-01"), pd.Timestamp("2026-01-01")),
    ("2026Q1", pd.Timestamp("2026-01-01"), pd.Timestamp("2026-04-01")),
    ("2026Q2", pd.Timestamp("2026-04-01"), pd.Timestamp("2026-07-01")),
]


def metrics(y, p, threshold=0.5) -> dict:
    pred = np.asarray(p) >= threshold
    return {
        "n": int(len(y)),
        "positive_rate": float(np.mean(y)),
        "roc_auc": float(roc_auc_score(y, p)),
        "average_precision": float(average_precision_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "accuracy_at_0_5": float(accuracy_score(y, pred)),
        "precision_at_0_5": float(precision_score(y, pred, zero_division=0)),
        "recall_at_0_5": float(recall_score(y, pred, zero_division=0)),
    }


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    train = canonicalize_train(read_csv(TRAIN_FILE))
    customers, products = load_reference(CUSTOMERS_FILE, PRODUCTS_FILE)
    X = build_features(train, customers, products).reset_index(drop=True)
    y = train.returned.astype(int).reset_index(drop=True)
    dates = train.order_placed_at.reset_index(drop=True)

    results = {
        "target": {"canonical_n": int(len(train)), "returns": int(y.sum()), "return_rate": float(y.mean()), "majority_accuracy": float(max(y.mean(), 1-y.mean()))},
        "folds": [],
        "primary_metric": "average_precision",
        "secondary_metric": "roc_auc",
        "deployed_model": "50/50 probability average of logistic regression and CatBoost",
        "ensemble_catboost_weight": ENSEMBLE_CATBOOST_WEIGHT,
        "catboost_params": CATBOOST_PARAMS,
        "call_break_even_probability": theoretical_call_break_even_probability(),
    }

    oof_y, oof_ensemble = [], []

    for name, start, end in FOLDS:
        tr = dates < start
        va = (dates >= start) & (dates < end)
        if tr.sum() == 0 or va.sum() == 0:
            continue

        lr = fit_logistic(X.loc[tr], y.loc[tr])
        cb = fit_catboost(X.loc[tr], y.loc[tr])
        p_lr = predict_logistic(lr, X.loc[va])
        p_cb = predict_catboost(cb, X.loc[va])
        p_ens = ENSEMBLE_CATBOOST_WEIGHT * p_cb + (1 - ENSEMBLE_CATBOOST_WEIGHT) * p_lr

        results["folds"].append({
            "fold": name,
            "train_n": int(tr.sum()),
            "valid_n": int(va.sum()),
            "valid_start": str(start.date()),
            "valid_end_exclusive": str(end.date()),
            "logistic": metrics(y.loc[va], p_lr),
            "catboost": metrics(y.loc[va], p_cb),
            "ensemble": metrics(y.loc[va], p_ens),
            "business_theoretical_threshold": call_policy_metrics(y.loc[va], p_ens, theoretical_call_break_even_probability()),
            "business_empirical_best_threshold": find_best_call_threshold(y.loc[va], p_ens),
        })
        oof_y.extend(y.loc[va].tolist())
        oof_ensemble.extend(p_ens.tolist())

    if oof_y:
        results["ensemble_oof"] = metrics(np.array(oof_y), np.array(oof_ensemble))
        results["ensemble_oof_best_call_threshold"] = find_best_call_threshold(np.array(oof_y), np.array(oof_ensemble))

    EVAL_FILE.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("Wrote", EVAL_FILE)
    for f in results["folds"]:
        print(f["fold"],
              "LR AP/AUC=", round(f["logistic"]["average_precision"],3), round(f["logistic"]["roc_auc"],3),
              "CB AP/AUC=", round(f["catboost"]["average_precision"],3), round(f["catboost"]["roc_auc"],3),
              "ENS AP/AUC=", round(f["ensemble"]["average_precision"],3), round(f["ensemble"]["roc_auc"],3))

if __name__ == "__main__":
    main()
