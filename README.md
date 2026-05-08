# Build 2 — CV-to-Standardized-Profile

🚧 **Work in progress.** Ship target: 10–12 May 2026.

See SCOPE.md for what this build does, what's out of scope, and definition of done.

Architecture, eval results, and ROI math will land here once v1 ships.

## Architecture Decisions for v1

### Why n8n instead of custom code
- **Pro:** legible to non-developers (Langdock customer fit)
- **Pro:** every step is visible as a workflow node
- **Con:** less testable than dedicated code
- **v2-trigger:** when validation logic exceeds 50 lines, extract to FastAPI

### Why Google Sheets instead of ATS API
- **v1 reason:** mock for demo without ATS access
- **Production:** replaced by REST-API call to ATS (SAP SuccessFactors, Personio)
- **Architecture impact:** zero — only the last node changes

### Why single LLM provider
- **v1 reason:** structured extraction is one task, one model fit
- **v2-trigger:** when cost dominates Bill or when fallback resilience is needed
