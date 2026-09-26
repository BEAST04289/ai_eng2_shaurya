import pandas as pd
from src.features import build_features, FEATURES, LEAKAGE_COLUMNS


def test_feature_allowlist_excludes_post_outcome_fields():
    for c in LEAKAGE_COLUMNS:
        assert c not in FEATURES


def test_october_scale_correction_and_no_leakage_columns():
    orders = pd.DataFrame([{
        "order_id":"O1","order_placed_at":pd.Timestamp("2025-10-10"),"customer_id":"C1","sku":"S1",
        "sales_channel":"web","payment_mode":"cod","discount_pct":10,"qty":1,
        "order_value_inr":90000.0,"promised_delivery_days":5,"delivery_pincode":"000000","is_gift":"N",
        "customer_prior_orders":1,"customer_prior_returns":0,"delivery_note":None,
        "last_service_event_type":"REVERSE_PICKUP","pickup_scheduled_at":"2025-10-20","source":"crm"
    }])
    customers = pd.DataFrame([{"customer_id":"C1","city":"Pune","state":"MH","signup_date":pd.Timestamp("2025-01-01"),"shield_member":"N"}])
    products = pd.DataFrame([{"sku":"S1","family":"Air Fryer","model_name":"X","list_price_inr":1000.0,"warranty_months":12,"launch_date":pd.Timestamp("2024-01-01")}])
    X=build_features(orders,customers,products)
    assert list(X.columns) == FEATURES
    assert X.loc[0,"order_value_corrected"] == 900.0
    assert X.loc[0,"pincode_missing"] == 1
