# Frozen Experiment Protocol v0.1

**Status:** FROZEN v0.1 before clean implementation results. Any change to cases, baselines, selector, metrics, controls, seeds, or analysis after implementation begins requires a new protocol version.

## Primary hypotheses

**H1 — ambiguity preservation:** On incident cases with genuinely confusable causal explanations, the investigator will produce fewer unsupported/premature causal closures than a forced-closure ablation given the same evidence, compatibility logic and probe set.

**H2 — useful next checks:** While ambiguity remains, its minimax-selected probes will produce greater *realized* reduction in the surviving explanation set per unit probe cost than seeded neutral probe selection on the frozen synthetic cases. Comparison with information-gain selection is descriptive/prior-art calibration, not a required superiority claim.

**H3 — operationalization:** For each unresolved state, the artifact can emit a concrete check with observable outcomes and outcome-conditioned predictions about which explanations survive. This is evaluated as a Track 2 usability property, not as a claim of a novel general diagnosis algorithm.

## Null / failure interpretation

The claim fails if any apparent advantage disappears under fair baselines, neutral naming/order, non-anticipation controls, independent scoring, or clean negative controls.

## Experimental units

Synthetic incident cases generated from frozen rules with hidden ground truth and staged evidence reveal.

## Required causal families

At minimum include confusable failure families covering:

- retrieval/evidence acquisition
- tool/action execution
- system/state context
- control/policy context

## Baselines and prior-art reference

- **Forced-closure ablation:** identical evidence, compatibility logic and available probes, but when multiple explanations survive it collapses to one using the same seeded neutral tie-rank and discards the others. This is explicitly an ablation of ambiguity preservation, not a state-of-the-art comparator.
- **Neutral probe baseline:** seeded neutral selection from the same available probe set; this is the primary comparator for H2.
- **Classical active-diagnosis reference:** where the synthetic case provides the probabilities required to compute it cleanly, include an information-gain / entropy-reduction selector as a reference comparator.
- Any additional baseline must be frozen before headline results are inspected.

**Important interpretation:** beating the information-gain reference is **not** required for the sprint contribution. If the clean selector agrees with or is outperformed by established active-diagnosis methods under complete probabilistic models, report that plainly. The intended contribution is operationalization for AI incident investigation, not invention of active diagnosis.

## Primary outcomes

- **Premature-closure rate:** fraction of decisions that select a cause while more than one explanation remains compatible with the evidence actually revealed at that step.
- **Valid-resolution rate:** fraction of resolved decisions where the selected cause is both the hidden ground truth and uniquely warranted under the revealed evidence/model.
- **True-explanation retention:** fraction of pre-resolution steps in which the hidden true explanation remains in the candidate set unless contradicted by revealed evidence.
- **Realized probe value:** reduction in the compatible candidate set after the probe outcome is revealed, divided by frozen probe cost. This is computed independently from raw traces and is not identical to the selector's internal score.
- **Observations/cost to valid resolution.**
- **MODEL_GAP detection rate:** cases with no compatible modeled explanation should surface model inadequacy rather than force attribution.

## Required controls

- Clean resolvable cases where early evidence genuinely warrants one explanation
- Persistent-ambiguity cases where no available evidence uniquely resolves the cause
- Model-gap cases where the true cause is intentionally absent from the candidate set
- No-contradiction / no-failure cases
- Distinct benign-history negative controls
- Renaming permutations
- Input-order permutations
- Seed stability where stochasticity exists
- No-future-leakage tests
- Holdout generator seeds not inspected while tuning implementation tests

## Anti-tautology requirement

The experiment must not define success as "the algorithm chose the probe that its own scoring function calls best." Selector score and headline probe-value metric must be separable. Case generation, hidden truth and realized outcomes are fixed independently of the strategy under test.

## Falsification tests

Actively attempt to explain any advantage by:

- weak baseline design
- marker/string leakage
- duplicated controls
- scoring circularity
- ordering/tie artifacts
- future-information leakage
- dataset construction effects
- implementation-specific shortcuts

## Analysis rule

Raw traces are written first. Headline metrics are recomputed independently from raw traces. Implementation-side summaries are not authoritative.

## Change control

After first frozen run, changes to cases, metrics, scoring, baselines, or controls require a new version and must be labeled post-result/exploratory.
