# v0.1 claim boundary

## Evidence identity

This boundary applies only to frozen commit `f7c68a51ea4ccc1f58b3c0ac7d1079e0977c3ea9` and the preserved HOLDOUT trace with SHA256 `3c6818f6cbde34d007227b1ddccdb83b6fb4637571f4f0e0353e668093afa6bd`.

The HOLDOUT was executed once during the audit. The code is deterministically seeded by inspection, but byte-for-byte repeatability was not tested by a second HOLDOUT execution. The frozen pytest command did not run because pytest was unavailable, and the repository contains no committed tests. These limitations remain part of the result.

## Supported

Within the declared v0.1 synthetic diagnostic model, the evidence supports the following statements:

1. **Observed frozen execution.** One complete DEV execution and one complete HOLDOUT execution ran at the exact local/`origin/main` commit. The preserved HOLDOUT contains 800 cases, five strategies, and 6,321 trace records.
2. **Ambiguity-preserving execution.** The four sequential strategies selected no cause while more than one explanation remained compatible. Persistent-ambiguity cases remained unresolved rather than becoming causal conclusions.
3. **Compatibility preservation.** For all 10,142 checked before/after states where the hidden truth was represented in the candidate model, the truth remained compatible. Every observed outcome in those cases was generated from the represented truth's singleton prediction.
4. **Warranted resolution.** AP minimax, information gain, neutral discriminating, and neutral all each produced 600 warranted/correct resolutions, 100 unresolved outcomes, and 100 model gaps. Resolution occurred only with exactly one independently compatible explanation.
5. **Observed premature closure.** The sequential strategies had zero premature closures. The deliberately forced-closure ablation made 600 premature selections from non-singleton compatible sets. Its selected causes were still compatible; they were unsupported as unique conclusions, not contradicted by the evidence.
6. **Comparative frozen-strategy results.** AP used 849 observations at total cost 1,498. Information gain used 811 at cost 1,485; neutral discriminating used 1,059 at cost 2,127; neutral all used 1,602 at cost 3,249. These are paired descriptive results for this fixed synthetic case mixture, not population estimates.
7. **AP versus information gain.** AP and information gain had identical terminal and safety outcomes on all 800 cases. Information gain used 38 fewer observations and 13 lower total cost. v0.1 therefore does not support superiority of AP over information gain.
8. **Tested invariances.** In implementation-level metamorphic checks, explanation renaming, explanation-order reversal, and probe-order reversal produced no substantive result changes across 4,000 case-strategy runs per transformation. Candidate-list presentation order did change under explanation reversal, without changing candidate membership or decisions.
9. **Tested leakage properties.** Static dataflow inspection found no hidden-truth access in the strategy or investigator modules. All selected trace actions were independently reproducible from current evidence, compatible explanations, available probes, cost, and neutral rank. Changing hidden-truth ID/family metadata did not alter decisions in the recorded metamorphic checks.

## Substantive claim that remains interesting

The nontrivial v0.1 result is not general superiority. It is a mechanism result:

> In a noiseless, deterministic compatibility model with explicit unresolved and model-gap states, ambiguity-preserving sequential policies can avoid unsupported causal closure and use evidence more efficiently than neutral-order policies; however, the particular AP minimax objective offers no demonstrated advantage over the frozen information-gain policy and is slightly less efficient on this HOLDOUT.

This motivates a new experiment about objective tradeoffs when AP and information gain actually choose different probes. It does not justify tuning v0.1 or reusing its HOLDOUT.

## Not established

The frozen evidence does **not** establish:

- real-world incident cause or incident-response superiority;
- production performance, reliability, safety, or operational utility;
- superiority or inferiority relative to human investigators;
- general causal-inference or diagnostic-reasoning superiority;
- superiority of AP minimax over information gain;
- robustness to noisy, unreliable, missing, delayed, deceptive, or contradictory observations;
- robustness when a represented truth makes non-singleton or probabilistic predictions;
- calibrated probabilistic inference or handling of observation reliability;
- robustness to distribution shift beyond the five frozen generator seeds;
- empirical repeatability of the HOLDOUT output across environments;
- inferential population claims from the designed stratum proportions;
- broader theoretical, proprietary, or ArcTopia claims;
- validation of any post-v0.1 implementation or future v0.2 design.

## Interpretation constraints

- Overall percentages depend directly on the constructed 400/100/100/100/100 stratum mixture and must be accompanied by stratum results.
- The generator makes all probe predictions singleton-valued and all represented-truth observations noiseless. Clean cases are singleton-resolved initially, model-gap cases have zero candidates initially, and persistent-ambiguity cases contain indistinguishable survivors by construction.
- The forced-closure ablation is a safety-negative control, not a competitive evidence-selection baseline.
- The invariance checks call the frozen runner and are implementation self-tests. They support absence of the tested sensitivities but do not independently prove that the runner is scientifically correct.
- Hidden truth may be used after a run to score correctness and to test preservation; it must not be used to choose actions. The review found no such action-selection use.
