# Low-token Claude Code prompts

Use a fresh Claude Code context for each phase if credits/context are tight. `CLAUDE.md` + `docs/STATE.md` carry the state.

## Prompt 1 — verify only
Paste exactly:

```text
Read CLAUDE.md and docs/STATE.md only. Do not redesign or rewrite working files.
Run:
python scripts/audit_data.py
pytest -q
python scripts/evaluate.py

If something fails, inspect only the relevant traceback/file and make the smallest correct fix. Do not add features or new files.
Then update docs/STATE.md with the exact test count and the three temporal-fold logistic/CatBoost AP+AUC results from artifacts/evaluation.json.
Do not train the final model yet. Stop.
Chat reply <=120 words.
```

## Prompt 2 — final model + predictions
After reviewing `artifacts/evaluation.json`, paste:

```text
Read CLAUDE.md, docs/STATE.md, and artifacts/evaluation.json.
Do not change feature policy, leakage exclusions, duplicate logic, or business framing unless a test proves a bug.
Run:
python scripts/train_final.py
python scripts/make_predictions.py
pytest -q

Validate predictions.csv against sample_submission.csv: same rows/order/columns, unique order_id, finite score in [0,1], no index.
Report only: model artifact path, prediction row count, score min/mean/max, pytest result, and any real issue. Stop.
```

## Prompt 3 — service smoke test
Paste:

```text
Read CLAUDE.md and docs/STATE.md.
Run the FastAPI service and test:
GET /health
POST /predict using one real test_unlabelled row converted to JSON
GET /

Check that /predict returns score + 3 readable reasons + recommended action, and that the screen calls the endpoint.
Fix only actual runtime errors. Do not redesign UI.
Update README only if startup instructions are wrong. Stop.
Reply <=120 words.
```

## Prompt 4 — final docs, no coding
Paste only after metrics/business numbers are approved:

```text
Read CLAUDE.md, docs/DECISIONS.md, docs/STATE.md, artifacts/evaluation.json, docs/RITU_MEMO_TEMPLATE.md and submission-form.md.
Update the memo and submission form using only verified numbers. Lead memo with decision + number + rupees. Use one consistent phrase for every evaluation claim. Do not invent hidden-test results.
Keep memo <=1 page of normal reading. Do not change code. Stop.
```
