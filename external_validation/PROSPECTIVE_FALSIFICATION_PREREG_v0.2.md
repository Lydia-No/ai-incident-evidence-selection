# AP-MINIMAX — prospective falsification protocol v0.2

**2026-10-09 | PREREGISTRATION DRAFT, NOT RUN.** Revises v0.1 without rewriting it. The fixed synthetic 400-case holdout and fixed AIID-50 sampling frame remain untouched. Controlled testbed results must not be presented as naturalistic external validation.

## 1. Falsifiable claims (separate, not interchangeable)
C1 **Selection**: AP-MINIMAX improves first-probe *truth-compatible discrimination* over baselines at matched cost and evidence budget.
C2 **Calibration / closure**: AP-MINIMAX makes fewer **unsupported closures** (declaring a single explanation when more than one remains compatible under the independent oracle), without simply abstaining on every case.
C3 **Robustness**: AP-MINIMAX loses less utility under predeclared observation noise, misspecified priors and correlated probes.
**Null and adverse findings are publishable outcomes**. No single composite 'win' substitutes for separate tests.

## 2. Independent case creation, before method selection
- Use a *method-agnostic*, versioned generator of benign, instrumented software incident episodes with explicit latent state, event log, initial observations, permissible read-only evidence requests, and **fully enumerated deterministic or distributional response oracles**. Generation code and parameters must not call AP-MINIMAX, inspect its decisions or optimize cases against its scoring rule.
- Generate cases from preregistered strata: **easy discrimination, observational equivalence, conflicting evidence, correlated evidence, noisy observation, unequal cost, prior misspecification, misleading low-cost probes, and nonidentifiability**. Include explicit anti-AP-MINIMAX cases where minimizing worst-case ambiguity is expected to be cost-inefficient; such expectations must be recorded *before* results.
- Case-author record: random seed, generator version/commit, raw log hashes, frozen cutoff, finite hypothesis set (including possible OTHER/UNKNOWN), permitted probe table, response oracle for each hypothesis, real costs, and independent truth key. Retain all generated cases in screening register; report exclusions and reasons before revealing method outcomes.
- No real credentials, malware, live third-party scanning or undisclosed external services. Do not fabricate historical counterfactuals: all probe outcomes must come from an **instrumented testbed oracle** and be labeled as such.

## 3. Separation, sealing, leakage controls
A case-author creates sealed truth and full oracle. An independent reviewer verifies case coherence and authorization **without seeing selector outputs**. The selector receives only cutoff snapshot, hypothesis descriptions, allowed probes, costs, and an explicitly specified common observation model when applicable. If case author/reviewer/analyst are the same person, label **self-audited feasibility**, never independent validation. Record canonical JSON SHA-256 of frozen keys and schema version. Hashing does not establish independence.

## 4. Baselines (same information, budget and abstention options)
B0 seeded uniform authorized probe; B1 cheapest authorized probe; B2 precommitted fixed order; B3 expected information gain with common priors/likelihoods; **B4 cost-sensitive Bayesian expected value of information (EVI)** with an explicit loss for wrong closure, evidence cost and an abstain/defer action. Report B3/B4 eligibility; if likelihoods unavailable, do not supply them selectively or treat missing as zero. AP-MINIMAX may use only information available to baselines, except clearly predeclared method-specific transforms. **No oracle truth or realized probe outcomes exposed before selection**.

## 5. Endpoints and adjudication
Primary feasibility endpoints, separately reported: (a) **first-probe discrimination**: independently defined reduction of compatible hypotheses while retaining true state, (b) **unsupported closure rate** among all episodes and among episodes where a method issues a closure, (c) **coverage**: proportion of episodes with justified closure or documented abstention. Report all denominators.
Secondary: normalized information gain when probabilistic models are well calibrated; cost to justified resolution; number of requests; false elimination of true state; retained ambiguity when truth is nonidentifiable; sensitivity to noise, correlation, cost and priors. **Do not use method's own internal uncertainty estimate as its ground truth**.
An always-abstain policy is a mandatory negative control: it has zero unsupported closures but low closure coverage. A premature-closure policy is a second negative control. Compare *risk–coverage curves* rather than closure error alone.

## 6. Paired analysis and adverse-result rules
Freeze all algorithms, thresholds, random seeds, strata and budget before unsealing. Compute paired per-case differences against B0–B4, show per-stratum effects and uncertainty intervals clustered by case. Multiple comparisons exploratory unless an explicit correction/hierarchy is preregistered. For 12–20 episodes treat results as **pilot feasibility**; no powered superiority claim. Record worst cases and AP-MINIMAX failures, not just aggregate means. If B4 matches/exceeds AP-MINIMAX or the effect disappears under prior misspecification, state this directly and narrow the contribution claim.

## 7. Stop / go gates
G1 source/generator provenance and deterministic rerun; G2 decision-time information separation and leakage audit; G3 sealed, independently adjudicated truth and complete permitted probe oracle; G4 fair shared information and cost accounting across AP-MINIMAX and B0–B4. **Any failed G2–G4 blocks quantitative performance claims**. Keep failures in denominator. Where a probe has no validated oracle, exclude it from primary scoring rather than inventing a result.

## 8. Implementation order
1. Implement a schema and validator for one benign three-hypothesis/three-probe case, with explicit truth/selector separation.
2. Run negative controls and B0–B4 before AP-MINIMAX; verify no oracle leakage.
3. Freeze generator and scoring, then run AP-MINIMAX from a pinned commit.
4. Expand only after the first case passes gates, with an external reviewer for independence claims.

**Status: design revision committed; zero prospective cases executed, zero independent reviews.**
