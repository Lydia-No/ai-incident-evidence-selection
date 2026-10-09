# AP-MINIMAX prospective instrumented validation — preregistration draft v0.1

**2026-10-09 | Status: DESIGN ONLY, NOT RUN.** Separate from frozen 400 synthetic cases and fixed AIID-50 external feasibility sample. This document does not claim external empirical validation.

## Target estimand
Among investigator episodes with >=2 initially plausible causal explanations and a fixed set of authorized evidence requests, compare the **probability that the first selected request separates the true explanation from its strongest alternative**, under a common observation budget, for AP-MINIMAX vs predeclared baselines. Report also total cost to justified resolution and unsupported-closure rate. A task with no independent truth or counterfactual probe oracle is ineligible for primary scoring and remains in the screening denominator.

## Instrumented prospective design
A separate **case author** constructs 12–20 controlled, benign incident-investigation episodes from actual logged software or model-evaluation runs with documented perturbations, without malware, credentials, or third-party targets. For each episode the author preserves: (1) original logs and source hashes, (2) a decision-time snapshot, (3) >=2 genuinely competing hypotheses, (4) >=3 permissible evidence requests, (5) pre-recorded probe results for *all* requests, (6) cost/latency, (7) independently checked truth key. Cases may be generated in a controlled testbed, but must be described as **instrumented controlled cases**, not naturally occurring external incidents.

## Independence and blinding
- **Author** records truth and full counterfactual probe table before selector sees the case.
- **Independent adjudicator** checks hypothesis exclusivity, oracle evidence and authorization; disputes are logged before unlocking selectors.
- **Selector runner** receives only snapshot + request labels/descriptions/cost estimates. The true hypothesis and full probe outcomes remain sealed.
- **Analyst** predeclares scoring and exclusions before seeing outcomes. Log any role overlap and any previous exposure; if the same person fills all roles, label as *self-audited pilot*, not independent validation.
- Seal key with SHA-256 of canonical JSON; retain original immutable version and record any revisions separately. A hash alone is not a secret or proof of independence.

## Baselines and controls
B0: uniform random among authorized requests (fixed seeds). B1: lowest-cost request. B2: fixed deterministic order, decided before seeing cases. B3: simple information-gain selector with identical priors and observation model where available. AP-MINIMAX must be run from a frozen code commit and configuration. Missing observation models must not be guessed to advantage one method; mark B3 ineligible for those episodes, retain B0–B2. Record ties, abstentions, and invalid requests explicitly.

## Primary and secondary endpoints
Primary: **first-probe discriminatory success** (predeclared oracle: resulting observation excludes at least one initially viable alternative while retaining true hypothesis, using a fixed compatibility function). Secondary: evidence cost to resolution, unsupported closures, abstention, remaining compatible hypotheses, and worst-case performance across cases. A cheap probe that returns no information is not a success. If the truth key is nonidentifiable, mark NOT_SCORABLE rather than forcing a result.

## Analysis plan
Use paired episode-level differences (AP-MINIMAX minus each baseline), bootstrap intervals by *case* rather than by repeated seeds, and exact success/failure counts. Report denominators, non-scorable cases, ties, and any method-specific eligibility exclusions. A pilot with 12–20 episodes is for feasibility, not a powered superiority claim. Do not retroactively change metrics or choose favorable seeds.

## Gate / stop rules
G1: source logs and hashes; G2: pre-outcome snapshot and no leakage; G3: independently adjudicated truth and complete authorized probe outcome table. **Any G3 failure => excluded from primary metric but retained in eligibility register**. Stop if the experiment cannot produce a complete probe table without fabricated counterfactuals, if sensitive data appears, or if the method sees the truth key. Predefine case generation and rejection before observing method choices.

## First executable milestone
Build **one benign, instrumented case** with three hypotheses, three read-only probes, and an independently checkable truth key, then verify the complete packet with a schema validator and leakage check. Only after this dry run freeze the case-generation protocol and collect more cases. This milestone is not yet completed.

## Nonclaims
Neither Mythos cutoff-100 nor AIID 455 supplies both a verified pre-decision snapshot and a complete counterfactual probe oracle. Neither should be scored as an AP-MINIMAX win. Existing synthetic 400-case results remain distinct from this prospective design.
