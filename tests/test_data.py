import pandas as pd
import pytest
from src.data import canonicalize_train

BASE = {
    "order_placed_at":"2025-04-01 10:00","customer_id":"C","sku":"S","sales_channel":"web",
    "payment_mode":"cod","discount_pct":0,"qty":1,"order_value_inr":1000,
    "promised_delivery_days":5,"delivery_pincode":"411001","is_gift":"N",
    "customer_prior_orders":0,"customer_prior_returns":0,"delivery_note":None,
    "last_service_event_type":"NONE","pickup_scheduled_at":None,"returned":0,
}


def test_partner_duplicate_prefers_crm():
    a={**BASE,"order_id":"O1","source":"crm"}
    b={**BASE,"order_id":"O1","source":"partner_feed"}
    out=canonicalize_train(pd.DataFrame([b,a]))
    assert len(out)==1
    assert out.iloc[0].source=="crm"


def test_conflicting_duplicate_fails():
    a={**BASE,"order_id":"O1","source":"crm"}
    b={**BASE,"order_id":"O1","source":"partner_feed","qty":2}
    with pytest.raises(ValueError):
        canonicalize_train(pd.DataFrame([a,b]))
