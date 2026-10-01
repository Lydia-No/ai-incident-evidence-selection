# Behavioral Specification v0.1

**Status:** FROZEN v0.1 for clean implementation. Any mechanism change after implementation begins requires a new specification version.

## Purpose

Define the minimum behavior of an ambiguity-preserving incident investigator without reference to the exploratory implementation.

## Core contract

Given a set of candidate explanations, currently observed evidence, and available probes, the investigator must:

1. Preserve every explanation still compatible with observed evidence.
2. Eliminate an explanation only when observed evidence makes it incompatible.
3. Never use unrevealed/future evidence when deciding the current state or next probe.
4. Evaluate probes only against currently surviving explanations.
5. Rank available probes using the frozen minimax discrimination rule below; the rule and tie-breaking must not be tuned to the clean-run outcome.
6. Recompute compatibility after each revealed observation.
7. Resolve only when the frozen resolution criterion is satisfied.
8. Produce a trace sufficient to reconstruct why each explanation survived or was eliminated and why each probe was chosen.

## Frozen probe-selection rule

For the current surviving explanation set **H** and each available probe **p**:

1. Each explanation specifies the outcomes it considers compatible for **p**.
2. For every outcome possible under at least one surviving explanation, compute the surviving subset that would remain if that outcome were observed.
3. Define the probe's **worst-case residual ambiguity** as the largest such surviving subset.
4. Choose the probe with the smallest worst-case residual ambiguity.
5. If tied, choose lower frozen probe cost.
6. If still tied, use a seeded neutral tie-rank independent of explanation/probe names and input ordering.

This rule is deliberately non-probabilistic: it does not require calibrated priors or outcome probabilities. It is a bounded operational choice, not a claim of a new optimal active-diagnosis algorithm.

## Resolution semantics

- **RESOLVED:** exactly one explanation remains compatible and the frozen resolution criterion is met.
- **UNRESOLVED:** more than one explanation remains compatible; do not select a cause merely because one is more convenient or salient.
- **MODEL_GAP:** no candidate explanation remains compatible with observed evidence; surface model inadequacy rather than forcing attribution.
- If multiple explanations survive and no available probe can distinguish them, remain **UNRESOLVED** and expose the evidence gap.

## Operational probe contract

Every proposed next check must be renderable as an incident-response request with:

- the question/check to perform;
- the evidence source or system/organization that could answer it;
- observable outcomes;
- which surviving explanations each outcome would eliminate or preserve;
- cost/availability metadata when relevant;
- the condition under which the check would resolve the current ambiguity.

This is the bridge to Track 2's requirement for resolvable questions, checks somebody could run tomorrow, and causal explanations that predict something.

## Prior-art / novelty boundary

Maintaining multiple hypotheses and selecting informative tests is established in active diagnosis, sequential diagnosis, active hypothesis testing, and Bayesian experimental design. This sprint does **not** claim to invent that general idea or information-gain probe selection.

The contribution under test is narrower: an auditable, ambiguity-preserving incident-investigation protocol for autonomous-AI incidents that keeps unresolvedness explicit, operates over heterogeneous staged evidence, turns surviving causal explanations into concrete evidence requests, and preserves a reconstructable trace suitable for cross-organizational incident review.

## Required invariants

- **Renaming invariance:** arbitrary explanation labels cannot change substantive behavior.
- **Ordering invariance:** input order cannot change substantive behavior except through an explicitly seeded neutral tie-break.
- **Non-anticipation:** future observations cannot affect present decisions.
- **Dynamic consistency:** new observations trigger fresh compatibility evaluation rather than pass-through state.
- **Traceability:** every state transition is reconstructable from recorded inputs and rules.

## Explicit non-goals

- Autonomous cyber attribution
- Production DFIR performance
- General AI reasoning
- ArcTopia architecture
- Containment prevention
- Claiming facts about the July incident

## Freeze test

This specification is acceptable only if an independent implementer could build a compatible system without seeing old sprint code.
