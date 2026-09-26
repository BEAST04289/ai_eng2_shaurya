from __future__ import annotations

import numpy as np

RETURN_COST_RS = 1150.0
CONFIRMATION_CALL_COST_RS = 45.0
CALL_PREVENTION_RATE = 0.35
HOLD_CANCEL_RATE = 0.12
RECOMMENDED_CALL_THRESHOLD = 0.13


def theoretical_call_break_even_probability() -> float:
    """Risk p where expected avoided return cost equals call cost.

    Expected benefit = p(return) * 35% prevented * Rs1150.
    """
    return CONFIRMATION_CALL_COST_RS / (RETURN_COST_RS * CALL_PREVENTION_RATE)


def call_policy_metrics(y_true, score, threshold: float) -> dict:
    y = np.asarray(y_true, dtype=int)
    s = np.asarray(score, dtype=float)
    flagged = s >= threshold
    n_flagged = int(flagged.sum())
    tp = int(y[flagged].sum()) if n_flagged else 0
    positives = int(y.sum())
    precision = tp / n_flagged if n_flagged else 0.0
    recall = tp / positives if positives else 0.0
    expected_prevented_returns = tp * CALL_PREVENTION_RATE
    gross_avoided_cost = expected_prevented_returns * RETURN_COST_RS
    call_cost = n_flagged * CONFIRMATION_CALL_COST_RS
    net_savings = gross_avoided_cost - call_cost
    return {
        "threshold": float(threshold),
        "flagged": n_flagged,
        "flag_rate": float(n_flagged / len(y)) if len(y) else 0.0,
        "true_returns_in_flagged": tp,
        "precision": float(precision),
        "recall": float(recall),
        "expected_prevented_returns": float(expected_prevented_returns),
        "gross_avoided_return_cost_rs": float(gross_avoided_cost),
        "call_cost_rs": float(call_cost),
        "net_savings_rs": float(net_savings),
        "net_savings_per_order_rs": float(net_savings / len(y)) if len(y) else 0.0,
    }


def find_best_call_threshold(y_true, score, lo=0.05, hi=0.50, step=0.01) -> dict:
    thresholds = np.arange(lo, hi + 1e-9, step)
    rows = [call_policy_metrics(y_true, score, float(t)) for t in thresholds]
    return max(rows, key=lambda r: r["net_savings_rs"])
