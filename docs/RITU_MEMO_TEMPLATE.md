# To: Ritu Deshpande, Head of D2C Operations
## Subject: Returns risk — recommended operating decision

**Decision / number / rupees first:** [Fill after final backtest: e.g. "Call the top X% highest-risk orders before dispatch; validation suggests Y avoided returns / Rs Z net per month at ~700 orders."]

### What I recommend next week
Use the risk score to route higher-risk orders to a pre-dispatch confirmation call. Do **not** automatically hold every flagged order yet.

Why: Kestrel's policy prices a return at Rs 1,150 and a confirmation call at Rs 45, and the pilot says calls prevented ~35% of returns that would otherwise have occurred. That makes a call economically attractive above roughly 11.2% return risk. By contrast, a >24h hold causes about 12% customer cancellation, but the pack does not state the margin/LTV loss from those cancellations, so an automatic-hold threshold cannot be priced honestly.

### What the model can and cannot do
[Insert final temporal backtest AP/AUC, precision/recall at action threshold, and one plain-language failure case.]

The model excludes two tempting historical fields—reverse-pickup/service status—because they are populated after the customer starts returning the order and would leak the outcome.

### Guardrail
Shield members have both higher observed return rates and the highest lifetime value segment. The score can trigger a confirmation call, but should not become an automatic penalty or hold for Shield customers without a separate retention/cancellation analysis.

### Next-week plan
1. Call the risk-selected cohort for one week.
2. Record whether the customer confirms/corrects/cancels and whether the order later returns.
3. Compare return rate and net cost with an untreated control band.
4. Price lost-margin/LTV from holds before enabling automated dispatch holds.
