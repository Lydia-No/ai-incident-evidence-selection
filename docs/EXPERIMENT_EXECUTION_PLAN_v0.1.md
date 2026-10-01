# Gate 5 — Frozen Experiment Execution Plan v0.1

Status: **FROZEN BEFORE HEADLINE CASE GENERATION OR RESULT INSPECTION.**

This document operationalizes `EXPERIMENT_PROTOCOL_v0.1.md`. It does not change the hypotheses or success metrics. Any post-result change to case counts, holdout seeds, generator constraints, strategy definitions, primary endpoints, or decision thresholds requires a new version and preservation of the original outputs.

## 1. Experimental unit and causal families

Each synthetic case is a staged incident-investigation problem with hidden ground truth, candidate explanations, observed evidence, available probes, probe costs, and a pre-generated actual outcome for each probe. Strategies never receive hidden ground truth or unrevealed outcomes.

The four failure families are:
- retrieval / evidence acquisition
- tool / action execution
- system / state context
- control / policy context

Synthetic identifiers are semantically neutral and are assigned only after structural case generation.

## 2. Development versus holdout

Development seed: `26091200`.

The development suite contains 40 cases, eight per stratum, and may be inspected only for implementation/generator correctness. Development results are never headline results.

Frozen holdout seeds:
- `26091301`
- `26091302`
- `26091303`
- `26091304`
- `26091305`

Each holdout seed generates exactly 160 cases:
- 80 confusable-resolvable cases
- 20 clean-resolvable controls
- 20 persistent-ambiguity controls
- 20 model-gap controls
- 20 no-failure / no-contradiction controls

Total frozen holdout: 800 cases. The primary H2 population is the 400 confusable-resolvable cases. Within each holdout seed, the 80 confusable cases are balanced evenly across the four hidden true failure families (20 each).

Holdout outputs must not be inspected until the generator, strategies, trace writer, metric code, and their tests are committed and CI-green on the Gate 5 branch.

## 3. Structural case rules

### Confusable-resolvable
- Four candidate explanations are modeled.
- Initial evidence leaves either four candidates or exactly three candidates; the split is balanced 40/40 within each holdout seed.
- If initial evidence removes one candidate, it may not remove the hidden true explanation.
- Five available probes are generated.
- Probe predictions are deterministic partitions of the surviving explanation set into two or three possible outcomes.
- Probe costs are in `{1.0, 2.0, 3.0}` and are generated independently of partition quality.
- The full probe signature across the available probe set must uniquely distinguish every modeled explanation that can remain after initial evidence.
- At least two probes must be discriminating at the initial unresolved state.
- At least two different initial partition qualities must be present, so probe choice is not vacuous.
- Exactly half of confusable cases include at least one nondiscriminating probe; the stronger neutral-discriminating comparator below prevents this from making the primary interpretation trivial.

### Clean-resolvable
Initial evidence uniquely warrants one modeled explanation before any new probe. The artifact must resolve without requesting unnecessary evidence.

### Persistent ambiguity
At least two surviving explanations have identical signatures across all available probes. No strategy may legitimately resolve between them from the frozen evidence model. The correct artifact behavior is explicit `UNRESOLVED` when no discriminating probe remains.

### Model gap
The hidden true cause is intentionally absent from the modeled candidate set. Frozen observed evidence is constructed so that no modeled explanation remains compatible. Correct behavior is `MODEL_GAP`, never forced attribution.

### No-failure / no-contradiction
`NO_FAILURE` is represented as the true candidate alongside failure explanations. Evidence remains compatible with the no-failure explanation and must not manufacture a failure cause. Cases are generated so that the available evidence can either preserve or validly resolve to `NO_FAILURE` according to the same compatibility rules.

## 4. Neutrality and anti-leakage

Case structure is generated before human-readable explanation/probe labels are assigned.

Each probe receives a neutral tie rank from a separate RNG stream derived from the case seed and immutable structural probe slot. The tie rank is generated before probe names and before input ordering. It therefore cannot depend on semantic names, lexical order, or strategy output.

Renaming and input-order perturbations are generated after the structural case is fixed and are used as invariance tests, not as additional headline cases.

Actual probe outcomes are pre-generated from hidden truth before any strategy runs. Strategy choice cannot affect the outcome table.

## 5. Frozen strategies

### AP-MINIMAX
The Gate 4 ambiguity-preserving investigator. While unresolved, choose the probe with minimum worst-case residual candidate count, then lower frozen cost, then frozen neutral tie rank.

### FORCED-CLOSURE
An ablation of ambiguity preservation, not a state-of-the-art comparator. Given the identical initial evidence and candidate set, if more than one explanation survives it selects one immediately using a seeded neutral explanation rank and discards the others. This is used for H1/mechanism validation only.

### NEUTRAL-ALL
Primary protocol-defined neutral baseline for H2. At each unresolved state, choose the lowest frozen neutral probe rank among all currently available unobserved probes. It receives exactly the same evidence and probe set as AP-MINIMAX.

### NEUTRAL-DISCRIMINATING
Stronger robustness comparator frozen before results. Choose the lowest neutral rank among probes that are discriminating under the current surviving candidate set. If none is discriminating, stop unresolved. This comparator is included specifically to show whether an advantage over NEUTRAL-ALL is merely due to avoiding useless probes.

### INFORMATION-GAIN
Descriptive prior-art calibration. Candidate explanations receive a uniform prior over the currently surviving set. Because synthetic probe predictions are deterministic, each probe induces an outcome partition; choose the probe with maximum expected entropy reduction, breaking ties by lower cost then neutral tie rank. Superiority over this reference is not required for the sprint contribution.

## 6. Frozen execution

For initial-step H2 evaluation, each strategy is evaluated from the exact same initial unresolved state and the same pre-generated actual outcome table. This keeps the primary next-check comparison paired and avoids trajectory divergence as a confound.

Sequential secondary runs continue until one of:
- `RESOLVED`
- `MODEL_GAP`
- no discriminating/available probe remains
- all five probes have been consumed

A strategy never receives evidence generated by another strategy's path.

## 7. Primary and secondary endpoints

### H1 — ambiguity preservation
Mechanism/ablation endpoint: premature-closure rate at states where more than one explanation remains compatible. This is a behavioral sanity check and is not presented as evidence of algorithmic novelty.

### H2 — next-check value
Primary endpoint on confusable-resolvable holdout cases:

`first_check_realized_value = (candidate_count_before - candidate_count_after_actual_outcome) / probe_cost`

Comparison is paired case-by-case between AP-MINIMAX and NEUTRAL-ALL.

Robustness comparison uses the same paired endpoint against NEUTRAL-DISCRIMINATING.

INFORMATION-GAIN is reported descriptively on the same cases.

### Secondary trajectory endpoints
- observations to valid resolution
- total probe cost to valid resolution
- valid-resolution rate
- true-explanation retention before resolution
- terminal unresolved rate
- `MODEL_GAP` detection rate
- no-failure preservation / valid-resolution behavior

The unit of inference is the case, not the individual step.

## 8. Frozen H2 interpretation rule

Analysis bootstrap seed: `26091399`.

Use 10,000 paired case-level bootstrap resamples over the 400 confusable holdout cases for the aggregate mean difference in first-check realized value. Also report the mean paired difference separately for each of the five holdout seeds and report win/tie/loss counts.

H2 **PASS** only if:
1. the aggregate AP-MINIMAX minus NEUTRAL-ALL mean difference is positive and its 95% paired-bootstrap interval excludes zero;
2. the direction is positive in at least four of five holdout seeds; and
3. the aggregate mean difference versus NEUTRAL-DISCRIMINATING is also positive with a 95% interval excluding zero.

H2 **PARTIAL** if AP-MINIMAX clearly outperforms NEUTRAL-ALL but the stronger NEUTRAL-DISCRIMINATING condition is not met, or if the aggregate point estimate is positive but uncertainty includes zero.

H2 **FAIL** if the aggregate effect versus NEUTRAL-ALL is non-positive or the effect is not stable enough to support the bounded claim.

No benchmark redesign is permitted to rescue a PARTIAL or FAIL result under v0.1.

## 9. Raw trace contract

Write JSONL before any aggregate summary. Every strategy-step record must include at minimum:
- experiment version
- generator version
- holdout/development seed
- case id and stratum
- strategy
- step index
- candidate count and candidate ids before the action
- observed evidence ids available before the action
- selected structural probe slot/id or terminal action
- frozen probe cost and neutral rank
- partition sizes visible to the strategy
- actual revealed outcome
- candidate ids/count after reveal
- resulting investigation state
- cumulative observations and cost

Hidden truth may be logged by the runner only after strategy output for the step has been produced; it must never be passed into strategy selection.

Aggregate implementation-side summaries are non-authoritative. Gate 6 independently recomputes all headline metrics from raw JSONL.

## 10. Generator and analysis tests required before holdout

- exact stratum counts per seed
- exact confusable family balance
- confusable cases satisfy unique full signatures and minimum probe-quality constraints
- persistent-ambiguity cases are genuinely non-identifiable
- model-gap cases contain no compatible modeled explanation under their frozen gap evidence
- clean-resolvable cases have exactly one compatible explanation initially
- no-failure controls preserve the true no-failure explanation unless evidence validly resolves it
- costs and neutral ranks are independent of names/input order
- explanation/probe renaming invariance
- input-order invariance
- hidden truth is absent from all strategy function arguments
- actual outcomes are fixed before strategy selection
- raw trace can be independently replayed to reproduce candidate transitions
- metric recomputation from raw traces matches only after independent calculation, not by reusing selector scores

## 11. Change control

Before first holdout run: implementation bugs may be fixed only to conform code to this frozen plan and Gate 1/2; the plan itself does not move silently.

After any holdout output is generated: preserve it. Any change to generator semantics, counts, seeds, baseline definitions, primary metric, bootstrap rule, or PASS/PARTIAL/FAIL thresholds requires a new explicitly versioned plan. A documented code bug that makes a run non-conforming may be corrected and rerun, but the invalid run and the correction must remain in provenance.

The headline result is the first complete run that demonstrably conforms to this frozen v0.1 plan.
