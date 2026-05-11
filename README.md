# Build 2 — CV-to-Standardized-Profile

🚧 **Work in progress.** Ship target: 10–12 May 2026.

See SCOPE.md for what this build does, what's out of scope, and definition of done.

Architecture, eval results, and ROI math will land here once v1 ships.

## Schema

This pipeline maps unstructured CVs onto a controlled, structured profile. Two schema variants are maintained side by side:

| File | Purpose |
|---|---|
| [`schema/profile.schema.json`](schema/profile.schema.json) | Canonical specification — full JSON Schema Draft-07 with `$schema`, `$id`, descriptions, format constraints, and minimal `required` (only `name`). Single source of truth for the data structure. |
| [`schema/profile.strict.schema.json`](schema/profile.strict.schema.json) | Runtime variant adapted for **OpenAI Structured Outputs Strict Mode**: all properties marked `required`, optional fields typed as `["type", "null"]`, format/pattern/minLength keywords removed, no `$schema`/`$id`. Used by the pipeline's extraction LLM node. |

Both describe the same data structure. The runtime variant exists because OpenAI Strict Mode imposes additional constraints beyond standard JSON Schema; keeping the canonical variant clean preserves it as documentation independent of any single LLM provider.

## Architecture Decisions

### Why text-extraction path (not direct vision-to-LLM)
- 8 of 20 CVs in eval set are DOCX — no LLM accepts DOCX directly, 
  so a text-extraction step is required regardless
- Keeping all formats on one pipeline gives one debugging surface
- Cost difference vs. vision is marginal at this volume in 2026 
  (~$30/month at 3,500 CVs)
- v2-roadmap: hybrid approach — simple layouts via text, complex 
  layouts (multi-column, embedded tables) via vision API based on 
  eval-driven trigger

### Why GPT-4o (not gpt-4o-mini, not Claude)
- Structured extraction is core use case for GPT-4o
- OpenAI Structured Outputs guarantee schema compliance >99%
- Smaller models lose 3-5pp accuracy on edge cases 
  (career-switcher, multi-sector)
- Build 1 used OpenAI — provider consistency
- v2-roadmap: A/B test against Claude Sonnet 4.6 
  (leads on extraction accuracy benchmarks at 97.6%)

### Why n8n (not custom Python service)
- Workflow is the legible artifact — Pascal/Lennart see every step
- Langdock customers use workflow tools, not custom code
- Validation in n8n Code-Node is appropriate for single pipeline
- v2-trigger: extract validation to FastAPI microservice when 
  2+ pipelines share validation logic

### Why CloudConvert for DOCX in v1 (not self-hosted, not AWS Textract)

- 8 of 20 CVs in the eval set are DOCX. n8n Cloud's standard Code Nodes disallow `require('mammoth')`, so DOCX-to-text conversion requires either a self-hosted runtime or an external service.
- **v1 choice:** CloudConvert. Free tier (25 conversions/day) is sufficient for eval, native n8n node exists, REST API is documented. Synthetic test data means no real PII flows through a US vendor.
- **v2 trigger:** as soon as the pipeline processes real candidate data, swap to AWS Textract Frankfurt for EU data residency with standard enterprise DPA.
- **v3 trigger:** if the customer's DPO rejects US-vendor regional deployments (US CLOUD Act exposure), migrate to self-hosted n8n + mammoth on EU infrastructure, or AWS European Sovereign Cloud, or STACKIT.
- **Architecture invariant:** all three tiers use the same HTTP-Request shape. Provider swap is a credential change, not a workflow change.

### Why Google Sheets as ATS stand-in
- v1 mock for demo without real ATS access
- Production architecture: replaced by REST-API call to ATS 
  (SAP SuccessFactors, Personio)
- Architecture impact of v1 → production: only the last node changes

## Pending before eval phase

- [ ] Re-review all 20 ground_truth JSONs against updated LABELING_CONVENTIONS (functional_expertise: liberal with role evidence — internships count when role title clearly reflects function)
- [ ] Document convention-drift pattern in FAILURE_LOG (discovered through first end-to-end pipeline run)
- [ ] Instrument pipeline (cost, latency, token tracking per LLM call)
- [ ] Run full pipeline against eval set (Field-Level F1, baseline comparison)
- [ ] BREAK session: adversarial inputs (10-15 stress CVs)

## Compliance and Sovereignty

CV extraction touches PII, so the deployment tier matters. v1 uses CloudConvert (US-based SaaS) for DOCX-to-text conversion. This is appropriate for the synthetic eval set but not for production with real candidate data.

| Compliance need | v1 (this build) | v2 (production-ready) | v3 (fully sovereign) |
|---|---|---|---|
| Synthetic data, demo | CloudConvert (US) ✓ | — | — |
| EU data residency, US vendor acceptable | CloudConvert Enterprise with DPA | AWS Textract Frankfurt region | — |
| US CLOUD Act exclusion required | — | — | Self-hosted mammoth on EU infrastructure, AWS European Sovereign Cloud (GA Jan 2026), or STACKIT (Schwarz-Gruppe) |

Customer chooses the tier based on their procurement constraints. German Mittelstand consulting firms typically accept v2 with US-vendor DPA. Regulated industries (banking, insurance, government, healthcare) require v3.

The pipeline architecture supports all three tiers by isolating DOCX conversion behind an HTTP node — swapping providers is a configuration change, not an architectural rebuild.

## Security and Governance Note

Data flows in v1:

1. **Inbound:** CV file (DOCX/PDF/TXT) via webhook POST to n8n Cloud (hosted by n8n GmbH, Berlin, EU)
2. **DOCX conversion:** DOCX files only — uploaded to CloudConvert (US) for text extraction. Files retained per CloudConvert retention policy (24h on free tier). PDF and TXT files do not leave the n8n Cloud environment.
3. **Extraction:** plaintext sent to OpenAI API. OpenAI does not train on API data; logs retained 30 days for abuse monitoring.
4. **Output:** structured profile written to Google Sheets (Google Cloud, EU region available).

What a DPO would object to in v1:
- CloudConvert is US-based — for production with real PII, requires either Enterprise DPA or migration to EU-resident alternative (see Compliance and Sovereignty section)
- OpenAI is US-based — production deployments would route via OpenAI EU data residency option (announced 2024, generally available 2026) or Azure OpenAI Service in EU region with DPA

Mitigations already in place:
- Synthetic eval data only — no real candidate PII processed
- Sheet contains no resume PDFs themselves, only extracted structured data
- Pipeline is stateless — no candidate data persists in n8n beyond the active execution