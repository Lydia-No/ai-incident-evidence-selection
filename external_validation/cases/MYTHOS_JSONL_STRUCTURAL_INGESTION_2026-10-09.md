# Mythos 5 JSONL structural ingestion — verified 2026-10-09

## Provenance
Anthropic public GitHub repository `anthropics/mythos-5-incident-transcript`; `transcript.jsonl`; blob SHA `488d11d83def14275c364566a1016d22dcc89157`. Retrieved via GitHub **fetch_blob**, which returned 2,611,933 decoded text characters. The GitHub directory metadata reports file size 2,621,187 **bytes**. These measure different encodings and should not be compared as if identical. Parsed **in memory**; raw transcript not copied into our repository.

## Verified machine-readable structure
- **2,065 JSONL records**; **0 JSON parse failures**.
- **1 metadata** record and **2,064 message** records.
- Message indices: **0**, then **82–2144**, all unique, strictly increasing in file order. Indices 1–81 absent, consistent with documented redaction.
- Role: Assistant **2,061**, Human **2**, System **1**. These are *record roles*, not necessarily distinct conversation turns.
- Type: ToolMessage **1,361**, TextMessage **703**.
- ToolMessage tool names: `terminal` **932**, `view_tool` **230**, `create_tool` **152**, `str_replace_tool` **47**.
- Among ToolMessage records, **1,348** contain both `tool_call` and `tool_result`; **13** contain a `tool_result` but no `tool_call` (some include `tool_call_raw`). This is *structural*, not semantic verification of successful calls.
- `timestamp` is nonempty in **2,063** of 2,064 message records. The index-0 System timestamp (21:29Z) is later than index-82 (01:02Z) on the same date, so **timestamps are not globally monotone**; do not sort blindly by timestamp or assume index 0 marks the first wall-clock event.
- Last public record index **2144**. Anthropic README says messages after 2145 were redacted.

## Interpretation and limits
**TRACE INGESTED — STRUCTURE ONLY.** No individual decision point has yet been validated; no tool result was interpreted as an independent external probe outcome. Message indices are a safer starting sequence than naive timestamps but must be checked against event ordering and tool causality. Redacted prehistory 1–81 may hide original instructions and authorization context. Transcript is Mythos 5 PyPI incident, **not** AIID 1629.

## Next controlled step
Build a *metadata-only* cutoff register from candidate indices: preceding visible observations, prior tool call/response pairing, redaction dependency, and whether authorization/simulation boundaries were visible. Avoid publishing exploit commands or copying sensitive payloads. **NO-GO quantitative scoring** until independent labels and non-leaky cutoff packets exist. Anthropic README requests no training on transcript.

## Frozen studies
AIID 50-case sampling frame and synthetic 400-case holdout unchanged. This is a separate public-trace feasibility pilot.
