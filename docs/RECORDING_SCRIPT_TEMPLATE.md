# <=3 minute recording outline

## 0:00-0:25 — business decision
Show the single-order screen.
Say the result first: model ranks return risk, but the operational action is a confirmation call rather than an automatic hold because call economics are measurable and hold-cancellation economics are incomplete.

## 0:25-0:55 — what I found / changed
Show `docs/AUDIT.md`.
Mention: 651 duplicate order IDs, October values 100x, post-outcome reverse-pickup/service leakage, ~11.4% returns so 95% raw accuracy is the wrong target.

## 0:55-1:35 — evidence
Show `artifacts/evaluation.json` or concise terminal output.
Compare majority/logistic/CatBoost. Show temporal folds and the chosen metric. Mention one known failure mode.

## 1:35-2:10 — prompt / AI usage
Show `CLAUDE.md` and one short Claude prompt. Explain that AI was constrained to run/fix the prepared scaffold rather than design an oversized system.

## 2:10-2:40 — what I threw away
Show `docs/DECISIONS.md`.
Mention: leaked service/pickup features, blind 95% accuracy optimization, automatic hold, paid/LLM runtime, unnecessary architecture.

## 2:40-2:55 — close
Show `predictions.csv`, README start commands, and the app response with reasons.
