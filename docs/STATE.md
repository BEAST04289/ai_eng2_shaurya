# State

Current phase: VERIFIED STARTER; RE-RUN LOCALLY, THEN FINALIZE

Already done:
- starter smoke-tested against the supplied CSVs
- 6/6 scaffold tests pass in this environment
- FastAPI `/health` and `/predict` smoke-tested successfully
- data audit completed
- leakage fields identified
- duplicate rule established
- October payment scaling bug identified
- business action reframed from auto-hold to targeted confirmation call
- model/evaluation/service scaffold created

Reference expanding temporal results from this scaffold run (re-run locally before quoting):
- 2025Q4 ensemble AP/AUC: ~0.328 / 0.766
- 2026Q1 ensemble AP/AUC: ~0.387 / 0.774
- 2026Q2 ensemble AP/AUC: ~0.414 / 0.780
- 3-fold OOF ensemble AP/AUC: ~0.374 / 0.773
- 3-fold best call thresholds: 0.12, 0.13, 0.13
- chosen operating threshold: 0.13
- OOF at 0.13: ~27.3% flagged, ~26.3% precision, ~63.6% recall
- OOF modeled net savings: ~Rs16.68/order using policy call economics and 35% prevention assumption
- planning at 700 orders/month: ~191 calls, ~18 prevented returns, ~Rs11.7k net/month if the pilot effect generalizes

Next commands on the user's machine:
1. `python scripts/audit_data.py`
2. `pytest -q`
3. `python scripts/evaluate.py`
4. inspect `artifacts/evaluation.json`
5. `python scripts/train_final.py`
6. `python scripts/make_predictions.py`
7. `pytest -q`
8. `uvicorn app:app --reload`
9. test `/health`, `/predict`, and the browser screen

Do not claim a hidden-test result. Expected hidden metric must be stated as an estimate from temporal backtests.
