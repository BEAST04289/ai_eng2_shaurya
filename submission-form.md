# Kestrel Home — Submission Form Draft

## Github Repo URL
https://github.com/BEAST04289/ai_eng2_shaurya

## What did you build, and what business decision does it support? State the number and the rupees.
I built a pre-dispatch return-risk system that scores each order, explains the main risk signals in employee-readable language, and exposes the result through a local FastAPI endpoint plus browser screen.

I would not use the score for automatic holds yet. I would use it to trigger a pre-dispatch confirmation call above a 0.13 risk threshold.

In temporal backtests that threshold flagged about 27.3% of orders, with 26.3% precision and 63.6% recall. At ~700 orders/month, that is about 191 calls/month. Using Kestrel's ₹45 call cost, ₹1,150 return cost and the policy's 35% observed call-pilot effect, the estimated net value is about ₹11.6k/month, ~₹35k/quarter or ~₹140k/year, assuming the pilot effect generalizes.

## What score do you expect predictions.csv to get on the hidden outcomes, on which metric, and why that metric? Say how you estimated it.
Expected hidden Average Precision: approximately 0.40.

I use Average Precision as the primary predictive metric because only about 11.4% of canonical historical orders were returned, so raw accuracy does not describe how well the model identifies the minority return class. Precision/recall metrics are more informative for this type of imbalanced prediction problem.

The estimate comes from three expanding temporal backtests that mimic the supplied hidden-test setup:

- 2025 Q4: AP 0.328, ROC-AUC 0.766
- 2026 Q1: AP 0.387, ROC-AUC 0.774
- 2026 Q2: AP 0.414, ROC-AUC 0.780

The most recent quarter is closest to the hidden Jul-Sep 2026 period, but I would treat ~0.40 as an estimate rather than a guaranteed score.

## How do you know it works? How you validated, on what split, error rate, and the kind of case it gets wrong.
I used expanding chronological validation rather than a random split because test_unlabelled.csv contains the most recent orders.

The three validation periods were:
- train through Sep 2025 -> validate Q4 2025
- train through Dec 2025 -> validate Q1 2026
- train through Mar 2026 -> validate Q2 2026

The final 50/50 CatBoost + logistic-regression ensemble produced AP of 0.328 / 0.387 / 0.414 and ROC-AUC of 0.766 / 0.774 / 0.780 across those folds.

At the selected 0.13 operational threshold across the temporal validation predictions, precision was ~26.3% and recall ~63.6%. So the model still misses roughly 36% of returns and most flagged orders do not ultimately return. It is therefore a prioritization tool, not a deterministic return detector.

Likely failure cases include behavior changes after the training period, new products/customer cohorts, and individual returns driven by causes not observable before dispatch.

## Did you change, narrow, or push back on the client's ask? What, when, and why.
Yes.

Ritu requested 95%+ accuracy and automatic dispatch holds for flagged orders. I kept the pre-dispatch risk-scoring goal but changed both the evaluation criterion and the first intervention.

First, I do not optimize raw accuracy. With an 11.4% return rate, predicting "not returned" for every order already gives 88.6% accuracy while identifying zero returns. I therefore report Average Precision, ROC-AUC and threshold-level precision/recall.

Second, I recommend confirmation calls rather than automatic holds. Kestrel has a quantified ₹45 call cost and an observed pilot showing calls prevented about 35% of returns. By contrast, the policy says >24-hour holds cause about 12% cancellation but gives no margin/LTV cost for those cancellations. That makes automatic holds economically under-specified, especially for high-LTV Shield customers.

## What is wrong with what you are handing us, or with the data we handed you?
The model is useful but not strong enough to treat its predictions as facts. At the chosen threshold precision is only ~26%, so roughly three quarters of flagged orders will not return. Recall is ~64%, so it still misses roughly one third of returns.

The ₹11.6k/month business estimate assumes the historical 35% confirmation-call pilot effect generalizes to model-selected orders. That has not yet been proven experimentally.

The hidden-test AP estimate is based on three historical future-quarter backtests; real Jul-Sep 2026 behavior may drift.

Some historical fields are unusable at dispatch because they contain post-return information. I exclude them, but this also means historical records are richer than the live dispatch snapshot.

The service is a local prototype, not a production deployment with authentication, monitoring, a feature store or warehouse integration.

## What does one prediction cost, and what would a month cost at Kestrel's volume (about 700 orders a month)?
Paid model/API cost per prediction: ₹0.

The submitted runtime uses local CatBoost + scikit-learn models and makes no paid model/API calls.

700 orders/month × ₹0 = ₹0/month paid inference cost.

This excludes ordinary machine/hosting compute. If the recommended confirmation-call intervention is used, calls are a separate business-operating cost: approximately 191 calls/month × ₹45 ≈ ₹8,600/month at the selected threshold.

## What did you deliberately leave out, and why that rather than something else?
I deliberately left out LLM-based scoring, RAG, deep learning, paid inference APIs, multi-agent workflows, automatic retraining, SHAP dashboards and an elaborate frontend.

The core problem is structured tabular prediction with a small set of categorical/numeric variables. Logistic regression and CatBoost were sufficient to establish a defensible baseline and temporal validation result.

Given the scope, I prioritized leakage prevention, reproducibility, temporal validation, decision economics, exact submission generation and a working endpoint/screen over additional architecture.

## Anything you built or found that nobody asked for?
Yes.

I found 651 duplicate order IDs caused by partner-feed re-imports and canonicalized them before modelling.

I found that `pickup_scheduled_at` and historical service-event values contain post-outcome information and would create severe leakage. They are excluded.

I found that October 2025 order values are systematically stored at 100× their expected scale, consistent with the email warning about the new payment gateway. The pipeline detects and corrects this using product price, quantity and discount consistency.

I also translated the policy costs into an operational threshold and found that the economically supported action is a confirmation call rather than an automatic hold.

## What did you use AI for?
I used ChatGPT for task decomposition, adversarial review, business/evaluation framing, implementation scaffolding and checking for leakage/privacy risks.

I used Claude Code locally as an execution/debugging assistant: reproducing the audit, running temporal evaluation, training the final model, validating predictions.csv, running tests and smoke-testing the FastAPI service.

I deliberately constrained Claude Code to short phase-specific prompts because broad autonomous exploration was unnecessary and would waste both time and model usage.

AI suggestions that added unnecessary complexity were not used. The submitted runtime itself uses no LLM or paid AI API.

## Someone picks this up on Monday and you are unreachable. The three things they need to know.
1. The prediction moment is pre-dispatch. Never add `pickup_scheduled_at` or post-return service events to the model; they leak the outcome.
2. Keep the deduplication and October-2025 value correction in the preprocessing path. Raw partner-feed duplicates and the payment-gateway scale anomaly materially distort the data if used untreated.
3. The 0.13 threshold currently means "send to confirmation call," not "hold order." Re-estimate the threshold if intervention costs/effectiveness change, and do not introduce automatic holds until cancellation/LTV economics are measured.
