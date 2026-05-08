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