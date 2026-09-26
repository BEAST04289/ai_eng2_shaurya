# Initial Data Audit — Kestrel Returns Risk

This file records the initial audit performed before model implementation.

## Dataset shape
- Raw training rows: **11,155**.
- Unique training `order_id`: **10,504**.
- Duplicate order IDs: **651 groups** / 1,302 duplicate rows.
- Every duplicate group observed is exactly one `crm` row plus one `partner_feed` row and all other fields agree.
- Canonical training set after de-duplication: **10,504 orders**.
- Canonical returns: **1,200**, return prevalence **11.42%**.
- Majority-class / predict-no-return accuracy: **88.58%**.
- Test set: **2,096 unique orders**, from **2026-07-01 to 2026-09-30**.
- Training range: **2025-04-01 to 2026-06-30**.

## Critical leakage
Do not train on:
- `pickup_scheduled_at`: written when reverse pickup is booked after a return is approved. It is non-null for 1,300 raw train rows but zero test rows.
- `last_service_event_type`: train contains outcome-linked `REVERSE_PICKUP`; test contains only `NONE` and `INSTALL_BOOKED`. Historical values are export-day state, not a clean pre-dispatch snapshot.

Using either could produce spectacular validation accuracy while failing on the actual warehouse snapshot.

## Duplicates
Partner-outlet orders are re-imported, producing duplicate `order_id` values. Canonical rule:
1. Verify duplicated rows agree on every field except `source`.
2. Prefer the `crm` row.
3. Fail rather than guess if a future duplicate conflicts.

## October-2025 money bug
The email warned that October festive orders used a new payment gateway. In the supplied data, **all 748 raw October rows** have `order_value_inr` exactly **100x** the checkout value implied by `list_price_inr * qty * (1-discount_pct)`; no other month has this >10x scale anomaly. After de-duplication this affects 700 unique October orders.

Feature logic therefore corrects the scale by ratio, not by date.

## Reference coverage
- Customer join coverage: 100% train and test.
- Product join coverage: 100% train and test.

## Descriptive risk signals (not causal claims)
On the canonical training set:
- Shield: 18.61% return rate vs 9.38% non-Shield.
- COD: 18.81% vs 7.68% prepaid UPI.
- Robot Vacuum: 19.50%; Water Purifier: 14.82%.
- Prior returns are strongly associated with later returns (e.g. 2 prior returns ~40.8%, 3 prior returns ~53.7% in this export).

These are candidate predictive signals, not reasons to penalize a customer or proof of causal drivers.

## Validation design
The hidden file is the most recent quarter, so random K-fold would be optimistic. Use expanding temporal folds:
- train before 2025-10-01 -> validate 2025Q4
- train before 2026-01-01 -> validate 2026Q1
- train before 2026-04-01 -> validate 2026Q2

Keep repeated customers naturally in future folds because production will also score repeat customers; use only explicitly pre-order history fields (`customer_prior_*`) and do not target-encode `customer_id`.

## Initial clean temporal model evidence
A leakage-safe CatBoost candidate and a simple 50/50 logistic+CatBoost ensemble using only pre-dispatch features produced approximately:
- 2025Q4: ROC-AUC **0.761**, Average Precision **0.323**
- 2026Q1: ROC-AUC **0.778**, Average Precision **0.391**
- 2026Q2: ROC-AUC **0.773**, Average Precision **0.402**

The one-hot logistic baseline remained close (latest fold AP ~0.403 / ROC-AUC ~0.776), which is an important complexity check. CatBoost is only worth keeping if the clean local rerun preserves a small average benefit or better operational ranking; do not claim it is dramatically better.

## Decision framing
The 95% accuracy promise is not the right objective: with only ~11.4% returns, doing nothing already gives ~88.6% accuracy.

Policy economics make targeted confirmation calls measurable:
- Return cost: Rs 1,150.
- Call cost: Rs 45.
- Pilot prevented about 35% of returns that would otherwise occur on called orders.
- Break-even return risk for a call = `45 / (1150 * 0.35)` = **~11.18%**.

By contrast, holding >24h leads to ~12% customer cancellation, but the pack does not state the economic value of a cancellation/lost margin. Therefore automatic holds cannot be priced defensibly from the supplied data.
