# Audit of the v0.1 audit — version 1

## Scope and preservation

Reviewed the original contents of `results/verification/` without changing them and without executing `experiments.run`, `run_case`, or any frozen strategy over the HOLDOUT. Both raw traces remained read-only and retained their original hashes.

The strengthened checker `audit_of_audit_v1.py` reads the preserved raw trace, reconstructs only frozen case definitions, and does not import the frozen runner, strategy module, or investigator engine.

## Result

**The numerical v0.1 audit result is confirmed.**

- Original manifest-listed hashes: 0 mismatches.
- HOLDOUT coverage: all 800 cases, all five strategies, all 4,000 case-strategy groups, and all 6,321 records.
- Independent metric comparison: 0 differences across every overall and by-stratum field in `holdout_metrics.json`.
- Strengthened per-row trace checks: 0 errors.
- DEV headline recomputation from all 200 case-strategy groups and 315 records matched every reported terminal count, warranted/premature count, observation total, and cost total.
- Every numerical claim in `verification_report.md` is supported by the preserved JSON/raw artifacts.

The `PARTIAL` verdict remains correct.

## Review of each audit script

### `verify_frozen_trace.py`

- Hidden truth is used only to check represented-truth preservation and correctness after actions; it is not an input to `independently_choose`.
- Compatibility and probe objectives are reimplemented without importing the investigator engine or runner.
- Metric definitions correctly distinguish singleton-warranted resolution, selection from a non-singleton set, unresolved multi-candidate state, and zero-candidate model gap.
- All cases and strata are included; comparisons are paired over the same fixed suite.
- The metrics were specified by the audit request, not selected after observing favorable results.
- Independence is limited by reconstruction through the same frozen case generator. The script independently checks runner behavior against generated definitions, but cannot independently establish that the generator itself represents a valid external diagnostic world.

Coverage defect: its `all_trace_invariants_pass` label is broader than its implemented checks. It does not validate every per-row `state_after`, `selected_cause`, version/seed/stratum metadata, terminal-action label, or whether an unresolved final row stopped despite a remaining discriminating probe. The new checker adds those checks and found zero latent failures. Therefore this is a verification-coverage/reporting defect, not a result error.

### `robustness_checks.py`

- The transformations and normalized substantive signature are appropriate for explanation renaming, explanation-order reversal, and probe-order reversal.
- It changes hidden-truth ID only to keep renamed case metadata internally consistent; hidden truth is not used to select actions.
- It imports and calls the frozen `run_case`. Its 12,000 checks are therefore implementation metamorphic self-tests, not independent evidence that the implementation is scientifically correct.
- The report generally describes these as robustness checks, but the independence boundary should be explicit whenever the result is cited.

### `source_and_tie_audit.py`

- It uses hidden metadata only for a perturbation test and excludes hidden metadata from the decision signature.
- Static checks correctly show no `hidden_truth` token in the strategy or investigator modules, but the literal-string search is shallow and would not by itself exclude alias-based leakage.
- The source dataflow plus the independent public-state action reconstruction provide the stronger nonanticipation evidence.
- Like the robustness script, its 4,000 perturbation checks call `run_case` and are implementation self-tests.
- Tie counts match the preserved source-audit output and trace action totals.

## Classification and metric review

- **Warranted resolution:** correctly requires one independently compatible candidate and selection of that candidate.
- **Premature closure:** correctly identifies a selected cause when the compatible set is not a singleton. This classifies forced closure as premature even when the selected cause remains compatible.
- **Unsupported incompatible selection:** correctly separated from premature-but-compatible selection; count is zero.
- **Unresolved:** correctly means multiple compatible candidates remain without forced closure.
- **Model gap:** correctly means zero compatible candidates.
- **Correctness:** hidden truth is used only after the trace to score whether a warranted singleton is the represented truth.
- **Strategy fairness:** all strategies see the same cases; overall means use the same denominator; stratum results are retained. The arbitrary designed stratum mix limits interpretation of overall means but does not make the arithmetic comparison unfair.
- **Case omission:** none. Every frozen case-strategy group is present.
- **Post-hoc favorable metric:** none found in the headline results. Observation count, cost, terminal distribution, warranted/premature closure, unresolved, model gap, and requested invariants were all specified in the audit request. Tie counts and metamorphic counts are diagnostics, not promoted performance endpoints.

## Errors and qualifications found

1. **Manifest completion timestamp error.** `artifact_manifest.json` says the audit completed at `2026-09-17T10:38:20Z`, but the final original report and manifest were written later; the manifest file timestamp corresponds to `2026-09-17T10:39:36.331991820Z`. `artifact_manifest_v2.json` corrects this without replacing the original.
2. **Overbroad invariant label.** `all_trace_invariants_pass` means all checks implemented by the original verifier passed, not that every requested invariant was implemented. The versioned strengthened checker fills the identified gaps and still reports zero errors.
3. **Independence qualification.** The robustness and hidden-metadata perturbation counts exercise the same runner under transformations. They are valid metamorphic self-tests but must not be described as independent trace recomputation.
4. **Repeatability wording.** “Executed reproducibly” or “executed deterministically” is too strong for an experiment executed only once. The exact environment, commit, command, trace, and hashes are preserved; deterministic construction is supported by code inspection, but empirical byte-for-byte repeatability was not tested.

None changes a numerical result or the `PARTIAL` verdict.

## Corrected/versioned artifacts

- `audit_of_audit_v1.py`: strengthened non-runner trace and metric checker.
- `audit_of_audit_v1.json`: zero errors, metric differences, or original hash mismatches.
- `v01_ap_vs_information_gain_analysis.py` and `.json`: non-runner structural diagnosis.
- `V01_CLAIM_BOUNDARY.md`: corrected, narrower interpretation.
- `V01_AP_VS_INFORMATION_GAIN_DIAGNOSIS.md`: source/data-supported explanation.
- `artifact_manifest_v2.json`: corrected preservation metadata and hashes.

The original artifacts remain preserved and are not overwritten.

## Verdict impact

The original `PARTIAL` verdict still holds. The audit is useful and numerically sound, but a clean `PASS` remains inappropriate because frozen tests were unavailable, environment/setup was not locked, empirical repeatability was not tested, and information gain matched AP on every terminal/safety result while using slightly fewer observations and cost.
