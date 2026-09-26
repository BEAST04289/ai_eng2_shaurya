# Kestrel Home — Returns Risk

A small leakage-safe pre-dispatch return-risk service for the supplied Kestrel Home hiring task.

## Decision
The model produces a continuous return-risk score. The operational recommendation is **targeted pre-dispatch confirmation calls**, not automatic holds, until Kestrel supplies enough information to price the 12% hold-cancellation risk.

Policy economics: return Rs1,150; confirmation call Rs45; pilot prevented ~35% of otherwise-occurring returns on called orders. Theoretical call break-even risk is about 11.18%.

## Why not "95% accuracy"?
Canonical training return prevalence is ~11.4%, so an all-negative classifier is already ~88.6% accurate. This project evaluates ranking quality with Average Precision and ROC-AUC, then evaluates the actual intervention at an operating threshold.

## Privacy
The raw task-pack files are client data and are gitignored. Do not use a public repository containing them.

Place the supplied files here:

```text
data/raw/train.csv
data/raw/test_unlabelled.csv
data/raw/customers.csv
data/raw/products.csv
data/raw/sample_submission.csv
data/raw/ops-policy.pdf
data/raw/email-thread.txt
data/raw/README.txt
```

## Clean setup

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/audit_data.py
pytest -q
python scripts/evaluate.py
python scripts/train_final.py
python scripts/make_predictions.py
pytest -q
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000`.

### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/audit_data.py
pytest -q
python scripts/evaluate.py
python scripts/train_final.py
python scripts/make_predictions.py
pytest -q
uvicorn app:app --reload
```

## API
`POST /predict` accepts one order JSON in the same pre-dispatch shape as the test file and returns:
- `return_risk_score`
- recommended action
- decision threshold
- employee-readable local reasons
- guardrail against automatic model-only holds

`GET /health` is a smoke-test endpoint.

## Data decisions
- One row per `order_id`; duplicate partner-feed re-imports are checked then collapsed to the crm copy.
- October-2025 order values are detected as 100x scale anomalies and corrected.
- `pickup_scheduled_at` and `last_service_event_type` are excluded from the model because historical values contain post-return/export-day leakage.
- Customer/product reference data are joined only for pre-dispatch attributes.
- `customer_id` itself is not a feature; explicit prior-order/prior-return history is used instead.

## Validation
`scripts/evaluate.py` runs expanding quarterly future validation:
- train before 2025-10 -> validate 2025Q4
- train before 2026-01 -> validate 2026Q1
- train before 2026-04 -> validate 2026Q2

It compares logistic regression with CatBoost and writes `artifacts/evaluation.json`.

## Submission generation
`python scripts/make_predictions.py` refuses to write a file unless:
- row count matches `sample_submission.csv`
- order IDs match in the same order
- IDs are unique
- scores are finite and in [0,1]
- column order is unchanged

## Project notes
- `docs/AUDIT.md` — data issues and initial findings
- `docs/DECISIONS.md` — scope and pushback decisions
- `docs/STATE.md` — current handoff state
- `CLAUDE_PROMPTS.md` — low-token Claude Code workflow
