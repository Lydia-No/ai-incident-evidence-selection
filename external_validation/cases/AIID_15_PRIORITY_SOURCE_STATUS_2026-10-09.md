# All 15 priority cases: source review status (2026-10-09)

This is a **source-availability review**, not 15 completed original-source audits. The 50-case sample remains fixed. Source status is intentionally conservative; no case passes Gate 3 and no performance scoring has been run.

| AIID | Original-source status | Gate 1 | Gate 2 | Gate 3 |
|---|---|---|---|---|
| 145 | Original video not checked | UNDETERMINED | UNDETERMINED | UNDETERMINED |
| 160 | Original interaction not checked | UNDETERMINED | UNDETERMINED | UNDETERMINED |
| 197 | Internal original report not checked | UNDETERMINED | UNDETERMINED | UNDETERMINED |
| 389 | Contemporary report citing city filing | UNDETERMINED | POTENTIAL | UNDETERMINED |
| 413 | Stack Overflow's own moderation policy | PROVISIONAL PASS (policy only) | UNDETERMINED | UNDETERMINED |
| 427 | NHTSA originals not checked | UNDETERMINED | UNDETERMINED | UNDETERMINED |
| 455 | Contemporary independent reporting, original corrections pending | UNDETERMINED | POTENTIAL | UNDETERMINED |
| 609 | Original query/output not checked | UNDETERMINED | UNDETERMINED | UNDETERMINED |
| 746 | Original lawsuit filing not checked | UNDETERMINED | UNDETERMINED | UNDETERMINED |
| 794 | Contemporary reporting with eyewitness source | UNDETERMINED | POTENTIAL | UNDETERMINED |
| 1442 | Amazon's own statement disputes AI causal attribution | UNDETERMINED (contested) | POTENTIAL | UNDETERMINED |
| 1544 | Original incident record not checked | UNDETERMINED | UNDETERMINED | UNDETERMINED |
| 1629 | Anthropic first-party investigation | PROVISIONAL PASS | POTENTIAL | UNDETERMINED |
| 1693 | AEPD regulator listing only; full text pending | UNDETERMINED | UNDETERMINED | UNDETERMINED |
| 1707 | Australian government statements; mechanism contested | PROVISIONAL PASS (bounded) | POTENTIAL | UNDETERMINED |

## Key independent source leads
- 389: https://www.wired.com/story/cruise-fire-truck-block-san-francisco-autonomous-vehicles/ (quotes city CPUC filing, which must be obtained).
- 413: https://meta.stackoverflow.com/questions/421831/policy-generative-ai-e-g-chatgpt-is-banned/ (platform primary policy, not original post-level accuracy labels).
- 455: https://www.engadget.com/cnet-reviewing-ai-written-articles-serious-errors-113041405.html (secondary; original CNET corrections needed).
- 794: https://www.theverge.com/2024/8/11/24218134/waymo-parking-lot-livestream-honking-4am-san-francisco (eyewitness and Waymo statement reported).
- 1442: https://www.aboutamazon.com/news/aws/aws-service-outage-ai-bot-kiro (first-party dispute; do not call Kiro the established cause).
- 1629: https://www.anthropic.com/research/investigating-incidents-cybersecurity-evals and https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents (first-party accounts, not independent transcripts).
- 1693: https://www.aepd.es/prensa-y-comunicacion/blog (listing, full article pending).
- 1707: https://www.pm.gov.au/media/press-conference-new-york (government statement, technical mechanism not resolved).

## Research decision
**NO-GO quantitative external evaluation for all 15.** Case 1629 is a strong candidate for deeper trace retrieval, not an automatic pass. Cases 1442 and 1707 are useful tests of source disagreement and uncertainty preservation. Seven cases remain without independently checked original evidence; this must not be described as full verification. A full 15-row local CSV register accompanies this research step but is not committed to the repository. Frozen synthetic tests untouched.
