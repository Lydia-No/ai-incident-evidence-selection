# External 50-case intake protocol — DRAFT v0.1

Status: NOT FROZEN / NOT PREREGISTERED / NO DATA SELECTED.

## Sampling frame
Choose one documented incident source collection and record its name, version/date, inclusion rules, accessibility, and licensing. Define a reproducible selection procedure and exclusion reasons *before* downloading or mapping the 50 target cases. Do not cherry-pick for favorable model performance.

## Eligibility
Require a stable incident identifier, dated source reference, enough source evidence to state at least two plausible explanations or a documented inability to do so, and a defensible distinction between observed facts and conjectures. Track cases that fail eligibility rather than silently replacing them.

## Evaluation tracks
A. Independently authored controlled cases with verifiable outcome ground truth: eligible for prespecified quantitative comparisons.
B. Real incident reports: source-bounded qualitative audit of next-check suggestions, traceability, ambiguity preservation and feasibility; no invented ground truth.
C. Omitted-hypothesis stress tests: distinguish contradictions that trigger MODEL_GAP from omitted causes that remain compatible with listed explanations.

## Method safeguards
- Separate source extraction, hypothesis construction, candidate probe generation, and selector evaluation.
- Avoid knowledge of eventual incident resolution when constructing time-bounded decision inputs.
- Audit whether every surviving explanation predicts each proposed probe; hard incompatibility is not a calibrated noisy likelihood.
- Compare against defensible alternatives with matched information and costs. The existing information-gain implementation is not automatically a probabilistically valid baseline when predicted outcomes overlap.
- Record disagreements and unresolved cases; do not silently discard them.

## GO gate
GO to sampling only after sampling frame, licensing, selection rule, and manifest schema are reviewed. GO to execution only after mappings, adapter, baselines, and evaluation criteria are frozen. No external performance result exists at this stage.
