# Decision-time packet feasibility: hard-stop review (2026-10-09)

**Scope:** AIID 1442, 1629, 1707 from the fixed 50-case screening sample. This record does **not** contain a blinded replay or newly retrieved logs. It is an evidence-availability and design decision. Retrospective incident descriptions are not admissible as pre-cutoff investigator observations.

| AIID | Proposed decision time (hypothesis only) | Critical pre-cutoff evidence needed | Independent probe-result evidence | Decision |
|---|---|---|---|---|
| 1442 | Before the disputed AWS Cost Explorer change | timestamped actor/action log, permissions, agent/human tool context, source chronology | none established | HOLD; causation disputed |
| 1629 | Before the research agent first contacted a non-allowlisted live target | full redacted timestamped model/tool transcript, target allowlist, instructions, what model knew | none established | HOLD; best *trace acquisition* candidate |
| 1707 | Before the reported first denied portal request | time-stamped request/response trace, authorization policy, endpoint state, agent observations | none established | HOLD; authorization vs access mechanism separate |

## Non-negotiable hard stops

- A post-incident report cannot be silently presented as information available at the cutoff.
- Analyst-invented hypotheses are not the historical investigator's hypotheses.
- A reported event outcome is not a measured outcome of an unperformed counterfactual probe.
- No method-specific tuning, probe-cost fitting, or post-hoc case replacement on the fixed 50.
- If an actual timestamped trace cannot be sourced, record **TRACE_UNAVAILABLE** and retain the case in denominator. Do not manufacture a pseudo-replay and call it external validation.

## Next feasible study unit
A **source-bounded, non-scored qualitative case study** is defensible with existing public reports. A **quantitative prospective-style replay** requires independent decision-time packet + held-out evidence key. If no cases meet this bar, report feasibility failure and redirect to a *separately labeled* public trace dataset (not a replacement of the AIID 50) with a preregistered transfer protocol.

## Priority
First request/locate redacted time-ordered tool transcripts and evaluation configuration for **AIID 1629**. Then audit official incident chronology and logs for **1707**; treat **1442** as disputed causal attribution. All three remain **NO-GO for scoring**.

## Provenance
Official AIID Excel export dated 2026-10-05; previously committed source audits and three-case feasibility matrix. No new source-level facts asserted here. Existing 400-case synthetic holdout unchanged.
