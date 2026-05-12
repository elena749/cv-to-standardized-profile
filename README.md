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

Both describe the same data structure. The runtime variant exists because OpenAI Strict Mode imposes additional constraints beyond standard JSON Schema; keeping the canonical variant clean preserves it as documentation independent of any single LLM provider. See *"Why a separate Strict-Mode schema variant"* in Architecture Decisions for the full rationale.

## Architecture Decisions

### Why text-extraction path (not direct vision-to-LLM)
- 8 of 20 CVs in eval set are DOCX — no LLM accepts DOCX directly in the n8n OpenAI node (PDF only as of May 2026), so a text-extraction step is required regardless
- Keeping all formats on one pipeline gives one debugging surface
- Cost difference vs. vision is marginal at this volume in 2026 (~$30/month at 3,500 CVs)
- Reproducibility better than vision-LLM (~95% vs ~93% across repeat runs on same input)
- v2-roadmap: hybrid approach — simple layouts via text, complex layouts (multi-column, embedded tables) via vision API based on eval-driven trigger

### Why GPT-4o (not gpt-4o-mini, not Claude)
- Structured extraction is core use case for GPT-4o
- OpenAI Structured Outputs guarantee schema compliance >99%
- Smaller models lose 3-5pp accuracy on edge cases (career-switcher, multi-sector)
- Build 1 used OpenAI — provider consistency
- v2-roadmap: A/B test against Claude Sonnet 4.6 (leads on extraction accuracy benchmarks at 97.6%)

### Why n8n (not custom Python service)
- Workflow is the legible artifact — Pascal/Lennart see every step
- Langdock customers use workflow tools, not custom code
- Validation in n8n Code-Node is appropriate for single pipeline
- v2-trigger: extract validation to FastAPI microservice when 2+ pipelines share validation logic

### Why a separate Strict-Mode schema variant (not one schema for both)

OpenAI Structured Outputs Strict Mode imposes constraints beyond standard JSON Schema: all properties must be in `required`, optional fields must use union types like `["string", "null"]`, and format/pattern/minLength keywords are not supported. Two paths were considered:

1. **One schema, Strict-Mode-compliant:** modify the canonical schema to satisfy Strict Mode constraints. Loses standard JSON Schema features (format validation, descriptions, `$schema`/`$id` metadata) in the canonical file.
2. **Two schemas, separate concerns:** keep the canonical schema as provider-independent documentation; derive a runtime variant for OpenAI Strict Mode.

**Decision:** Option 2 — two schemas, separate concerns.

**Rationale:** the canonical schema is documentation that outlives any single LLM provider. If we A/B-test against Claude in v2 (already in roadmap), or migrate to a different provider entirely, we don't want to have already compromised the canonical schema to fit OpenAI's runtime requirements. The two-schema pattern isolates provider-specific constraints behind a derivation step.

**Trade-off accepted:** two files to keep in sync. Mitigation: the derivation rules are documented in the Schema section so the runtime variant can be regenerated mechanically if the canonical schema changes.

**v2-trigger:** if/when multiple LLM providers are supported (Claude, Gemini, others), formalize the derivation as a build-step script rather than manual sync.

### Why DOCX is deferred to v2 (not in v1)

v1 processes PDF and TXT only — 14 of 20 eval CVs. DOCX (the remaining 8) is deferred. Four conversion paths were evaluated:

| Option | Setup | Compliance | Status |
|---|---|---|---|
| OpenAI Responses API native DOCX (Feb 2026) | Medium | US vendor processes file | n8n's OpenAI node currently exposes PDF only as file input |
| AWS Textract Frankfurt | Medium-high | EU data residency, US CLOUD Act applies | Production-ready, v2 candidate |
| AWS European Sovereign Cloud Textract (Jan 2026) | High (enterprise onboarding) | Full EU sovereignty, US CLOUD Act excluded | v3 candidate for regulated industries |
| CloudConvert | Low | US vendor only | Synthetic demo only |

**v1 decision:** ship PDF + TXT pipeline. Defer DOCX until either (a) n8n exposes DOCX in the OpenAI Responses node, or (b) a customer's compliance tier determines which AWS Textract variant fits. The DOCX path is a compliance choice, not a technical gap — it should be made when the customer is identified, not pre-empted by v1 defaults.

**Build phasing rationale:** Phase 1 (happy-path end-to-end) ships PDF + TXT. Phase 2 (eval against ground truth) measures the existing pipeline's quality. Phase 4 (format expansion) extends to DOCX with data-driven compliance-tier selection. Expanding formats before Phase 2 measurement means building on an unmeasured foundation.

**Architecture invariant:** all four DOCX paths plug into the existing pipeline at the same point (between the file-type router and the OpenAI extraction node). Adding DOCX in v2 is additive, not a rebuild.

### Why Google Sheets as ATS stand-in
- v1 mock for demo without real ATS access
- Production architecture: replaced by REST-API call to ATS (SAP SuccessFactors, Personio)
- Architecture impact of v1 → production: only the last node changes

## Compliance and Sovereignty

CV extraction touches PII, so the deployment tier matters. v1 uses synthetic eval data only and does not yet process DOCX (see Architecture Decisions).

| Compliance need | v1 (this build) | v2 (production-ready) | v3 (fully sovereign) |
|---|---|---|---|
| Synthetic data, demo | OpenAI direct ✓ | — | — |
| EU data residency, US vendor acceptable | OpenAI EU region | AWS Textract Frankfurt for DOCX | — |
| US CLOUD Act exclusion required | — | — | Self-hosted n8n + mammoth on EU infrastructure, AWS European Sovereign Cloud (GA Jan 2026), or STACKIT (Schwarz-Gruppe) |

Customer chooses the tier based on their procurement constraints. German Mittelstand consulting firms typically accept v2 with US-vendor DPA. Regulated industries (banking, insurance, government, healthcare) require v3.

The pipeline architecture supports all three tiers by isolating each external service behind a stable interface — swapping providers is a configuration change, not an architectural rebuild.

## Security and Governance Note

Data flows in v1:

1. **Inbound:** CV file (PDF or TXT) via webhook POST to n8n Cloud (hosted by n8n GmbH, Berlin, EU)
2. **Extraction:** plaintext sent to OpenAI API. OpenAI does not train on API data; logs retained 30 days for abuse monitoring
3. **Output:** structured profile written to Google Sheets (Google Cloud, EU region available)

What a DPO would object to in v1:
- OpenAI is US-based — production deployments would route via OpenAI EU data residency option or Azure OpenAI Service in EU region with DPA
- Google Sheets is a mock — production replaces this with direct ATS REST-API call

Mitigations already in place:
- Synthetic eval data only — no real candidate PII processed
- Sheet contains no resume PDFs themselves, only extracted structured data
- Pipeline is stateless — no candidate data persists in n8n beyond the active execution

## Pending before eval phase

- [ ] Re-review all 20 ground_truth JSONs against updated LABELING_CONVENTIONS (functional_expertise: liberal with role evidence — internships count when role title clearly reflects function)
- [ ] Document convention-drift pattern in FAILURE_LOG (constraint leakage discovered through first end-to-end pipeline run)
- [ ] Instrument pipeline (cost, latency, token tracking per LLM call)
- [ ] Run full pipeline against eval set — 14 of 20 CVs (PDF + TXT only in v1)
- [ ] Compute Field-Level F1 with baseline comparison (zero-shot GPT-4o without schema)
- [ ] BREAK session: adversarial inputs (10-15 stress CVs)

## Deferred to v2

- [ ] DOCX support — compliance-driven path selection (see Architecture Decisions)
- [ ] Email-trigger for inbound CV files (currently webhook-only)
- [ ] REST-API output to ATS (currently Google Sheets mock)
- [ ] Multi-provider LLM routing (currently OpenAI-only)