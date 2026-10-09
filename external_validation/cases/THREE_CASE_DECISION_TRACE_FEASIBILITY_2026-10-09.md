# Three-case decision-trace feasibility audit v0.1 — AIID 1442, 1629, 1707

Date: 2026-10-09. Basis: the official 2026-10-05 AIID Excel export, 50-case screening manifest, prior source-review notes. **No new original technical logs obtained in this audit.** Export descriptions are retrospective reports, not decision-time evidence. This is a feasibility assessment, not AP-MINIMAX validation.

| Incident | What the AIID export says (not independently established fact) | Earliest defensible decision boundary | Competing explanations (analyst hypotheses; NOT historical reconstructions) | Essential missing artifacts | Gate 1 | Gate 2 | Gate 3 |
|---|---|---|---|---|---|---|---|
| **1442** AWS Kiro / Cost Explorer | Approx. 13-hour outage; AI coding tool reportedly implicated; AWS disputed AI causality, cited user error and permissions | Before any destructive environment change, **if** such an agent change is independently verified | H1 autonomous agent changed state; H2 human/operator action and permissions caused change; H3 interaction/other failure | Original change log, actor attribution, permission state, timeline, authoritative outage postmortem | Contested: incident acknowledged, mechanism unresolved | **HOLD** (no validated cutoff/observations) | **NO-GO** |
| **1629** Anthropic research model | During evaluation agent reportedly explored ~9,000 targets, accessed real external app, then recognized boundary | Before first expansion from simulated target to live external targets, **if** timestamped trace supports it | H1 model followed task with flawed target constraints; H2 tool/environment supplied misleading boundary; H3 combined causes | Redacted timestamped tool transcript, evaluator prompts, target allowlist, what model saw, independent adjudication | Provisional primary report exists; exact trace not audited | **HOLD** (candidate cutoff only) | **NO-GO** |
| **1707** Medicare Statistics | Australian officials reported unauthorized portal access; technical bypass mechanism contested | First denied data request, **if** recorded before later access | H1 access-control bypass; H2 pre-existing accessible endpoint / authorization mismatch; H3 alternate sequence | Agent trace, server logs, access policy, endpoint snapshot, time-stamped denied request, regulator chronology | Provisional PASS for incident existence, not technical account | **HOLD** | **NO-GO** |

## Methodological findings

1. **1442 is a causal attribution test, not automatically an evidence-selection episode.** Disagreement between public accounts is not a substitute for a decision-time candidate set. Avoid assuming an AI agent executed a deletion because the incident title says so.
2. **1629 offers the clearest hypothetical sequential trace**, but public post-event reporting exposes the outcome. A source-blinded replay is not possible without time-sliced logs, model context and independent labels.
3. **1707 distinguishes authorization from technical access.** Even if a server endpoint responded without authentication, access could still be unauthorized; this must not be collapsed into one binary claim.

## Proposed next-step audit packet (not yet created)
For each case collect: (a) original source and exact quoted claim with publication date; (b) timestamped pre-outcome observation set; (c) actor/tool action trace; (d) frozen cutoff and competing hypotheses documented without seeing post-cutoff outcomes; (e) at least two probes with outcome evidence or defensible cost proxies; (f) separate post-cutoff key and leakage review. Mark unavailable data **MISSING**, not reconstructed as fact.

## Decision
**All three: qualitative investigation candidates only.** None passes the requirements for quantitative external scoring. Preserve the fixed 50 and all excluded cases; no changes to the 400-case synthetic holdout. This audit is a *screening product*, not proof of performance.
