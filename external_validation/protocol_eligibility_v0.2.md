# External case eligibility protocol v0.2 — three independent gates

Applies to the fixed 50-case AIID screening draw from the official 2026-10-05 export. **Do not re-draw or substitute cases after inspecting outcomes.** Maintain a row for every sampled case including exclusions.

## Gate 1 — incident validity
PASS only if at least one traceable original/primary report substantiates the event and identity of the incident; log URLs, dates, report IDs and discrepancies. FAIL if source cannot substantiate an AI-related event or record conflates multiple unrelated incidents. Otherwise UNDETERMINED.

## Gate 2 — investigation suitability
PASS only if an explicit pre-outcome decision time can be defined; at least two plausible competing explanations can be stated without hindsight; at least two discriminating evidence checks are available or defensibly reconstructable; information available at the cutoff is separated from later reporting. FAIL if the event has no meaningful investigation decision point. Otherwise UNDETERMINED. Analyst-generated hypotheses must be labelled as reconstructions, not historical facts.

## Gate 3 — evaluation feasibility
PASS only if independent probe outcomes and source-grounded costs/constraints or explicitly justified standardized proxies exist; comparison methods receive identical pre-cutoff information; reference answers are established independently of AP-MINIMAX output; and hindsight leakage checks pass. FAIL if the event cannot support a valid comparison even after reasonable source review. Otherwise UNDETERMINED. A Gate 2 PASS with Gate 3 FAIL may still support a qualitative case study, **not** a quantitative performance claim.

## Review order and adjudication
Prioritize the 15 initial priority cases for source checking, but assess all 50 with the same rubric. Keep priority labels separate from eligibility labels. Record reviewer, date, primary report references, cutoff, reasons, missing evidence, and any conflict. Use HOLD/UNDETERMINED until evidence is inspected. Never silently convert UNKNOWN to PASS or equate reported outcome with prospective probe availability.

## Leakage safeguards
1. Freeze the decision-time cutoff before constructing the candidate set.
2. Build the investigator-facing packet using only material demonstrably available by that cutoff.
3. Keep post-outcome descriptions and outcome keys in a separate restricted record.
4. Blind method comparison and score only pre-specified eligible instances.
5. Report excluded cases and sensitivity to reconstruction assumptions; no claims of incident-population representativeness from equal-year quotas.

## Current state
All 50 have Gate 1=PENDING_PRIMARY_SOURCE, Gate 2=UNDETERMINED, Gate 3=UNDETERMINED, decision=HOLD. This is an explicit evidence-based **NO-GO for quantitative external evaluation**, not a negative result about AP-MINIMAX. A 50-row local eligibility register has been generated separately; the source data and frozen synthetic holdout were not modified.
