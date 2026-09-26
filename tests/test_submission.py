from pathlib import Path
import pandas as pd


def test_predictions_shape_if_present():
    root = Path(__file__).resolve().parents[1]
    pred = root / "predictions.csv"
    sample = root / "data" / "raw" / "sample_submission.csv"
    if not pred.exists() or not sample.exists():
        return
    a=pd.read_csv(pred)
    b=pd.read_csv(sample)
    assert list(a.columns)==list(b.columns)
    assert len(a)==len(b)
    assert a.order_id.tolist()==b.order_id.tolist()
    assert a.order_id.is_unique
    assert a.score.notna().all()
    assert a.score.between(0,1).all()
