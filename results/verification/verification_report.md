# A. FROZEN COMMIT SHA

- Repository: `Lydia-No/ai-incident-evidence-selection` (`https://github.com/Lydia-No/ai-incident-evidence-selection.git`)
- Branch: `main`
- Local `HEAD`: `f7c68a51ea4ccc1f58b3c0ac7d1079e0977c3ea9`
- Refreshed `origin/main`: `f7c68a51ea4ccc1f58b3c0ac7d1079e0977c3ea9`
- Exact match: yes
- Initial tracked and untracked worktree state: clean
- Freeze identity was recorded before tests or experiments.

# B. COMMANDS EXECUTED

Core identity and inspection commands:

```text
git rev-parse --show-toplevel
git remote -v
git branch --show-current
git rev-parse HEAD
git status --short --branch
git diff --stat
git diff --cached --stat
git fetch --prune origin main
git rev-parse origin/main
git log -1 --format='%H%n%cI%n%s' HEAD
find . -maxdepth 3 -type f -not -path './.git/*' -print | sort
git ls-tree -r --name-only HEAD
nl -ba <each committed source/configuration/documentation file>
```

Environment, declared test, and frozen executions:

```text
python --version
python -c 'import sys,platform; print(sys.executable); print(platform.platform())'
python -m pytest
PYTHONPATH=src python -m experiments.run --mode dev --output results/verification/raw_dev_f7c68a51_20260917T103407Z.jsonl
PYTHONPATH=src python -m experiments.run --mode holdout --output results/verification/raw_holdout_f7c68a51_20260917T103421Z.jsonl
chmod a-w results/verification/raw_dev_f7c68a51_20260917T103407Z.jsonl
chmod a-w results/verification/raw_holdout_f7c68a51_20260917T103421Z.jsonl
```

Independent post-freeze verification commands:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python results/verification/verify_frozen_trace.py --mode dev --raw results/verification/raw_dev_f7c68a51_20260917T103407Z.jsonl --metrics results/verification/dev_metrics.json --invariants results/verification/dev_invariants.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python results/verification/verify_frozen_trace.py --mode holdout --raw results/verification/raw_holdout_f7c68a51_20260917T103421Z.jsonl --metrics results/verification/holdout_metrics.json --invariants results/verification/holdout_invariants.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python results/verification/robustness_checks.py --output results/verification/robustness_results.json
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python results/verification/source_and_tie_audit.py --output results/verification/source_audit.json
rg -n --hidden --glob '!.git/**' --glob '!results/verification/**' 'hidden_truth|expected|hardcod|selected_cause|candidate_ids|tie_rank|sort\(|sorted\(|min\(|max\(' .
sha256sum results/verification/*
```

# C. TEST/CHECK RESULTS

- `python -m pytest`: **FAIL (exit 1 before collection)** — `/usr/bin/python: No module named pytest`.
- The frozen repository contains no committed `tests/` directory despite `pyproject.toml` declaring `testpaths = ["tests"]` and an optional pytest dependency.
- No lint, formatting, type-check, or other static-check command is configured in the repository.
- The test failure was recorded before experiments. No dependency was installed and no repair was attempted.
- Independent verification programs executed successfully, but they are post-freeze audit checks and are not substitutes for missing frozen tests.

# D. DEV HEADLINE RESULTS

- Command and seed: module command above; `DEV_SEED=26091200`.
- Generator/experiment: `v0.1` / `v0.1`.
- Cases: 40 (8 in each of five strata); strategies: 5; raw trace records: 315.
- Raw SHA256: `02195c55d358e2a0ac5d43f28ed6cc15ff93dbbc51342f29c90ded9b17853b38`.
- `ap_minimax`: 24 warranted/correct resolutions (60%), 8 unresolved (20%), 8 model gaps (20%), 0 premature closures; 36 observations, cost 59.
- `information_gain` reached the same terminal distribution with 33 observations and cost 58; `neutral_discriminating` used 39/cost 75; `neutral_all` used 71/cost 136.
- `forced_closure`: 8 warranted/correct resolutions, 24 premature closures, and 8 model gaps.

# E. HOLDOUT HEADLINE RESULTS

- Start timestamp: `2026-09-17T10:34:21Z`; Python `3.12.3`; Linux `6.8.0-139-generic` / glibc 2.39.
- Frozen commit: `f7c68a51ea4ccc1f58b3c0ac7d1079e0977c3ea9`; experiment/generator: `v0.1` / `v0.1`.
- Frozen seeds: `26091301, 26091302, 26091303, 26091304, 26091305`.
- Per seed: 80 confusable-resolvable plus 20 each clean-resolvable, persistent-ambiguity, model-gap, and no-failure. Total: 800 cases.
- Strategies: 5 (`ap_minimax`, `forced_closure`, `neutral_all`, `neutral_discriminating`, `information_gain`).
- Raw trace records: 6,321.
- Raw SHA256: `3c6818f6cbde34d007227b1ddccdb83b6fb4637571f4f0e0353e668093afa6bd`.

| Strategy | Terminal states | Warranted/correct | Premature | Observations total/mean | Cost total/mean |
|---|---:|---:|---:|---:|---:|
| ap_minimax | 600 R / 100 U / 100 MG | 600 (75%) | 0 | 849 / 1.06125 | 1498 / 1.8725 |
| information_gain | 600 R / 100 U / 100 MG | 600 (75%) | 0 | 811 / 1.01375 | 1485 / 1.85625 |
| neutral_discriminating | 600 R / 100 U / 100 MG | 600 (75%) | 0 | 1059 / 1.32375 | 2127 / 2.65875 |
| neutral_all | 600 R / 100 U / 100 MG | 600 (75%) | 0 | 1602 / 2.0025 | 3249 / 4.06125 |
| forced_closure | 100 R / 600 FC / 100 MG | 100 (12.5%) | 600 (75%) | 0 / 0 | 0 / 0 |

`R=RESOLVED`, `U=UNRESOLVED`, `MG=MODEL_GAP`, `FC=FORCED_CLOSED`.

# F. INDEPENDENT VERIFICATION RESULTS

Metrics were recomputed from every raw trace row using a separate compatibility and probe-scoring implementation against the frozen generated case definitions. No runner headline counter was trusted.

- **Warranted resolution:** the final independently compatible set has exactly one ID and `selected_cause` is that ID.
- **Warranted/correct resolution:** warranted resolution and `selected_cause == hidden_truth_id`.
- **Premature closure:** a cause is selected while the independently compatible set is not a singleton.
- **Unsupported incompatible selection:** selected cause is absent from the independently compatible set.
- **Unresolved:** multiple compatible explanations remain without forced closure.
- **Model gap:** zero explanations are compatible.
- **Observations/cost:** count of non-null selected probes and sum of their frozen costs.

For all four sequential strategies, the designed stratum outcomes were identical: 400/400 confusable cases resolved, 100/100 clean cases resolved, 100/100 no-failure cases resolved, 100/100 persistent-ambiguity cases remained unresolved, and 100/100 model-gap cases reported model gap. No sequential strategy made an unsupported or premature selection.

Mean observations / mean cost by nontrivial stratum (clean and model-gap cases were 0 / 0 for every strategy):

| Strategy | Confusable | No-failure | Persistent ambiguity |
|---|---:|---:|---:|
| ap_minimax | 1.3825 / 2.5125 | 1.85 / 3.02 | 1.11 / 1.91 |
| information_gain | 1.3325 / 2.48 | 1.67 / 2.91 | 1.11 / 2.02 |
| neutral_discriminating | 1.765 / 3.535 | 1.93 / 3.94 | 1.60 / 3.19 |
| neutral_all | 2.205 / 4.4475 | 2.20 / 4.47 | 5.00 / 10.23 |
| forced_closure | 0 / 0 | 0 / 0 | 0 / 0 |

`ap_minimax` versus each baseline, expressed as AP minus baseline on the predeclared metrics:

- `information_gain`: same terminal/safety results; **+0.0475** mean observations and **+0.01625** mean cost (AP was slightly worse).
- `neutral_discriminating`: same terminal/safety results; **-0.2625** mean observations and **-0.78625** mean cost.
- `neutral_all`: same terminal/safety results; **-0.94125** mean observations and **-2.18875** mean cost.
- `forced_closure`: AP had +0.625 warranted-resolution rate and -0.75 premature-closure rate, at +1.06125 observations and +1.8725 cost.

There were zero incompatible selected causes, including forced closure: its defect was premature selection among multiple still-compatible causes, not selection of an already-contradicted cause.

# G. INVARIANT / ROBUSTNESS RESULTS

- 6,321 before-state compatibility calculations and 4,321 post-reveal calculations matched the trace exactly.
- All 4,321 selected probes were independently reproduced from current public evidence, current candidates, available probes, costs, and neutral ranks only.
- All selected probes were available; no probe was reused; candidate counts matched IDs; before/after evidence, cumulative observation counts, and cumulative costs matched.
- Across 10,142 applicable before/after states, represented hidden truth remained compatible (0 failures).
- `RESOLVED` occurred only with one compatible explanation; `MODEL_GAP` only with zero; unresolved cases remained non-causal; forced closure remained `FORCED_CLOSED`.
- Source inspection found no hidden-truth reference in `experiments/strategies.py` or `src/investigator/engine.py`. In `run.py`, hidden truth appears only in four trace-serialization fields. Hidden truth is not passed to `choose_probe`; actual outcome is read only after selection.
- Changing only hidden-truth ID/family metadata caused 0 decision changes in 4,000 case-strategy checks.
- No hardcoded expected-output/gold-answer pattern was found.
- Tie ranks legitimately resolved 190 AP worst-case+cost ties and 119 information-gain+cost ties. Neutral policies are explicitly rank-defined (1,602 `neutral_all`, 1,059 `neutral_discriminating` choices).
- Explanation renaming, explanation-order reversal, and probe-order reversal: 4,000 checks each, 0 substantive failures (12,000 total). Explanation reversal changed candidate-list presentation order in 3,000 runs, but not candidate membership, probes, states, selected causes, observations, or costs.

# H. DISCOVERED PROBLEMS

1. The frozen test command is not executable in the present environment because pytest is absent, and the repository contains no tests. This prevents a clean frozen-test pass.
2. Setup and execution are undocumented: the README has only a title. The runner required the inferred module invocation plus `PYTHONPATH=src`; there is no committed lockfile or environment capture.
3. AP does **not** outperform every frozen baseline. `information_gain` achieves identical resolution/safety outcomes with 38 fewer observations and 13 lower total cost on HOLDOUT.
4. Aggregate terminal rates are largely fixed by designed stratum proportions. Clean/model-gap strata terminate from initial evidence, persistent ambiguity is constructed, and represented-truth outcomes are noiseless generator outputs. These results demonstrate internal behavior under this synthetic diagnostic model, not external incident-response superiority.
5. The forced-closure baseline is intentionally unsafe and therefore weak evidence of comparative superiority. The stronger information-gain baseline matches safety and slightly beats AP efficiency.
6. Trace rows that become terminal immediately after a reveal have terminal `state_after` but `terminal_action=null`; this is interpretable, but explicit terminal-action semantics are inconsistent with separately appended terminal rows.
7. No previous result files existed in the initial clean checkout. All result files listed below were generated by this audit; none are frozen-release artifacts.

# I. PASS / PARTIAL / FAIL VERDICT

**PARTIAL.**

The frozen runner executed deterministically at an exact local/remote-matching commit, its raw traces are internally consistent, and it supports a narrow claim: within the declared noiseless synthetic model, the ambiguity-preserving investigator avoids premature closure, preserves model gaps and irreducible ambiguity, and uses fewer observations/cost than the neutral-order baselines. A clean PASS is not defensible because frozen tests are unavailable, reproducible setup is undocumented, and AP fails to beat the strongest frozen baseline (`information_gain`) on efficiency while matching it on all terminal/safety outcomes.

# J. FILES CREATED OR CHANGED

No committed frozen source file was modified. No commit or push was made. The audit created the untracked `results/verification/` directory:

- `raw_dev_f7c68a51_20260917T103407Z.jsonl` (read-only original)
- `raw_holdout_f7c68a51_20260917T103421Z.jsonl` (read-only original)
- `dev_metrics.json`, `holdout_metrics.json`
- `dev_invariants.json`, `holdout_invariants.json`
- `robustness_results.json`, `source_audit.json`
- `verify_frozen_trace.py`, `robustness_checks.py`, `source_and_tie_audit.py`
- `verification_report.md`
- `artifact_manifest.json` (created after this report)

Python execution also created ignored bytecode caches under `experiments/__pycache__/` and `src/investigator/__pycache__/`. They contain no experimental inputs, outputs, or source changes.

# K. RECOMMENDED NEXT ACTION

Preserve this run unchanged as the v0.1 audit record. Before making any broader claim, independently review the audit scripts and decide whether the missing frozen tests/environment and the information-gain result require a new, separately versioned experiment. Any repair, new cases, noise model, or additional baseline must be a new pre-registered freeze with an unseen holdout; do not reinterpret or rerun this HOLDOUT as confirmatory evidence.
