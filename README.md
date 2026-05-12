# Build 2 — CV-to-Standardized-Profile

🚧 **Work in progress.** Ship target: 13–14 May 2026.

See SCOPE.md for what this build does, what's out of scope, and definition of done.

Architecture, eval results, and ROI math will land here once v1 ships.

## Who this is for

A typical buyer at a German recruiting consultancy or HR-Tech firm processing
3,500+ CVs per month. Decision-makers: VP Operations (cost-saving frame),
CTO (compliance + integration), Head of Recruiting (quality + turnaround).

What they buy: shorter time-to-shortlist + consistent profile structure
across recruiters.

What they object to: data sovereignty (handled in Compliance section),
quality variance (handled in Eval results), integration cost (handled in
Architecture decisions section).

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
- Workflow is the legible artifact — non-engineering stakeholders can read every step
- Enterprise customers with non-engineering buying centers (HR Ops, Procurement, Finance Ops) tend to prefer workflow tools over custom code — lower handover cost between roles, easier audit by non-technical stakeholders.
- Enterprise customers in this space prefer workflow tools over custom code (lower handover cost, easier audit) 
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

### Why DOCX and TXT are deferred to v2 (not in v1)

v1 processes **PDF only** — 11 of 20 eval CVs. The remaining 9 are deferred: 8 DOCX and 1 TXT (cv_19).

**DOCX:** four conversion paths were evaluated:

| Option | Setup | Compliance | Status |
|---|---|---|---|
| OpenAI Responses API native DOCX (Feb 2026) | Medium | US vendor processes file | n8n's OpenAI node currently exposes PDF only as file input |
| AWS Textract Frankfurt | Medium-high | EU data residency, US CLOUD Act applies | Production-ready, v2 candidate |
| AWS European Sovereign Cloud Textract (Jan 2026) | High (enterprise onboarding) | Full EU sovereignty, US CLOUD Act excluded | v3 candidate for regulated industries |
| CloudConvert | Low | US vendor only | Synthetic demo only |

**TXT:** statistically negligible (1 of 20 CVs). Pipeline's Extract-from-File node is PDF-only; TXT support requires either a file-type router (IF-node on mime-type, separate handler for plaintext) or adapting the existing node. Deferred to v2 alongside DOCX as part of the format-expansion phase.

**v1 decision:** ship PDF pipeline (11 of 20 CVs). Defer DOCX and TXT until either (a) n8n exposes DOCX in the OpenAI Responses node, or (b) a customer's compliance tier determines which AWS Textract variant fits, or (c) format-expansion is prioritized over current eval-driven priorities. The DOCX path is a compliance choice, not a technical gap — it should be made when the customer is identified, not pre-empted by v1 defaults.

**Build phasing rationale:** Phase 1 (happy-path end-to-end) ships PDF. Phase 2 (eval against ground truth) measures the existing pipeline's quality. Phase 4 (format expansion) extends to DOCX and TXT with data-driven decisions. Expanding formats before Phase 2 measurement means building on an unmeasured foundation.

**Architecture invariant:** all DOCX paths plug into the existing pipeline at the same point (between the file-type router and the OpenAI extraction node). TXT support requires only an IF-node by mime-type and routing plaintext content directly to the OpenAI extraction node. Adding either format in v2 is additive, not a rebuild.

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

1. **Inbound:** CV file (PDF) via webhook POST to n8n Cloud (hosted by n8n GmbH, Berlin, EU)
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

- [x] Re-review all 20 ground_truth JSONs against updated LABELING_CONVENTIONS — DONE 2026-05-11 (see CONVENTION_DRIFT_REVIEW.md)
- [x] Document convention-drift pattern in FAILURE_LOG — DONE 2026-05-08 (constraint leakage)
- [x] Instrument pipeline (cost, latency, token tracking per LLM call) — DONE 2026-05-12
- [ ] Run full pipeline against eval set — 11 of 20 CVs (PDF only in v1)
- [ ] Compute Field-Level F1 with baseline comparison (zero-shot GPT-4o without schema)
- [ ] BREAK session: adversarial inputs (10-15 stress CVs)

## v2 Architecture Roadmap (eval-driven)

v2 architecture decisions wait on Phase 2 eval results. Three patterns are pre-evaluated; the choice depends on which failure modes Phase 2 surfaces:

| Pattern | Trigger condition | Trade-off |
|---|---|---|
| **B — Multi-stage extraction** | A specific field has sub-F1 below 85% (especially employment_history with project-to-role temporal mapping, education, or taxonomy fields). Failure-isolation matters more than aggregate accuracy. | 3× cost, 3× latency, better failure isolation. Each LLM call has a single clear task. |
| **C — Self-critique loop** | Aggregate F1 acceptable but "confidently wrong" outputs frequent (e.g., LLM derives functional_expertise from MBA specializations despite explicit convention against it). Or: high variance between repeat-runs on same input. | 2× cost, 2× latency, best accuracy on convention violations. More failure-modes (see "Failure-modes vs accuracy" learning note). |
| **Provider A/B test** | Long-CV F1 lower than short-CV F1 by >5pp, OR DACH-language F1 notably weaker than English. Suggests model-capability ceiling rather than prompting issue. | Different cost/latency curve depending on chosen provider. Claude Sonnet 4.6 leads at 97.6% on extraction benchmarks; Gemini 2.5 Pro offers larger context window. |

These patterns are not mutually exclusive — v3 could combine Multi-stage with Self-critique on specific stages. The decision is sequential: Phase 2 surfaces the dominant failure mode, v2 addresses it, Phase 5 re-evaluates.

**What this rules out:** pre-empting v2 architecture before eval data exists. Vendor-marketing-driven decisions ("Claude is more accurate, switch to Claude") without baseline comparison on this specific use case are not architecture decisions — they are guesses.

## Deferred to v2

- [ ] DOCX support — compliance-driven path selection (see Architecture Decisions)
- [ ] TXT support — file-type routing in pipeline
- [ ] Email-trigger for inbound CV files (currently webhook-only)
- [ ] REST-API output to ATS (currently Google Sheets mock)
- [ ] Multi-provider LLM routing (currently OpenAI-only)

## What I'd improve next / Was ich als nächstes verbessern würde

### v2 (next iteration / nächste Iteration)
- **Audited synonym normalization for set-valued fields.** Lookup table 
  built from observed mismatches in v1 eval set (industries, functional_
  expertise, methods, tools). Audit trail per mapping. Deterministic, 
  explainable, but closed-vocabulary.
  *(DE: Auditierte Synonym-Normalisierung für Set-Felder. Lookup-Tabelle 
  aus beobachteten Mismatches im v1-Eval-Set. Audit-Trail pro Mapping. 
  Deterministisch, erklärbar, geschlossenes Vokabular.)*
  
- **DOCX + TXT support.** v1 ships PDF only (11 of 20 CVs). Extension to 
  full corpus via n8n's Extract-from-File node configured for DOCX/TXT.
  *(DE: DOCX- und TXT-Support. v1 nur PDF, Erweiterung auf gesamten Korpus.)*
  
- **Field-level F1 breakdown in eval report.** Per-field scores (currently 
  aggregated) to identify which fields are weakest.
  *(DE: Feld-Level F1 im Eval-Report. Pro-Feld-Scores statt nur Aggregat.)*

### v3 (production hardening / Production-Reife)
- **Embedding-based similarity for open-vocabulary fields.** OpenAI 
  text-embedding-3-small + cosine similarity threshold (~0.85). Handles 
  unseen synonyms without manual table maintenance. Trade-off: extra API 
  call per comparison, non-deterministic, harder to explain in audit.
  *(DE: Embedding-basierte Ähnlichkeit für offene Vokabulare. Behandelt 
  unbekannte Synonyme ohne manuelle Tabellen-Pflege. Trade-off: zusätzlicher 
  API-Call, nicht-deterministisch, schwerer auditierbar.)*
  
- **Sub-field F1 for employment_history and education.** Currently scored 
  by employer/institution name coverage only. v3 evaluates role-title, 
  date-range, and responsibility-extraction accuracy separately.
  *(DE: Sub-Feld-F1 für employment_history und education. Aktuell nur 
  Employer-Name-Coverage. v3 bewertet Rolle, Zeitraum, Verantwortungen separat.)*
  
- **Adversarial test set.** Currently 11 synthetic CVs. v3 adds: heavily 
  formatted PDFs, scanned-image PDFs (OCR path), multi-language CVs, 
  CVs with intentional ambiguities (e.g., gap years, freelance + employed 
  parallel).
  *(DE: Adversariales Test-Set. Aktuell 11 synthetische CVs. v3 ergänzt: 
  stark formatierte PDFs, gescannte Bild-PDFs, mehrsprachige CVs, 
  CVs mit absichtlichen Mehrdeutigkeiten.)*
  
- **Confidence calibration.** Pipeline currently emits no confidence per 
  field. v3 adds per-field confidence with calibration check (does 0.8 
  confidence actually mean ~80% accuracy?).
  *(DE: Confidence-Kalibrierung. Pipeline gibt aktuell keine Confidence 
  pro Feld aus. v3 ergänzt Confidence-Score mit Kalibrierungs-Check.)*