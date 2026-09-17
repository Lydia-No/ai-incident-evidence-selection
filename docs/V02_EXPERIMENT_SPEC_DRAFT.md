# v0.2 experiment specification — draft, not implemented or frozen

Status: **FORWARD-LOOKING DRAFT — SPECIFICATION ONLY**

This document is not part of the v0.1 empirical evidence. It has not been implemented or tested. It specifies a possible future experiment and does not modify v0.1, authorize implementation, freeze scientific inputs, generate a HOLDOUT, or authorize execution.

## 1. Research boundary

v0.1 showed that AP minimax and information gain had identical terminal/safety outcomes in a noiseless deterministic generator, while information gain used 38 fewer observations and 13 lower total cost. Structural review found only 79/800 cases where their first choices differed, always at a four-candidate `2+2` versus `2+1+1` partition conflict.

v0.2 will isolate evidence-selection objective conflicts. It will **not** attempt to make AP win and will not reuse v0.1 HOLDOUT cases or seeds as confirmatory evidence.

## 2. Primary research question

When minimax residual ambiguity and expected information gain prefer different probes, how do the frozen-style objectives trade off:

1. mean observations,
2. cumulative evidence cost, and
3. tail/worst-case residual burden,

while preserving the same warranted-resolution safety rules?

The target is a conditional mechanism claim inside a synthetic deterministic diagnostic model. No real-world or production claim is in scope.

## 3. Competing hypotheses

These hypotheses are symmetric; no policy is designated the expected winner.

- **H0 — no material policy distinction:** conditional on objective-conflict cases, AP minimax and information gain have no meaningful paired difference in cumulative cost, observation count, or tail burden.
- **H1-mean — information-gain advantage:** information gain reduces mean observations or mean cumulative cost by accepting a less balanced worst-case partition.
- **H1-tail — minimax advantage:** AP reduces upper-tail observations/cost or maximum post-probe survivor count at the expense of mean efficiency.
- **H1-tradeoff — neither dominates:** one policy improves mean efficiency while the other improves tail risk or cost under specified cost regimes.
- **H1-null-safety failure:** either policy produces unsupported resolution, removes a represented truth, or otherwise violates a safety invariant. This is a failure finding, not a performance win.

## 4. Why v0.2 remains noiseless

Noisy, unreliable, contradictory, missing, or time-varying evidence will **not** be introduced in this minimum experiment.

Reason: v0.1 defines hard deterministic compatibility, not probabilistic observation likelihoods, confidence updates, repeat-observation semantics, or reliability-aware stopping. Adding noise now would change both the selection problem and the inference engine, preventing attribution of any difference to the AP-versus-information-gain objective. A reliability study should be separately specified after v0.2 isolates objective tradeoffs.

Asymmetric probe costs are retained because v0.1 already has costs and the policy definitions use them. Costs will be controlled rather than randomly confounded with partition type.

## 5. Experimental unit and paired design

The experimental unit is one sealed synthetic case evaluated once by each frozen v0.2 strategy.

Strategies receive the same public case definition, initial evidence, probe metadata, and realized reveal sequence for a given case. Results are paired by `case_id`. Hidden truth and unrealized outcomes are unavailable to action selection and available only to the post-run scorer.

The scientific unit for uncertainty summaries is the case, not an individual trace step or strategy-case record.

## 6. Candidate and observation model

- Each case has 4 or 6 candidate explanations, depending on stratum.
- Every candidate declares one deterministic outcome for every available probe.
- Exactly one truth is represented in resolvable and persistent-ambiguity controls.
- Model-gap controls have no compatible represented truth.
- Revealed outcomes equal the sealed truth prediction; there is no observation noise in v0.2.
- Candidate IDs, probe IDs, input order, and neutral ranks are generated independently of hidden truth, family, partition role, and expected policy performance.
- Hidden truth is balanced across candidate positions within each seed and stratum.
- Full case definitions, including all unrealized outcomes, are sealed from strategies.

## 7. Strata

### 7.1 Primary stratum A — risk/information conflict

- Six initially compatible candidates.
- At least one AP-preferred probe induces `3+3` (worst residual 3; entropy gain 1 bit).
- At least one information-gain-preferred probe induces `4+1+1` (worst residual 4; entropy gain approximately 1.252 bits).
- Probe costs are equal for the two primary probes, so the disagreement is caused by the primary objectives rather than cost or neutral rank.
- Remaining probes permit eventual singleton resolution for every candidate.
- Truth positions are exactly balanced across the six outcome cells.

This stratum tests mean-versus-tail ambiguity directly.

### 7.2 Primary stratum B — cost/information conflict

- Four initially compatible candidates.
- A lower-cost probe induces `2+2`.
- A higher-information probe induces `2+1+1`.
- Both have worst residual 2, so AP selects by cost while information gain selects by entropy.
- Two preregistered cost regimes are used:
  - modest information premium: costs `1.0` versus `1.25`;
  - high information premium: costs `1.0` versus `2.0`.
- Remaining probes permit eventual singleton resolution.
- Truth positions are exactly balanced across all four candidates.

This stratum tests whether an extra chance of immediate resolution repays its initial evidence cost.

### 7.3 Control stratum C — objective concordance

- Four or six candidates.
- AP and information gain have the same uniquely preferred probe before tie-breaking.
- Cases are otherwise matched to the primary strata on candidate count, number of probes, downstream resolvability, and cost range.

This detects unintended implementation differences when objectives should agree.

### 7.4 Control stratum D — persistent ambiguity

- At least two represented candidates have identical signatures across all probes.
- Both policies must terminate unresolved after exhausting discriminatory opportunity.

This is a safety/stopping control, not an efficiency comparison.

### 7.5 Control stratum E — model gap

- Initial or revealed evidence is incompatible with every modeled explanation.
- Every sequential strategy must report `MODEL_GAP` and select no cause.

This is a model-adequacy control.

No clean-at-initial-singleton stratum is needed: v0.1 already established that trivial branch, and it cannot distinguish evidence-selection objectives.

## 8. Generator constraints

The generator must reject and regenerate a case unless all applicable constraints hold:

1. primary-stratum objective conflict is independently verified before outcomes are generated;
2. intended partitions and costs are exact;
3. resolvable cases have unique full probe signatures;
4. persistent-ambiguity cases retain at least two identical full signatures;
5. model-gap cases have zero compatible explanations at the specified gap point;
6. no candidate/probe string, order, or neutral rank encodes truth or partition role;
7. all probe IDs are unique and all costs positive;
8. truth/cell assignments are balanced within seed and stratum;
9. downstream probe networks are generated without conditioning on which strategy will win a final metric;
10. case acceptance uses structural constraints only, never observed strategy performance.

Generator rejection counts and reasons must be logged. Rejection sampling may not inspect aggregate results.

## 9. Strategies

All strategy definitions and tie-breaking rules must be executable, unit-tested, and frozen before HOLDOUT generation.

1. **AP minimax:** among discriminating probes, minimize worst-case compatible survivor count; then minimize cost; then use neutral rank.
2. **Information gain:** maximize expected entropy reduction under a uniform distribution over currently compatible candidates; then minimize cost; then use neutral rank.
3. **Cost-first discriminating control:** among discriminating probes, minimize cost; then use neutral rank.
4. **Neutral-discriminating control:** among discriminating probes, select lowest neutral rank.

Forced closure is excluded from the primary v0.2 comparison because v0.1 already established it as an unsafe negative control and it does not test evidence selection. If retained for regression purposes, it must be labeled an ablation and excluded from superiority claims.

No strategy may access hidden truth, realized unrevealed outcomes, generator rejection history, other strategies' actions, or post-run score fields.

## 10. Common stopping and terminal rules

- `RESOLVED`: exactly one compatible explanation remains.
- `MODEL_GAP`: zero compatible explanations remain.
- `UNRESOLVED`: more than one explanation remains and no available probe can discriminate among them.
- A probe may be selected at most once.
- No maximum-step truncation may silently create a terminal conclusion. A safety cap may stop execution only as `UNRESOLVED_CAP`, reported separately and treated as a protocol/design failure if reached.
- Forced causal selection from a non-singleton set is prohibited for all primary strategies.

## 11. Endpoints

### 11.1 Safety gate

Before performance comparisons, report by strategy and stratum:

- unsupported or premature closure rate;
- represented-truth elimination rate;
- incorrect singleton resolution rate;
- model-gap detection rate;
- unresolved-control preservation rate;
- protocol/cap failure rate.

No strategy may be called superior if it has any safety-gate failure not shared by its comparator. Safety is not traded against efficiency in a composite score.

### 11.2 Co-primary performance endpoints

Reported separately, never collapsed into a post-hoc composite:

1. paired difference in cumulative evidence cost to terminal state, AP minus information gain;
2. paired difference in number of selected probes to terminal state, AP minus information gain.

Both are reported separately for stratum A and each stratum B cost regime. A policy dominates only if it is no worse on the safety gate and better on both co-primary endpoints under the preregistered uncertainty criterion. Otherwise the result is a tradeoff or no distinction.

### 11.3 Secondary endpoints

- 90th and 95th percentile cumulative cost and probe count;
- maximum cumulative cost and probe count;
- first-step realized survivor count;
- probability of immediate singleton resolution;
- fraction of cases where AP and information gain choose different first probes;
- terminal-state distribution;
- results of each control strategy;
- by-seed estimates and between-seed dispersion.

No metric may be added to the confirmatory analysis after unsealing.

## 12. Cost metric

Evidence cost is the sum of preregistered probe costs actually selected. Costs are abstract synthetic units and carry no real-world monetary or time interpretation.

Report both cost and probe count. Do not use a weighted cost-plus-error utility unless a separate utility function is justified and frozen before HOLDOUT generation.

## 13. Sample-size rationale

The design uses balanced paired cases rather than an unpaired power calculation.

Proposed HOLDOUT allocation:

- Stratum A risk/information conflict: 360 cases (60 per hidden-truth position).
- Stratum B modest premium: 240 cases (60 per hidden-truth position).
- Stratum B high premium: 240 cases (60 per hidden-truth position).
- Concordance control: 120 cases.
- Persistent ambiguity control: 120 cases.
- Model-gap control: 120 cases.
- **Total: 1,200 cases per strategy.**

Generate these across six independent sealed seeds, with equal stratum contribution per seed. This gives exact truth-position balance in primary strata, supports paired distributions rather than only means, and provides 240–360 primary cases per preregistered regime without expanding into a broad noise/model-mismatch factorial.

Before freezing, a blinded design simulation may verify that the proposed counts produce stable interval widths for the endpoints. It may not use v0.1 HOLDOUT outcomes to tune v0.2 effect expectations or select favorable strata.

## 14. DEV protocol

- Use public DEV seeds disjoint from every v0.1 and v0.2 HOLDOUT seed.
- DEV cases are for schema validation, invariant tests, runner debugging, and confirming that each intended conflict/concordance condition is reachable.
- DEV results may not be used to change primary endpoints, choose a favorable cost regime, remove a strategy, or alter HOLDOUT stratum weights.
- Any change to generator constraints, strategy semantics, stopping, scoring, endpoints, or analysis after DEV requires a new specification version and a fresh HOLDOUT seed commitment.
- Preserve failed DEV attempts as engineering evidence; do not present them as confirmatory results.

## 15. HOLDOUT generation and sealing

1. Obtain independent review approval of this specification.
2. Freeze and hash the generator, strategies, runner, scorer, schemas, tests, environment lock, and analysis program.
3. Record a protocol-lock manifest containing commit SHA and SHA256 for every scientific input.
4. An independent custodian generates six cryptographically random seeds not used by v0.1 or DEV.
5. Before case generation, publish or escrow a commitment `SHA256(canonical_seed_file)` without revealing seeds.
6. Generate the full case manifest once. Store seeds, hidden truths, and unrevealed outcomes outside the strategy-access boundary.
7. Record the encrypted case-manifest hash, case counts, rejection counts, and generator log hash.
8. Verify exact stratum/truth balance and structural constraints without running strategies.
9. Seal the HOLDOUT read-only. No regeneration, filtering, substitution, or selective rerun is allowed after any result is observed.
10. Execute each strategy once per case under the frozen runner. Preserve complete raw traces before summary generation.

If any frozen scientific input differs from the protocol-lock manifest, the run is invalid and no scientific result may be claimed.

## 16. Preregistered analysis

- Analyze every generated case and every strategy.
- Recompute all metrics independently from raw traces.
- Report case counts, exclusions (expected: zero), protocol failures, and missing records.
- Present safety endpoints first.
- Present paired AP-minus-information-gain differences with two-sided 95% bootstrap confidence intervals resampled by case within seed and stratum; use a fixed, preregistered bootstrap seed and replicate count.
- Also report exact paired sign counts (`AP lower`, `equal`, `AP higher`) and by-seed effects.
- Report strata separately. An overall result may be shown only as a prespecified allocation-weighted descriptive summary and may not replace stratum results.
- Adjust the two co-primary endpoint confidence decisions using Holm correction within each primary regime, or make no binary significance claim and report intervals descriptively. This choice must be frozen before HOLDOUT generation.
- Report information gain outperforming AP fully if observed; do not redefine success around a favorable tail or cost result.
- Do not infer real-world, human, production, general causal, or theoretical superiority.

## 17. Required invariants and leakage protections

The frozen test suite must verify:

- compatibility recomputation after every reveal;
- candidate changes only from newly revealed evidence;
- selected probe was available and is never reused;
- cumulative cost equals selected-probe costs;
- candidate counts equal candidate IDs;
- terminal state matches compatible-set cardinality;
- unresolved/cap states have no selected cause;
- hidden truth remains compatible in every represented-truth noiseless case;
- action-selection call graphs contain no hidden-truth or unrevealed-outcome input;
- renaming and input ordering do not change substantive decisions;
- neutral ranks are unique and independent of truth/partition role;
- objective-conflict/concordance constraints hold before execution;
- trace/scorer fields cannot pass hidden truth into actions;
- raw trace coverage is exactly cases × strategies, with variable trace length accounted for.

Tests must use both static inspection and independent trace recomputation. Metamorphic tests that call the runner must be labeled implementation self-tests, not independent evidence.

## 18. Falsification and invalidation criteria

The following outcomes falsify or sharply narrow the intended claim:

- AP and information gain do not choose different first probes in at least 95% of primary conflict cases: generator/protocol failure, not a null scientific result.
- A primary strategy makes any unsupported causal selection: safety failure.
- Represented truth is eliminated in the noiseless model: implementation/model failure.
- Results change under semantic renaming or ordering: validity failure.
- A neutral/cost control matches or dominates both named policies: no evidence that the named objective adds value under that regime.
- AP improves only a tail endpoint while worsening both co-primary means, or information gain improves only means while materially worsening the preregistered tail: report a tradeoff, not superiority.
- Effects reverse materially across sealed seeds: report instability; do not pool into a win claim.
- Any post-unsealing change to cases, strategy semantics, scoring, stopping, or analysis invalidates confirmatory status.
- Any reliance on the v0.1 HOLDOUT as confirmatory v0.2 evidence invalidates the v0.2 claim.

## 19. Deferred questions

The following remain outside v0.2 and require separate specifications:

- calibrated observation reliability;
- stochastic/noisy or contradictory evidence;
- repeat observations and sequential evidence revision;
- missing or delayed evidence;
- probabilistic candidate predictions;
- model mismatch arising after probes rather than at initial evidence;
- deceptive high-information/low-reliability probes;
- human or model-assisted investigators;
- real incident data.

Deferral prevents an objective-comparison experiment from becoming an unidentifiable mixture of selection, inference, reliability, and model-mismatch changes.
