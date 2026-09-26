# Kestrel Returns Risk — Claude Code Instructions

Goal: finish the supplied hiring task with the smallest defensible pre-dispatch return-risk system.

## Non-negotiables
- Do not invent data facts, costs, metrics, or model results.
- Raw client data in `data/raw/` is immutable and must not be published.
- Prediction time is immediately before shipment.
- Never use `last_service_event_type` or `pickup_scheduled_at` as model features: in historical training data they are post-order/export-day service fields and leak outcomes.
- De-duplicate training orders by `order_id`, preferring the `crm` row when the same order also appears as `partner_feed`; fail if duplicate rows disagree on anything except `source`.
- Correct the October-2025 payment-gateway scaling issue before using order value.
- Primary validation is chronological, because `test_unlabelled.csv` is the most recent period.
- Do not optimize raw accuracy. Report Average Precision/PR-AUC, ROC-AUC, and operating-point economics.
- Do not auto-hold orders solely from the model. The policy gives enough economics to justify targeted confirmation calls; it does not give enough information to price the 12% hold-cancellation risk.
- No paid runtime API. No RAG, agents, vector DB, LLM inference, or deep learning.
- Do not spawn subagents unless explicitly asked.
- Keep chat responses concise. Use files to persist results.
- Run tests after changes. Never weaken tests to make them pass.
- Do not git push or publish anything unless explicitly told.

## Existing architecture
Do not redesign unless a real failing test or data fact requires it.

1. `src/data.py` — load/validate/dedupe
2. `src/features.py` — leakage-safe pre-dispatch features
3. `src/model.py` — CatBoost model + shared preparation
4. `src/business.py` — call economics and thresholds
5. `src/explain.py` — employee-readable local reasons
6. `scripts/evaluate.py` — expanding temporal backtests + logistic baseline
7. `scripts/train_final.py` — final ensemble artifacts
8. `scripts/make_predictions.py` — exact submission file
9. `app.py` + `static/index.html` — one API endpoint + one screen
10. `tests/` — invariants and privacy/reproducibility checks

## Known audit facts already established
Do not spend tokens rediscovering these unless a script contradicts them:
- train.csv: 11,155 rows, 10,504 unique order_ids.
- 651 duplicate order_ids; each is one `crm` + one `partner_feed` row and otherwise identical.
- Canonical training set: 10,504 orders; 1,200 returns; return rate ~11.42%.
- A trivial all-not-return classifier is ~88.58% accurate, so the client's 95% accuracy target is not a useful operating objective.
- test_unlabelled.csv: 2,096 unique orders, 2026-07-01 through 2026-09-30.
- `pickup_scheduled_at` is non-null for 1,300 raw train rows and zero test rows.
- `last_service_event_type` includes `REVERSE_PICKUP` in train but test only has `NONE`/`INSTALL_BOOKED`; it is leakage/distribution mismatch.
- Every raw October-2025 train row has order_value stored exactly 100x the product/list-price-derived checkout value (748 raw rows; 700 canonical orders).
- Customer and product joins have 100% coverage in supplied files.
- Policy: return cost Rs 1,150; confirmation call Rs 45; call pilot prevented ~35% of returns on called orders; >24h hold causes ~12% customer cancellation; Shield customers are high lifetime value.

## Token discipline
- Prefer running existing scripts over reading entire CSVs.
- Print aggregates, not full data.
- When fixing a bug, inspect only the relevant file/function.
- Do not rewrite working files for style.
- Stop when the requested phase is complete.
