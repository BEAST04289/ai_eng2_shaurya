# Decisions

## D1 — Push back on "95% accuracy"
Status: decided.

Return prevalence is ~11.4%, making accuracy a weak objective for a risk-ranking workflow. Use Average Precision/PR-AUC as the primary model-quality metric, ROC-AUC as a secondary ranking metric, and business utility at an operating threshold for the action. Three expanding temporal backtests put the empirical net-savings optimum at 0.12, 0.13 and 0.13; use **0.13** as the submitted operating threshold while retaining 11.18% as the theoretical call break-even risk.

## D2 — No automatic hold from the model
Status: decided.

The requested action is `flag and hold`, but policy says holds >24h lead to ~12% cancellations and does not supply lost-margin/LTV cost of those cancellations. Shield customers are explicitly high-LTV. We can price confirmation calls, not blanket holds. Recommendation: high-risk -> pre-dispatch confirmation call; use model as decision support, not autonomous hold.

## D3 — Remove service/pickup fields
Status: decided.

`last_service_event_type` and `pickup_scheduled_at` are historical export-day/post-return fields and materially leak the target. Test is a true dispatch snapshot, so the distributions do not match. Both are excluded.

## D4 — Canonicalize partner duplicates
Status: decided.

One row per `order_id`; verify duplicate content and prefer `crm` over `partner_feed` when duplicates are identical except source.

## D5 — Correct October payment scale
Status: decided.

Use product list price, quantity and checkout discount to identify 100x scale rows and divide those stored values by 100. Do not hard-code the month as a feature correction rule.

## D6 — Temporal validation
Status: decided.

Use expanding quarterly backtests because the hidden test is the most recent quarter. Do not random-split the headline evaluation.

## D7 — Model ladder
Status: decided.

1. majority baseline
2. logistic regression
3. CatBoost candidate and a simple 50/50 logistic+CatBoost ensemble

Keep CatBoost only if it gives a reproducible benefit or materially better operational ranking. No LLM inference, RAG, deep learning or paid APIs.
