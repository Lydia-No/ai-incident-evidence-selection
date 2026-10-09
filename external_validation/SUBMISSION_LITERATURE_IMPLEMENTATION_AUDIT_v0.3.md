# AP-MINIMAX — submission / literature / implementation audit v0.3

**9 October 2026 | Audit and revision, not new experimental results.** This record distinguishes primary sprint notes, inspected repository code, and retrieved scholarly abstracts. The final submitted PDF and the verbatim Apart reviewer reports have **not** been located/read in this audit; no claim of reviewer-by-reviewer compliance is made.

## 1. Source and evidence ledger
- Sprint refresh (11 Sep 2026): central question is premature causal closure **and** next discriminating observation; predeclared sequential controls, fairness, neutral ties, independent metric recomputation, non-anticipation, model gaps. Its statements were planning-stage, not evidence that all gates passed.
- Addon review (13 Sep 2026): four *motivating* evidence-state examples — Anthropic retrieval gap, OpenAI/Hugging Face incident boundary, RubyGems cross-source divergence, Brömme evidence-preservation infrastructure. None validates AP-MINIMAX; maintain attribution boundaries and source-relative decision-time evidence.
- Repository inspected: `src/investigator/engine.py`, `experiments/strategies.py`, `experiments/cases.py`, `experiments/run.py` on `external-validation-50-case-setup-20261009`. Engine ranks discriminating probes lexicographically by worst-case survivor count, cost, then neutral tie rank. A single survivor triggers `RESOLVED` **relative to represented hypotheses**, not independent truth.
- Consensus scholarly records: Rodler (2018) *On Active Learning Strategies for Sequential Diagnosis*; Rodler (2023) *Sequential model-based diagnosis by systematic search*; Fisch et al. (2022) *Calibrated Selective Classification*. These are close prior art, **not proof of equivalence** without full-text comparison.

## 2. Claim audit and corrections
| Candidate claim | Audit disposition | Corrected wording / required evidence |
| --- | --- | --- |
| Novel minimax next-probe selection | **NOT ESTABLISHED** | One-step worst-case query selection is close to sequential diagnosis; compare formal objectives and implementations with Rodler before novelty claim. |
| Preserves ambiguity | **IMPLEMENTED WITH ASSUMPTIONS** | Preserves explanations consistent with declared deterministic predictions and observed evidence; wrong or missing predictions can eliminate true cause. |
| Prevents unsupported real-world causal closure | **NOT DEMONSTRATED** | A singleton is model-relative; assess false closure under out-of-set causes, forged/noisy observations, and co-occurring factors. |
| Outperforms strong baselines | **NOT ESTABLISHED HERE** | Existing repository strategies include neutral and information-gain selectors; cost-sensitive Bayesian EVI is specified in a later design document but **not verified implemented**. |
| Independent external validation | **NO** | AIID-50 is a feasibility sample; selected source audits have no complete decision-time oracle. Controlled fixture is self-audited. |
| 400-case holdout | **PRESERVE** | No new tuning, seed selection, or score changes to the frozen holdout. Independently recompute results from raw traces before quoting exact effects. |
| Reviewer concerns resolved | **UNVERIFIED** | Obtain verbatim reviewer reports and final PDF; map each comment to change, test and residual limitation. |

## 3. High-priority code / experiment risks
1. **Model gap:** `investigate()` handles zero survivors, but `experiments/run.py` has `outcomes[selected.probe_id]` for each selected probe; inspect model-gap path and validate no impossible oracle lookup. Missing true hypothesis may still yield one wrong surviving explanation: distinguish `model_gap_detected` vs `false_model_relative_resolution`.
2. **Closure semantics:** singleton -> RESOLVED regardless of evidence trustworthiness or hypothesis-set completeness. Rename in reporting to `MODEL_RELATIVE_SINGLETON`; only externally adjudicated truth supports `WARRANTED_CAUSAL_CLOSURE`.
3. **Evidence types:** current `_compatibility_record` treats missing prediction as contradiction; test missing/untrusted/contradictory observations separately. Do not silently change frozen v0.1 behavior.
4. **Probe fairness:** `INFORMATION_GAIN` assumes uniform mass over survivors; compare this to worst-case minimax on identical prior/likelihood/cost inputs and distinguish EVI from cost-normalized entropy heuristics.
5. **Independent recomputation:** report exact counts and costs from raw traces with a separate code path and frozen denominator; no claimed rerun in this audit.
6. **Bridge smoke test:** `external_validation/pilots/run_fixture_with_engine.py` and fixture were committed but **not verified executed**. The fixture is deliberately deterministic and author-designed; cannot establish external validity or method superiority.

## 4. Revised contribution positioning (candidate manuscript text)
> We study a bounded, decision-time evidence-selection problem in AI incident investigation: given a provisional set of causal explanations, a source-relative observation record, and authorized follow-up checks, can an explicit compatibility-preserving policy reduce premature *model-relative* closure while choosing useful subsequent observations at acceptable cost? Our implementation uses a one-step worst-case residual-hypothesis criterion with cost and neutral tie-breaking. We do not claim that this selection rule, abstention, or sequential diagnosis is new. The empirical question is whether this explicit protocol and its audit trace provide useful behavior in the incident-investigation setting, including cases where assumptions fail.

**Avoid** claiming novelty for minimax discrimination, abstention, evidence preservation, incident reconstruction in general, or performance on real incidents. State that the model may be incomplete, observations may be untrusted, and hypotheses may co-occur.

## 5. Revised test matrix, separated from frozen experiment
A. **Original frozen comparison:** do not modify; independently verify reported metrics, seeds, invariance and negative controls.
B. **Prospective controlled extension:** instrumented decision-time snapshots, complete outcome oracles, truth sealed from selectors, strong cost-sensitive EVI and sequential-diagnosis comparator when faithfully implemented; preregister adverse strata.
C. **External incident feasibility:** retain all AIID-50 cases in screening denominator; G1 provenance, G2 cutoff, G3 truth/oracle. Qualitative case studies are not performance wins.
D. **Risk/coverage:** count justified closures, unsupported closures, abstentions, costs, true-hypothesis elimination and model gaps separately; include always-abstain and forced-close negative controls.

## 6. Direct comparison needed against prior work
- Rodler 2018: compare query quality criteria, optimal partition notions, cost assumptions and sequential update semantics; avoid calling same minimax rule novel under a new name.
- Rodler 2023: compare search space, computational cost and query optimization, with full-text verification before asserting dominance/equivalence.
- Fisch et al. 2022: contrast selective *probabilistic classification/calibration* with deterministic *set-compatible incident hypotheses*; abstention alone is not new.
- Brömme 2026: evidence capture/integrity versus downstream evidence-selection decision; adjacent, not proof of uniqueness.

## 7. Go/no-go
**GO** for an honest manuscript revision and implementation audit. **NO-GO** for claims of new general minimax algorithm, superiority to strong sequential diagnosis, real-world causal accuracy, independent validation, or reviewer satisfaction. Priorities: (1) obtain final submitted PDF + verbatim reviews; (2) full-text prior-art mapping; (3) rerun and independently recompute frozen traces; (4) inspect and test model-gap/false-singleton behavior; (5) then prospective validation.

**References:** Rodler (2018), https://consensus.app/papers/on-active-learning-strategies-for-sequential-diagnosis-rodler/9ea791a57f6f517c9f799670fd84b406/ ; Rodler (2023), https://consensus.app/papers/sequential-modelbased-diagnosis-by-systematic-search-rodler/41c4e799aacb5fbeab25c08ad51cfa63/ ; Fisch et al. (2022), https://consensus.app/papers/calibrated-selective-classification-fisch-jaakkola/35272f7c8d345a9f89098fe0779029f5/ .
