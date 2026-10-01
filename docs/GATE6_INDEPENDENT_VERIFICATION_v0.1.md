# Gate 6 — Independent Verification v0.1

Status: **PASS within the frozen synthetic evaluation scope.**

This document records a post-holdout verification of the first complete v0.1 run. It does not alter generator semantics, strategy definitions, holdout seeds, metrics, or interpretation thresholds.

## Provenance

- Frozen execution plan commit: `9919c13c0fb07db3aec708e134632e2388b09d5c`
- Pre-holdout code head: `3b9bd80d3b4e7adab08efcfda081a966c2e9e0c2`
- Holdout workflow-only commit: `c092164d4368d75687e21d2ecd5a63a9e144ac7e`
- Marker-only holdout commit: `f874168a91b447cdf704ad3cbe2868d5643b6ae1`
- GitHub Actions run: `34664446883`
- Artifact ID: `10287944357`
- Artifact name: `sprint2-frozen-holdout-v0.1-f874168a91b447cdf704ad3cbe2868d5643b6ae1`
- Artifact ZIP SHA-256: `7d8ee3eca6dbb9891c941c5ee48c29a8045a063c35836b2c41bd903f9860c38f`
- Raw JSONL SHA-256: `3c6818f6cbde34d007227b1ddccdb83b6fb4637571f4f0e0353e668093afa6bd`
- Analysis JSON SHA-256: `053f8c7d9d840aa80ec659eedbb13284d2c6fb7f18568ae4122fa31f8b5b1692`

The downloaded artifact ZIP digest matches the digest reported by GitHub. The raw and analysis file hashes match the provenance manifest embedded in the artifact.

## Raw-data conformance checks

Independent inspection of the raw JSONL found:

- 6,321 trace rows.
- 800 distinct cases.
- exactly 160 cases for each of the five frozen holdout seeds.
- per seed: 80 confusable-resolvable, 20 clean-resolvable, 20 persistent-ambiguity, 20 model-gap, and 20 no-failure controls.
- within each seed, confusable cases are exactly balanced across retrieval, tool, state, and control hidden-truth families: 20 each.
- no duplicate `(case_id, strategy, step)` records.
- no step-sequence gaps.
- recorded candidate counts equal the lengths of recorded candidate-ID sets.
- no candidate-count increases after evidence reveal.
- no repeated selected probe within a case/strategy trajectory.
- no missing realized outcome for a selected probe.
- no non-positive selected-probe costs.
- cumulative observation and cost fields are monotonic.

No raw-trace integrity violation was found in these checks.

## Independent headline recomputation

Headline metrics were recomputed directly from raw JSONL rather than accepted from `analysis_v0.1.json`.

### H1 — ambiguity preservation

On the 400 confusable-resolvable cases:

- AP-MINIMAX unsupported premature closures: **0 / 400**; premature-closure rate **0.000**.
- FORCED-CLOSURE unsupported premature closures: **400 / 400**; premature-closure rate **1.000**.

This is a mechanism sanity check only. FORCED-CLOSURE is an ablation, not a state-of-the-art comparator.

### H2 — primary next-check value

First-check realized value is `(candidate_count_before - candidate_count_after_actual_outcome) / probe_cost`.

AP-MINIMAX versus NEUTRAL-ALL:

- mean paired difference: **+0.5195833333**
- frozen 10,000-replicate paired-bootstrap 95% interval: **[+0.4383333333, +0.5991666667]**
- seed directions: **5 / 5 positive**
- wins / ties / losses: **235 / 129 / 36**

AP-MINIMAX versus NEUTRAL-DISCRIMINATING:

- mean paired difference: **+0.42125**
- frozen paired-bootstrap 95% interval: **[+0.3458333333, +0.4954166667]**
- seed directions: **5 / 5 positive**
- wins / ties / losses: **217 / 145 / 38**

These independently recomputed values exactly match the frozen analysis artifact. Under the pre-registered rule, **H2 = PASS**.

### Prior-art calibration — descriptive only

On the same first-check endpoint:

- AP-MINIMAX mean: **1.4516666667**
- INFORMATION-GAIN mean: **1.4058333333**
- paired AP minus INFORMATION-GAIN mean: **+0.0458333333**
- paired-bootstrap 95% interval: **[+0.0225, +0.0708333333]**
- wins / ties / losses: **24 / 371 / 5**

This comparison was not required for PASS and should not be presented as the principal novelty claim. The high tie count is consistent with substantial behavioral overlap between the frozen minimax selector and a standard information-gain reference.

## Control behavior

For AP-MINIMAX:

- model-gap detection on model-gap controls: **100%**
- unresolved behavior on persistent-ambiguity controls: **100%**
- valid resolution on clean-resolvable controls: **100%**
- valid resolution on no-failure controls: **100%**
- true-explanation retention over all eligible recorded steps: **100%**
- all 400 confusable-resolvable cases eventually resolved to the hidden true explanation.

NEUTRAL-ALL, NEUTRAL-DISCRIMINATING, and INFORMATION-GAIN also eventually resolved all 400 confusable-resolvable cases correctly. Therefore the supported synthetic advantage is **evidence-selection value / efficiency and avoidance of unsupported closure**, not superior eventual correctness on these deliberately resolvable cases.

## Adversarial interpretation check

The v0.1 result supports a bounded statement:

> Under the frozen controlled synthetic conditions, explicit ambiguity preservation plus the frozen AP-MINIMAX next-check rule avoided unsupported causal closure and selected higher realized-value first checks than both neutral and neutral-discriminating baselines under equal available information and frozen probe costs.

It does **not** establish:

- real-world incident attribution accuracy;
- production DFIR performance;
- autonomous incident-response safety;
- superiority over expert investigators;
- a new general active-diagnosis or information-theoretic algorithm;
- facts about the Hugging Face / OpenAI incident;
- generalization outside the frozen synthetic generator.

Important interpretation constraints:

1. The synthetic generator intentionally creates confusable but diagnosable cases with heterogeneous probe quality. This is appropriate for mechanism testing but is not a real-world incident distribution.
2. The AP-MINIMAX objective is related to, but not identical with, the realized-value endpoint. The stronger NEUTRAL-DISCRIMINATING comparison reduces the risk that the result is merely an artifact of avoiding completely useless probes.
3. INFORMATION-GAIN is behaviorally very close on most cases. The contribution should remain framed as an auditable operational protocol for AI-incident investigation, not as invention of active diagnosis.
4. Real-incident application must be presented as a mapping of unresolved questions and executable checks, not as validation that synthetic performance transfers to the July incident.

## Gate decision

**Gate 6: PASS within reviewed scope.**

**Gate 7 empirical decision: PASS for the frozen synthetic v0.1 claim.**

The next step is incident mapping and submission construction. The frozen holdout result must remain preserved unchanged; any new experiment is a separately versioned extension rather than a repair of v0.1.
