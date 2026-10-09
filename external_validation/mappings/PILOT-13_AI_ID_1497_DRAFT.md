# PILOT-13 — Brazilian labour-court prompt injection (AIID 1497)

Status: SOURCE-IDENTIFIED / SEQUENTIAL QUALITATIVE MAPPING DRAFT / NOT INDEPENDENTLY VALIDATED.

## Primary record to verify
- Brazilian regional labour court public news item: https://www.trt4.jus.br/portais/trt4/modulos/noticias/50981781
- AI Incident Database citation: https://incidentdatabase.ai/cite/1497
- Derivative catalog: DB-2026-077 (DavidFarago/ai_security_incidents_2026)

## Reported incident (derivative catalog only, not yet independently confirmed from full court article)
A malicious instruction was allegedly embedded in a labour-court petition intended for a court AI system (Galileu). The attack was reportedly blocked. The precise text, detection mechanism, timing, and any system logs are **not established** by the catalog entry alone.

## Decision-point hypothesis for research (analyst-generated)
At intake of an untrusted legal document, before relying on any AI-generated summary or advice:
- H1: document contains ordinary case-relevant factual assertions only;
- H2: document contains instruction-like text attempting to redirect the assistant;
- H3: suspicious content is quotation, example or legitimate legal text, not an operative instruction.

## Possible discriminating checks (proposals; not observed incident actions)
- Inspect provenance and trust boundary of suspicious text.
- Compare a document-only extraction to an instruction-following execution, in a safely isolated environment.
- Seek source-grounded context and human review before classifying the text as malicious.

## Evaluation restrictions
No case-specific probe predictions, action costs, ground-truth labels, or attack-success measurements can be assigned until the original court record is checked and a time-bounded decision trace is available. A blocked attack is not automatically evidence that AP-MINIMAX would succeed. The hypotheses above are not claimed to be the court's actual hypotheses.

## Decision
**HOLD** source confirmation and mapping review. Candidate for a useful negative/near-miss case, but not eligible for performance evaluation or an unqualified source-verified designation.
