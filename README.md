# What Should We Check Next?
## An Auditable Ambiguity-Preserving Investigator for AI Incidents

Submission artifact for the Apart Research AI Incident Response Sprint, Track 2: **“What happened, and what breaks next.”**

## Project / Sprint submission

This repository is the reproducibility and research artifact associated with Linda Thorstensen's submission to the **Apart Research AI Incident Response Sprint**:

**What Should We Check Next? Testing Ambiguity-Preserving Evidence Selection for AI Incident Investigation**

Apart Research project page: https://apartresearch.com/sprints/projects/what-should-we-check-next-testing-ambiguitypreserving-evidence-selection-for-ai-incident-investigation-5nv4

The Apart page is the public Sprint project record. The repository preserves the implementation, frozen evaluation materials, provenance, and reproducibility evidence associated with the submission. Sprint projects are participant work and should not be interpreted as publications authored or endorsed by Apart Research.

## What this artifact tests

When incident evidence is incomplete, several causal explanations may remain compatible with what has actually been observed. This artifact tests whether a small, explicit investigator can:

- preserve all explanations still compatible with observed evidence;
- expose `UNRESOLVED` when evidence does not justify single-cause closure;
- expose `MODEL_GAP` when none of the supplied explanations fit;
- choose a next check using a frozen, auditable rule based on worst-case residual ambiguity, probe cost, and neutral tie-breaking;
- record enough trace information to reconstruct why explanations survived, were eliminated, or were selected.

The underlying ideas of active diagnosis, hypothesis testing, evidence requirements, and information gain are established prior art. The sprint contribution is a bounded AI-incident implementation, a frozen empirical stress test, and a source-bounded operational handoff on one documented incident.

## Frozen result

The experiment specification, case-generation rules, holdout seeds, comparators, primary endpoint, bootstrap seed, and PASS criteria were frozen before the first holdout result.

Primary population: **400 confusable-resolvable synthetic cases** across five frozen holdout seeds.

| Comparison | Mean paired difference in first-check realized value | 95% paired-bootstrap interval | Positive seeds | Wins / ties / losses |
| --- | ---: | ---: | ---: | ---: |
| AP-MINIMAX − NEUTRAL-ALL | **+0.5196** | **[0.4383, 0.5992]** | **5/5** | 235 / 129 / 36 |
| AP-MINIMAX − NEUTRAL-DISCRIMINATING | **+0.4213** | **[0.3458, 0.4954]** | **5/5** | 217 / 145 / 38 |
| AP-MINIMAX − INFORMATION-GAIN | +0.0458 | [0.0225, 0.0708] | 5/5 | 24 / 371 / 5 |

The pre-registered H2 decision was **PASS**.

AP-MINIMAX also made **0/400** unsupported premature closures on the confusable cases, compared with **400/400** for a deliberately forced-closure ablation. That comparison is a mechanism sanity check, **not** a state-of-the-art benchmark.

## Critical non-claim

**All non-forced strategies eventually resolved all 400 confusable-resolvable cases correctly.**

The supported synthetic advantage is therefore:

- higher realized value from the **next evidence check** under the frozen endpoint; and
- avoidance of unsupported causal closure.

It is **not** evidence that AP-MINIMAX has higher eventual attribution accuracy than the non-forced comparators, and it is not a claim of production incident-response effectiveness.

The information-gain reference tied AP-MINIMAX on 371/400 first checks. That high overlap is consistent with the prior-art boundary: the selection rule belongs to an established family of active-diagnosis ideas rather than constituting a new general diagnosis algorithm.

## Real-incident artifact

`incident/HUGGING_FACE_CASE_MAPPING_v0.1.md` maps the July 2026 OpenAI/Hugging Face incident as:

**documented fact → unresolved question → compatible explanations → discriminating evidence → operational check/request**

`incident/NEXT_EVIDENCE_REQUEST_PACKET_v0.1.md` turns selected unresolved questions into concrete evidence handoffs: evidence owner, exact records/fields, observable outcomes, causal consequences, resolution conditions, and conditions that should remain `UNRESOLVED` or become `MODEL_GAP`.

The public incident mapping demonstrates use of the protocol. It does **not** establish which explanation is correct and does **not** validate the synthetic result on the July incident.

## Reproduce the implementation and tests

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
pytest
```

Generate the frozen holdout trace:

```bash
python -m experiments.run --mode holdout --output artifacts/holdout_v0.1.jsonl
```

Independently recompute the reported analysis from a raw JSONL trace:

```bash
python -m analysis.recompute artifacts/holdout_v0.1.jsonl --output artifacts/analysis_v0.1.json
```

The submission does not rely on rerunning the holdout after seeing the result. The original immutable run is preserved separately and identified below.

## Frozen provenance

- execution-plan freeze: `9919c13c0fb07db3aec708e134632e2388b09d5c`
- pre-holdout code head: `3b9bd80d3b4e7adab08efcfda081a966c2e9e0c2`
- marker-only holdout commit: `f874168a91b447cdf704ad3cbe2868d5643b6ae1`
- GitHub Actions holdout run: `34664446883`
- immutable artifact ID: `10287944357`
- artifact ZIP SHA-256: `7d8ee3eca6dbb9891c941c5ee48c29a8045a063c35836b2c41bd903f9860c38f`
- raw JSONL SHA-256: `3c6818f6cbde34d007227b1ddccdb83b6fb4637571f4f0e0353e668093afa6bd`
- analysis JSON SHA-256: `053f8c7d9d840aa80ec659eedbb13284d2c6fb7f18568ae4122fa31f8b5b1692`

Independent verification and trace-integrity checks are documented in `docs/GATE6_INDEPENDENT_VERIFICATION_v0.1.md`.

## Research controls included here

- `docs/BEHAVIORAL_SPEC_v0.1.md`
- `docs/EXPERIMENT_PROTOCOL_v0.1.md`
- `docs/EXPERIMENT_EXECUTION_PLAN_v0.1.md`
- `docs/PRIOR_ART_BOUNDARY_v0.1.md`
- `docs/GATE6_INDEPENDENT_VERIFICATION_v0.1.md`

## Scope

This release intentionally contains the minimum material needed to evaluate and reproduce the sprint claim. It does not include unrelated research programmes, broader architecture, private publication strategy, exploratory mechanisms, or post-result drafting history.

## License

This repository is licensed under the MIT License. See `LICENSE`.
