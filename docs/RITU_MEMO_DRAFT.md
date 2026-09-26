# To: Ritu Deshpande, Head of D2C Operations
## Subject: Use return-risk scoring to target confirmation calls, not automatic holds

**At ~700 orders a month, I would call roughly the highest-risk 27% before dispatch. On three future-period backtests, that policy would have been worth about Rs 11.7k net per month after call costs, if the spring pilot's 35% prevention effect carries over. I would not automatically hold flagged orders yet.**

The model ranks each order by return risk before dispatch. A 0.13 operating threshold was stable across three expanding quarterly backtests: the empirical best threshold was 0.12, 0.13 and 0.13. Across those future-period predictions, the selected cohort contained 456 of 717 returns: 63.6% recall at 26.3% precision. At 700 orders/month that translates to about 191 calls, about 50 eventual returns concentrated in that cohort, and about 18 returns prevented if the pilot effect generalizes. Return-cost avoided is then about Rs 20.3k/month against about Rs 8.6k of call cost, for about Rs 11.7k net/month.

I changed one part of the original ask. I would use the score to trigger a confirmation call rather than automatically hold the order. Kestrel can price the call: Rs 45, versus Rs 1,150 for a return, and the pilot prevented about 35% of returns on called orders. That makes a call break even at roughly 11.2% predicted risk. But the policy also says a >24-hour hold causes about 12% customer cancellation and does not give the lost-margin or lifetime-value cost of that cancellation. Shield customers are also Kestrel's highest-LTV segment. Automatic holds therefore have an unpriced downside.

The model was validated only on future periods, not random rows. A simple logistic model and CatBoost were close individually, so I use a 50/50 average because it improved both Average Precision and ROC-AUC in all three temporal folds. Ensemble Average Precision was 0.328, 0.387 and 0.414; ROC-AUC was 0.766, 0.774 and 0.780. The latest-quarter result is the closest analogue to the hidden July-September period.

Two historical fields were deliberately excluded even though they make prediction look easier: reverse-pickup timing and latest service event. They are populated after the return process starts in historical data and do not exist in the same form at dispatch. The October payment-gateway value error and partner-feed duplicate orders are also corrected before training.

**Next week:** run the 0.13 threshold as a controlled confirmation-call pilot, retain a nearby untreated comparison band, measure actual prevented returns/cancellations, and price the lost-margin/LTV cost of a dispatch hold before enabling any automated hold rule.
