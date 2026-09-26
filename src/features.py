from __future__ import annotations

import re
import numpy as np
import pandas as pd

# Explicit allow-list of fields available/derivable before dispatch.
# Intentionally absent: source, last_service_event_type, pickup_scheduled_at,
# order_id, customer_id.
CAT_FEATURES = [
    "sku",
    "sales_channel",
    "payment_mode",
    "is_gift",
    "delivery_note_norm",
    "city",
    "state",
    "shield_member",
    "family",
    "order_month",
    "order_dow",
    "pincode_prefix3",
]

NUM_FEATURES = [
    "discount_pct",
    "qty",
    "order_value_corrected",
    "promised_delivery_days",
    "customer_prior_orders",
    "customer_prior_returns",
    "prior_return_rate",
    "list_price_inr",
    "warranty_months",
    "order_hour",
    "order_weekend",
    "account_age_days",
    "product_age_days",
    "value_vs_list_ratio",
    "pincode_missing",
]

FEATURES = CAT_FEATURES + NUM_FEATURES
LEAKAGE_COLUMNS = ["last_service_event_type", "pickup_scheduled_at"]


def normalize_note(value) -> str:
    if pd.isna(value) or not str(value).strip():
        return "MISSING"
    text = str(value).lower().strip()
    text = re.sub(r"\d+", "#", text)
    text = re.sub(r"\s+", " ", text)
    return text[:180]


def build_features(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    out = orders.copy()
    if not pd.api.types.is_datetime64_any_dtype(out["order_placed_at"]):
        out["order_placed_at"] = pd.to_datetime(out["order_placed_at"], errors="raise")

    out = out.merge(customers, on="customer_id", how="left", validate="many_to_one")
    out = out.merge(products, on="sku", how="left", validate="many_to_one")

    if out["city"].isna().any() or out["family"].isna().any():
        # Unknown IDs can happen in a future online request; CatBoost can still
        # handle missing numeric fields and explicit MISSING categoricals.
        pass

    dt = out["order_placed_at"]
    out["order_month"] = dt.dt.month.astype("Int64").astype(str)
    out["order_dow"] = dt.dt.dayofweek.astype("Int64").astype(str)
    out["order_hour"] = dt.dt.hour.astype(float)
    out["order_weekend"] = (dt.dt.dayofweek >= 5).astype(int)

    out["account_age_days"] = (dt - out["signup_date"]).dt.days.clip(lower=0)
    out["product_age_days"] = (dt - out["launch_date"]).dt.days.clip(lower=0)

    prior_orders = pd.to_numeric(out["customer_prior_orders"], errors="coerce")
    prior_returns = pd.to_numeric(out["customer_prior_returns"], errors="coerce")
    out["prior_return_rate"] = np.where(
        prior_orders > 0, prior_returns / prior_orders, 0.0
    )

    list_price = pd.to_numeric(out["list_price_inr"], errors="coerce")
    qty = pd.to_numeric(out["qty"], errors="coerce")
    discount = pd.to_numeric(out["discount_pct"], errors="coerce")
    stored_value = pd.to_numeric(out["order_value_inr"], errors="coerce")

    expected_checkout = list_price * qty * (1 - discount / 100.0)
    ratio = stored_value / expected_checkout.replace(0, np.nan)

    # October-2025 payment-gateway rows are exactly 100x in the supplied pack.
    # Detect by scale ratio rather than hard-coding a date so inference remains sane.
    scaled = ratio.between(50, 150, inclusive="both")
    out["order_value_corrected"] = np.where(scaled, stored_value / 100.0, stored_value)
    out["value_vs_list_ratio"] = (
        out["order_value_corrected"] / (list_price * qty).replace(0, np.nan)
    )

    pincode = out["delivery_pincode"].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6)
    out["pincode_missing"] = (pincode == "000000").astype(int)
    out["pincode_prefix3"] = pincode.str[:3]
    out["delivery_note_norm"] = out["delivery_note"].map(normalize_note)

    X = out[FEATURES].copy()
    for c in CAT_FEATURES:
        X[c] = X[c].fillna("MISSING").astype(str)
    for c in NUM_FEATURES:
        X[c] = pd.to_numeric(X[c], errors="coerce")
    return X
