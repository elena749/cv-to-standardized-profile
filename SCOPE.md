# Build 2 — Scope

## CV-to-Standardized-Profile (n8n + LLM)

**Status:** Scope finalized
**Ship target:** ~10–12 May 2026

---

## 1. Customer problem

Recruiting teams in mid-cap and enterprise organizations spend 10–30 minutes per CV manually transcribing candidates into standardized company profiles. At a volume of several thousand CVs per month, that adds up to hundreds of hours of manual work — work that can be automated to 1–2 minutes per CV without compromising data quality.

---

## 2. Customer persona

### Company
- **Industry:** management/strategy consulting
- **Size:** ~3,000 employees
- **Region:** DACH headquarters, international presence
- **Recruiting model:** in-house team. Lead-level hires (8+ years of experience) go through executive search.

### Recruiting team
- **Size:** ~25–40 recruiters
- **Split:** campus recruiting (entry-level) + experienced-hire recruiting (mid to senior level)
- **Tech affinity:** medium — familiar with ATS, no programming background

### Candidate profile
- **Career level:** Entry (graduate), Mid (2–4 years), Senior (5–8 years)
- **Out-of-scope roles:** Lead-level (8+ years, executive search), support functions
- **CV language:** ~70% German, ~30% English
- **Typical profile:** academic (often PhD or MBA), industry experience across multiple sectors, methods toolkit (strategy, operations, digital, M&A, performance improvement)

### Volume — justification
- ~3,000 employees × ~12% attrition/growth = ~400 hires/year
- × ~100 CVs/hire (industry benchmark for top strategy consultancies) = ~40,000 CVs/year
- **CVs per month:** ~3,500 on average, ~6,000–8,000 in seasonal peaks (campus recruiting autumn/spring)
- **Manual processing time:** 10–15 min (experienced recruiters), up to 30 min (junior). Mean ~15–20 min.
- **Current bottleneck:** inconsistent profile formatting across recruiters + delays in seasonal peaks

### ATS / system of record
- **System:** ATS with API access (typical examples: SAP SuccessFactors, Workday, Greenhouse, or in-house solution)
- **In v1:** Google Sheet as a stand-in. Columns map to a typical ATS profile schema. Migration to the ATS API is mechanical — the final pipeline step is replaceable.

### Use case in one sentence
*"Sourcing recruiters at strategy consultancies process 3,500–8,000 CVs/month for consultant roles (entry to senior) and need standardized profiles in their ATS so hiring managers can review candidates comparably across locations and practice areas."*

---

## 3. Why this build is relevant

Three properties make this build relevant to enterprise contexts:

1. **API-accessible target system.** Output writes to an ATS. Without an API-accessible HR system there is no real value created — so this is central.

2. **Data governance built in.** Schema enforcement, controlled vocabulary for skills, and logic validation ensure that only clean, consistent data lands in the target system. Validation happens at write-time, not at read-time — no technical debt for downstream systems.

3. **Prerequisite for HR analytics.** Standardized profiles are a prerequisite for any analysis in Snowflake or comparable data platforms. Free-text CVs are not analyzable; profiles with controlled vocabulary are.

---

## 4. ROI math
3,500 CVs/month × 18 min/CV       = 63,000 min/month
63,000 min ÷ 60                    = 1,050 hours/month
1,050 hours × €70/hr (loaded cost) ≈ €73,500/month
× 12                               ≈ €880,000/year

**Assumptions (defensible):**
- 18 min/CV: midpoint between 10–15 (experienced) and 30 (junior)
- €70/hr: loaded cost (gross salary + employer-side costs + overhead) for mid-level recruiters in Germany
- 3,500 CVs/month: industry benchmark for strategy consultancies with ~3,000 employees

**Seasonal peak effect:** at 6,000–8,000 CVs/month in campus season, savings double — and the bottleneck becomes critical (processing slows, candidates wait too long, top profiles move to competitors).

---

## 5. What v1 does (happy path)
Input  →  Parsing   →  Extraction  →  Validation  →  Output
↓         ↓             ↓               ↓             ↓
PDF      Text          1 LLM call    Schema +       Sheet
DOCX    extraction     → JSON        taxonomy +    (stand-in
TXT     (no LLM!)                    logic         for ATS)

**Components:**

- **Input:** one CV file (PDF, DOCX, or text). German or English.
- **Parsing:** text extraction with `pdf-parse` (PDF) and `mammoth` (DOCX). No LLM. Deterministic and low-cost.
- **Extraction:** one LLM call with schema (Structured Outputs). Fields:
  - `name`
  - `current_role`
  - `total_years_experience`
  - `career_level` (Entry / Mid / Senior)
  - `employment_history` (array: employer, role, start, end, responsibilities)
  - `education` (array)
  - `industries` (array, mapped to taxonomy)
  - `functional_expertise` (array, mapped to taxonomy)
  - `methods_and_tools` (array, mapped to taxonomy)
  - `languages` (array with proficiency)
- **Validation:** code-based.
  - Schema check (all required fields present, types correct)
  - Taxonomy mapping (map or mark as `unmapped`)
  - Logic checks (date plausibility, no impossible overlaps in employment history, total years vs. sum of stations)
- **Output:** JSON written to Google Sheet, stand-in for ATS API.

**Latency target:** <2 min per CV (end-to-end).

---

## 6. Out of scope for v1

Scope discipline is part of the build. The following aspects are deliberately excluded and documented in the v2 roadmap:

- **Multi-page PDF layout parsing.** Tables, columns, embedded images are ignored. Exotic layouts → parsing failure → entry in the failure log.
- **Skill/expertise inference from job descriptions.** *"Senior Strategy Consultant in Pharma"* does not automatically trigger *"Pharma industry + strategy method"* — only explicitly named industries and methods are extracted.
- **Photo / profile-image extraction.** Candidate photo on the CV is ignored.
- **OCR on scanned PDFs.** Scanned CV → parsing failure.
- **Multi-language mixing within a single CV.** One language per CV in v1.
- **Lead-level profiles (8+ years).** Handled via executive search, not via this workflow.
- **No UI.** Input via n8n trigger folder or webhook. Output via sheet row.
- **No anonymization / GDPR pseudonymization.** Synthetic CVs in the eval phase. Real data only in v2 with the appropriate setup.

---

## 7. Definition of done for v1

A Build 2 v1 is done when all 7 boxes are checked:

1. ☐ A CV file (PDF, DOCX, text, DE or EN) is transformed into a validated sheet row in <2 min.
2. ☐ Schema is hard-specified (JSON schema committed in the repo).
3. ☐ Taxonomy exists (industries, functional expertise, methods/tools, languages — committed in YAML).
4. ☐ Eval set exists: 20 hand-labeled CVs, ground-truth profiles as JSON, committed.
5. ☐ Eval script runs and produces a number (field-level F1 or exact-match rate per field category).
6. ☐ **Baseline measured:** zero-shot LLM without schema enforcement, without taxonomy. In the README.
7. ☐ **Pipeline number measured:** full pipeline. In the README. Beats baseline.

---

## 8. Quality markers

Three standards the build must meet before it's considered "done":

### Numerical evaluation
- Held-out test set (20 CVs)
- Baseline number (zero-shot LLM without pipeline)
- Pipeline number (full stack)
- Failure taxonomy in FAILURE_LOG

### Generalizing FAILURE_LOG entries
At least one entry per build that doesn't describe the specific bug, but the class of failures it generalizes.

### ROI transparency in README
Concrete math with traceable assumptions — not *"saves time"*, but volume × time per CV × hourly rate = monthly value. Assumptions explicit and defensible.

---

## 9. Per-build discipline

1. ✅ **SCOPE** — this document
2. ☐ **BUILD v1** — hygiene only: input validation, schema enforcement, basic retries. Happy path first.
3. ☐ **INSTRUMENT** — log every LLM call: input, output, latency, token count, cost.
4. ☐ **BREAK** — red-team session with adversarial inputs:
   - Ambiguous CVs (missing dates, freelance tangles)
   - Long CVs (context limit)
   - Empty/malformed files, Unicode, mixed languages
   - Prompt injection in CV text
   - API failures (timeouts, rate limits)
   - Confidently wrong outputs (invented industries/expertise)
5. ☐ **EVAL** — score output against ground truth.
6. ☐ **v2 + MITIGATIONS** — per break: fix, mitigate, or accept-and-document.
7. ☐ **COST & LATENCY** — cost per 1,000 runs, p50/p95 latency.
8. ☐ **SECURITY/GOVERNANCE NOTE** — what flows where, what is stored, GDPR concerns, mitigations.
9. ☐ **SHIP** — README, FAILURE_LOG, CHANGELOG, eval results, Loom demo.

---

## 10. Concrete next action

**Build the taxonomy.** YAML file, organized into categories that fit the consulting persona:

- `industries` (FinServ, Pharma, FMCG, Energy, Public Sector, Telco, Automotive, Retail, etc.)
- `functional_expertise` (Strategy, Operations, M&A, Digital Transformation, Performance Improvement, Org Design, etc.)
- `methods` (Lean Six Sigma, Design Thinking, Agile, Change Management, etc.)
- `tools` (Excel, PowerPoint, Tableau, Power BI, Alteryx, etc.)
- `languages` (with proficiency levels)
- `education_credentials` (MBA, PhD, etc.)

Commit as `taxonomy/taxonomy.yaml`. ~30–60 min of work.

**Sequence after that:**

1. Define the schema (references the taxonomy)
2. Build the eval set (20 hand-labeled CVs as ground truth)
3. Build the pipeline (n8n workflow)
4. Measure baseline (zero-shot)
5. Measure pipeline (full stack)
6. Iterate

