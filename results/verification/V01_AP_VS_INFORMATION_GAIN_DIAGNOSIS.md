# v0.1 AP minimax versus information gain diagnosis

## Question

Why did AP minimax and information gain reach identical terminal/safety outcomes, while information gain used slightly fewer probes and lower total cost?

This diagnosis uses only the preserved raw HOLDOUT trace and deterministic reconstruction of the frozen case definitions. It does not call the experiment runner or frozen strategy functions and does not rerun the HOLDOUT.

## Findings

### Terminal equivalence is primarily structural

The identical terminal outcomes are principally caused by case construction, noiseless deterministic compatibility, and shared stopping semantics—not by the two objectives being generally equivalent.

- **100 clean-resolvable cases** begin with exactly one compatible explanation. Neither policy selects a probe.
- **100 model-gap cases** begin with zero compatible explanations. Neither policy selects a probe.
- **400 confusable-resolvable plus 100 no-failure cases** have survivor signatures that are unique across the full probe set. With noiseless outcomes and monotone elimination, any policy that continues selecting discriminating probes must eventually reach the represented singleton truth.
- **100 persistent-ambiguity cases** contain nonunique survivor signatures: the truth and a twin make identical predictions across every probe. No evidence-selection order can distinguish them, so both policies must stop unresolved under the shared no-discriminating-probe rule.

Thus 200/800 cases terminate before selection, 500/800 are guaranteed resolvable by the available deterministic signatures, and 100/800 are guaranteed irreducibly ambiguous. This fixes the terminal distribution for both competent sequential policies.

### The observation model removes safety differentiation

- All 16,000 candidate-probe prediction sets are singleton-valued.
- All 3,500 realized outcomes for represented truths match the corresponding truth prediction.
- There is no observation reliability, noise, contradiction process, missing reveal, or temporal revision.
- Compatibility only shrinks monotonically as exact observations are added.

Under these conditions, neither AP nor information gain faces a tradeoff between discrimination and evidence reliability. The represented truth cannot be removed, and no strategy-specific false-resolution mechanism is exercised.

### The objectives do differ, but only in a narrow partition pattern

Across 880 unique realized public decision states visited by AP or information gain:

- the independently computed choices agreed in 801 states;
- they differed in 79 states;
- all 79 differences occurred with four compatible explanations;
- choices agreed in every visited two- and three-survivor state.

The reason is the small deterministic partition space:

- With two survivors, every discriminating probe has partition `1+1`; AP and information gain have the same discrimination ordering.
- With three survivors, `1+1+1` dominates `2+1` for both worst-case residual and entropy; otherwise the available discriminating probes are equivalent on the primary objective.
- With four survivors, `2+2` and `2+1+1` both have worst-case residual 2, so AP moves to cost and neutral rank. Information gain prefers `2+1+1` because its entropy gain is 1.5 bits rather than 1 bit.

Every one of the 79 divergent first choices had exactly this form:

| Stratum | AP partition | IG partition | Cases |
|---|---:|---:|---:|
| Confusable resolvable | `2+2` | `2+1+1` | 38 |
| No failure | `2+2` | `2+1+1` | 31 |
| Persistent ambiguity | `2+2` | `2+1+1` | 10 |

In 58/79 divergences, AP's selected probe had lower immediate cost; in 21/79 the costs tied and neutral rank selected AP's probe. Information gain's higher-information probe produced a singleton realized survivor in 38 cases, saving one observation. In the other 41 cases, both choices left two survivors.

At case level:

- terminal state was identical in 800/800 cases;
- the full probe sequence was identical in 721/800;
- observation count tied in 762 cases and AP used one more observation in 38; AP never used fewer;
- total cost tied in 746, AP was lower in 23, and AP was higher in 31.

The net result—AP +38 observations and +13 cost—is therefore explained by a real but narrow objective difference, not by leakage or terminal safety failure.

### Cost structure is secondary, not absent

Probe costs are already asymmetric: among 4,000 frozen probes, costs 1, 2, and 3 occur 1,319, 1,350, and 1,331 times. Both strategies use cost only as a lexicographic secondary criterion after their ambiguity/information objective. AP often chose a cheaper first probe in divergent states, but the additional follow-up sometimes erased that saving. Random cost assignment affects efficiency totals but does not explain terminal equivalence.

### Stratum composition dilutes the policy comparison

The 200 initial-terminal cases contribute zero probes and zero cost to both strategies. The 100 persistent cases are structurally unresolvable. Overall means therefore mix policy-sensitive and policy-insensitive cases in a generator-chosen ratio. Stratum-specific and paired case-level comparisons are more informative than the 800-case aggregate.

## Causal diagnosis within the code/data boundary

Ranked by importance for terminal equivalence:

1. **Case construction and deterministic signatures:** primary.
2. **Noiseless, singleton-valued observations:** primary.
3. **Shared compatibility and stopping rules:** primary.
4. **Small survivor/partition structure:** explains why objectives usually select the same probe.
5. **Stratum composition:** fixes and dilutes aggregate rates.
6. **Cost structure:** explains part of the small efficiency difference, not terminal equivalence.

No evidence supports attributing equivalence to general mathematical identity between minimax and information gain. The objectives demonstrably diverge on the 79 `2+2` versus `2+1+1` states.

## Implication for v0.2

The smallest unresolved question is whether the objectives have different mean-versus-tail and cost tradeoffs on cases deliberately containing preregistered objective conflicts. Noise should not be added in the same first follow-up experiment: v0.1 has no probabilistic compatibility or reliability semantics, so adding noisy evidence would conflate probe selection with a new inference/update model. Reliability deserves a later separately frozen study after the objective tradeoff is isolated.
