# Pilot feasibility matrix — 2026-10-09

Status: PRELIMINARY TRIAGE ONLY. These are 15 candidate records from a derivative catalog, not a representative or validated AIID sample. No outcomes or baseline scores have been computed.

| Pilot | AIID | Incident category | Primary-source verification | Sequential mapping | Quantitative eligibility | Principal concern |
|---|---:|---|---|---|---|---|
| 01 | 1412 | Autonomous security testing / SQLi | Initial original report reviewed | Qualitative candidate | NO | Retrospective account, outcome leakage |
| 02 | 1368 | Malicious agent skills | Pending | Not mapped | NOT ASSESSED | Campaign aggregation vs single decision |
| 03 | 1469 | Agent deletion of production database | Pending | Not mapped | NOT ASSESSED | Logs and authority boundary unknown |
| 04 | 1507 | Student data exposure / vendor AI | Pending | Not mapped | NOT ASSESSED | AI causal role and data access boundaries |
| 05 | 1364 | Agent-platform data exposure | Pending | Not mapped | NOT ASSESSED | Security misconfiguration vs AI causal role |
| 06 | 1395 | Model distillation allegation | Pending | Not mapped | NOT ASSESSED | Attribution and independently observable probes |
| 07 | 1424 | Terraform production destruction | First-person report reviewed | Qualitative mapping drafted | NO | Reconstruction informed by outcome |
| 08 | 1471 | Internal agent security incident | Pending | Not mapped | NOT ASSESSED | Sparse public incident detail |
| 09 | 1472 | Deepfake identity fraud | Pending | Not mapped | NOT ASSESSED | Multiple fraud events / independent units |
| 10 | 1389 | Robot-vacuum cloud exposure | Pending | Not mapped | NOT ASSESSED | AI relevance and original source provenance |
| 11 | 1441 | Agent deleted personal photos | Pending | Not mapped | NOT ASSESSED | Anecdotal account / missing action trace |
| 12 | 1418 | Smart-glasses human review / privacy | Pending | Not mapped | NOT ASSESSED | Organizational process, not a probe sequence |
| 13 | 1497 | Prompt injection near miss | Pending (court source linked) | Provisional draft only | NO | Blocked-attack assertion unverified |
| 14 | 1362 | Facial recognition / civil rights | Pending | Not mapped | NOT ASSESSED | Disputed causality and ethical context |
| 15 | 1390 | Surveillance allegation | Pending | Not mapped | NOT ASSESSED | Low-confidence derivative claim |

## Sampling design decision
The present 15 are a **convenience feasibility sample** from 17 AIID-linked entries in one derivative 2026 incident compilation, selected by derivative ID. They are **not** an independent random draw from the AI Incident Database and cannot support generalizable rate estimates. Before expanding to 50, obtain a reproducible primary-database snapshot or documented export, stratify by incident mechanism and available evidence, and retain exclusions. A separate independent test set should be drawn only after inclusion criteria and analysis protocol are frozen.

## Gate
GO: source verification and qualitative feasibility audit. NO-GO: external model performance, precision estimates, or treating 50 as already sourced. No changes to existing frozen 400-case experiment.
