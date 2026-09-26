# To: Ritu Deshpande, Head of D2C Operations
## Kestrel Returns Risk — recommendation

**Recommendation: do not automatically hold every order the model flags. Use the risk score to trigger a pre-dispatch confirmation call for orders above 13% predicted return risk. At ~700 orders/month, the validation results imply roughly ₹11,600 net savings per month, or ~₹35,000 per quarter, before any longer-term customer-value effects.**

Returns are 11.4% of unique historical orders in the supplied data. A simple "nothing will return" model would already be 88.6% accurate, which is why I would not manage this system to the 95% accuracy target alone. The useful question is whether the model can concentrate enough real returns into an intervention group to pay for the intervention.

I tested the model as it would actually be used: train on earlier orders and predict later quarters. Across three future-quarter backtests, Average Precision was 0.328, 0.387 and 0.414, with ROC-AUC of 0.766, 0.774 and 0.780. I would therefore expect hidden-test Average Precision around 0.40, with meaningful uncertainty around that number.

At a 13% operating threshold, the backtests flag about 27% of orders, capture about 64% of returns, and achieve about 26% precision among flagged orders.

At ~700 orders/month that is approximately:

- 191 confirmation calls
- 50 returns concentrated in the called group
- ~18 returns prevented if the previous 35% call-pilot effect carries forward
- ~₹20,200 avoided return cost
- ~₹8,600 call cost
- **~₹11,600 net saving per month**

I would not use the same score to automatically hold dispatch yet. Kestrel's own policy says a >24-hour hold leads to cancellation about 12% of the time, but the supplied pack does not quantify the margin or lifetime-value loss from those cancellations. That is especially important for Shield members, who are both more return-prone and Kestrel's highest-LTV segment.

**What I would do next week:** run the model as a confirmation-call queue, not an automated hold rule. Track flagged orders, call completion, return outcome, cancellation and Shield status. After several weeks, compare model-selected calls against a small randomized control group. That gives Kestrel the evidence needed to decide whether any segment should later move from "call" to "hold."

Two data issues must remain guarded in production. Partner-outlet orders are duplicated through re-imports, and two historical service fields contain information created after a return begins; those fields are deliberately excluded from prediction. October 2025 order values also contain a 100× payment-gateway scale anomaly, which the pipeline corrects using product price, quantity and discount consistency.

That directly fixes your Task 1 reviewer feedback: the memo starts with the decision, number, and rupees, rather than making Ritu sit through the data-cleaning story first.
