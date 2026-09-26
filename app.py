from __future__ import annotations

from pathlib import Path
from typing import Optional
import joblib
import pandas as pd
from catboost import CatBoostClassifier
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict

from src.business import RECOMMENDED_CALL_THRESHOLD
from src.config import CUSTOMERS_FILE, PRODUCTS_FILE, MODEL_FILE, LOGISTIC_FILE
from src.data import load_reference
from src.explain import readable_reasons
from src.features import build_features
from src.model import predict_ensemble

app = FastAPI(title="Kestrel Returns Risk", version="1.0")
ROOT = Path(__file__).resolve().parent
_cb = _lr = _customers = _products = None

class OrderRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    order_id: str
    order_placed_at: str
    customer_id: str
    sku: str
    sales_channel: str
    payment_mode: str
    discount_pct: float
    qty: int
    order_value_inr: float
    promised_delivery_days: int
    delivery_pincode: str | int
    is_gift: str
    customer_prior_orders: int
    customer_prior_returns: int
    delivery_note: Optional[str] = None
    last_service_event_type: Optional[str] = None
    pickup_scheduled_at: Optional[str] = None
    source: Optional[str] = None


def get_runtime():
    global _cb, _lr, _customers, _products
    if _cb is None:
        if not MODEL_FILE.exists() or not LOGISTIC_FILE.exists():
            raise RuntimeError("Model artifacts missing. Run `python scripts/train_final.py` first.")
        _cb = CatBoostClassifier(); _cb.load_model(str(MODEL_FILE))
        _lr = joblib.load(LOGISTIC_FILE)
        _customers, _products = load_reference(CUSTOMERS_FILE, PRODUCTS_FILE)
    return _cb, _lr, _customers, _products

@app.get("/")
def home(): return FileResponse(ROOT / "static" / "index.html")

@app.get("/health")
def health(): return {"status":"ok", "model_ready": MODEL_FILE.exists() and LOGISTIC_FILE.exists()}

@app.post("/predict")
def predict(order: OrderRequest):
    try:
        cb, lr, customers, products = get_runtime()
        row = pd.DataFrame([order.model_dump()]); row["order_placed_at"] = pd.to_datetime(row["order_placed_at"], errors="raise")
        X = build_features(row, customers, products)
        score = float(predict_ensemble(cb, lr, X)[0])
        reasons = readable_reasons(cb, X, n=3)
        threshold = RECOMMENDED_CALL_THRESHOLD
        action = "confirmation_call_before_dispatch" if score >= threshold else "ship_normally"
        return {
            "order_id": order.order_id,
            "return_risk_score": round(score,6),
            "recommended_action": action,
            "decision_threshold": round(threshold,6),
            "reasons": reasons,
            "explanation_basis": "Reasons are local CatBoost-component contributions; risk score is a 50/50 CatBoost/logistic ensemble.",
            "guardrail": "Do not auto-hold solely from this score; hold cancellation economics are incomplete." if score >= threshold else "No model-triggered intervention.",
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
