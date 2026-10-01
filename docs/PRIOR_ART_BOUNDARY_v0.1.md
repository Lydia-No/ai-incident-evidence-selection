# Prior-Art Boundary v0.1

**Status:** FROZEN prior-art boundary for sprint v0.1.

## Established ideas we do not claim

- Active diagnosis already studies maintaining diagnostic hypotheses while selecting informative tests.
- Sequential model-based diagnosis already iteratively asks probes/measurements/questions to discriminate between multiple diagnoses.
- Active hypothesis testing / sequential experiment design already chooses experiments adaptively to eliminate false hypotheses efficiently.
- Bayesian experimental design commonly uses expected information gain to select informative experiments.

## Implication for the sprint claim

The sprint contribution is **not** “we invented maintaining multiple hypotheses” or “we invented information-gain probe selection.”

The bounded contribution is the operationalization and empirical stress-test of an auditable ambiguity-preserving protocol for autonomous-AI incident investigation, with explicit unresolved/model-gap states, staged heterogeneous evidence, concrete cross-organizational evidence requests, and reconstructable traces.

## Closest methodological comparators

- Bellala et al. (2013), *A Rank-Based Approach to Active Diagnosis* — sequential query selection in fault/diagnosis settings; discusses information-gain approaches.
- Rodler (2023), *Sequential model-based diagnosis by systematic search* — iteratively selects queries to discriminate among diagnoses.
- Active hypothesis testing / Chernoff-style sequential experiment design — adaptive experiment choice to eliminate false hypotheses.
- Bayesian experimental design — expected-information-gain optimization.

## Reviewer-safe wording

Prefer: **“We adapt and operationalize established active-diagnosis principles for autonomous-AI incident reconstruction under incomplete, heterogeneous evidence.”**

Avoid: **“We introduce a new general method for selecting diagnostic probes.”**

## Falsifiable sprint value

The sprint artifact must still earn its value by showing that, on frozen confusable incident cases, it:

1. does not force attribution while multiple explanations remain compatible;
2. surfaces model gaps rather than selecting an unsupported cause;
3. proposes operational checks whose possible outcomes have explicit causal consequences;
4. produces an auditable trace; and
5. maps these behaviors to concrete questions/checks from the July incident without claiming real-world validation.

## Freeze rule

New literature may narrow wording further, but no post-result literature discovery may be used to retroactively redefine the frozen experiment as a different success criterion.
