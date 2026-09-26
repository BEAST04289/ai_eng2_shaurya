from __future__ import annotations

from catboost import Pool
import numpy as np
import pandas as pd

from .features import CAT_FEATURES, FEATURES
from .model import ensure_feature_order

FRIENDLY = {
    "customer_prior_returns": "Prior returns",
    "prior_return_rate": "Prior return rate",
    "customer_prior_orders": "Prior orders",
    "payment_mode": "Payment mode",
    "shield_member": "Shield membership",
    "family": "Product family",
    "sku": "Product",
    "sales_channel": "Sales channel",
    "discount_pct": "Discount",
    "is_gift": "Gift order",
    "promised_delivery_days": "Promised delivery time",
    "pincode_missing": "Address quality",
    "pincode_prefix3": "Delivery area",
    "delivery_note_norm": "Delivery-note pattern",
    "warranty_months": "Warranty",
    "qty": "Quantity",
    "order_value_corrected": "Order value",
}


def _format_value(feature: str, value) -> str:
    if feature == "prior_return_rate" and pd.notna(value):
        return f"{float(value):.0%}"
    if feature == "discount_pct" and pd.notna(value):
        return f"{float(value):.0f}%"
    if feature == "order_value_corrected" and pd.notna(value):
        return f"Rs {float(value):,.0f}"
    if feature == "pincode_missing":
        return "default/missing pincode" if int(value or 0) == 1 else "normal pincode"
    return str(value)


def readable_reasons(model, X_one: pd.DataFrame, n: int = 3) -> list[dict]:
    X = ensure_feature_order(X_one)
    pool = Pool(X, cat_features=CAT_FEATURES)
    shap = model.get_feature_importance(pool, type="ShapValues")
    contrib = np.asarray(shap)[0][:-1]
    values = X.iloc[0]

    ranked = sorted(
        zip(FEATURES, contrib),
        key=lambda x: x[1],
        reverse=True,
    )
    positive = [(f, c) for f, c in ranked if c > 0]
    chosen = positive[:n] if positive else sorted(ranked, key=lambda x: abs(x[1]), reverse=True)[:n]

    reasons = []
    for feature, contribution in chosen:
        label = FRIENDLY.get(feature, feature.replace("_", " ").title())
        reasons.append(
            {
                "feature": feature,
                "reason": f"{label}: {_format_value(feature, values[feature])}",
                "model_contribution": round(float(contribution), 4),
            }
        )
    return reasons
