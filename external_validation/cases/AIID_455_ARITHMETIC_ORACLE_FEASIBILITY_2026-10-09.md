# AIID 455 — independent arithmetic oracle feasibility audit (2026-10-09)

## Why this case
AIID 455 concerns corrected AI-generated CNET financial explainers. Contemporaneous January 2023 reporting identifies a specific compound-interest error in a published article and a subsequent correction. Sources: https://www.vice.com/en/article/cnet-defends-use-of-ai-blogger-after-embarrassing-163-word-correction-humans-make-mistakes-too/ ; https://thedesk.net/2023/01/cnet-artificial-intelligence-ai-article-errors-futurism/ . These are **secondary contemporary reports quoting a correction**, not independently fetched original CNET article versions.

## Independently computable factual oracle
Given initial principal P=10,000, annual interest rate r=0.03, and one year of annual compounding, end balance P(1+r)=10,300 and **interest earned = 300**. Reporting described a claim that the amount earned was 10,300, conflating end balance and interest. This numerical correction is independently computable without trusting either media account's arithmetic.

## Narrow investigation candidate
At an editorial verification decision **before publication** (hypothetical; actual workflow trace not public here), candidate evidence requests might include: (A) recompute interest and balance separately from stated variables; (B) check formula against a reputable reference; (C) request human editorial verification. A and B may share the same mathematical premise; independence requires review. None of these probes is documented as an actual historical action at a dated pre-publication cutoff.

## Explicit gate audit
- **G1** incident/report source: **PROVISIONAL**, because contemporaneous secondary reports document a correction; retrieve original CNET corrected article and ideally archived original to establish exact wording.
- **G2** pre-outcome decision trace: **FAIL/UNAVAILABLE**. Neither model generation trace nor editor's decision-time observation set or publication cutoff is independently evidenced.
- **G3** independent probe truth: **PARTIAL**. Arithmetic for one claim is independently verifiable, but the available source does not establish a fair evidence-selection comparison, counterfactual costs, or full hypothesis ground truth.
- **Quantitative AP-MINIMAX evaluation: NO-GO.** Do not turn a correct math check into a claim that AP-MINIMAX would have selected it or prevented publication.

## What this adds relative to Mythos
Mythos has an observable tool/action trace but no independently confirmed network-boundary truth. AIID 455 offers one independently checkable numerical claim but **no contemporaneous investigator decision trace**. The two cases are complementary incomplete evidence types, not interchangeable evaluation cases. Do not splice them together or claim either passes G3.

## Next testable acquisition
Find an **original dated pre-correction article snapshot** and **original correction notice**, then establish whether any *pre-publication* editorial evidence/probe logs are available. If not, use 455 for factual-verification oracle development only, and pursue a separate instrumented prospective case for evidence-selection comparison. Preserve fixed AIID-50 and synthetic-400.
