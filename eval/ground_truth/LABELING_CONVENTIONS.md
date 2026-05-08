# Labeling Conventions for Ground Truth

This document records how I make decisions during hand-labeling so the eval set stays consistent. When a new edge case comes up during labeling, I document the decision here before continuing.

---

## Industries

- **Internships and working student roles count**, when they show in which industries the candidate gathered experience. Rationale: signals profile interest over time, even if the experience was short.
- **Study projects and master's theses do NOT count** toward industries, even if they're thematically in a sector.
- **Multi-sector CVs:** all mentioned industries are counted, even if only a single project happened in a sector.

## Functional Expertise — Liberal with Role Evidence

**Decision: liberal interpretation with role evidence.**

Functional expertise is recorded when the role title or stated responsibilities clearly reflect the function — including in internships, working student roles (Werkstudent), and part-time positions.

**Rationale (customer reality):** In consulting recruiting, even pre-full-time exposure to a function carries signal value for **practice routing** ("Which practice does this candidate fit? Which projects will they be staffed on?"). It's not a mastery claim, it's an interest/exposure signal. Ground truth that strips internship-derived functional expertise would lose information the recruiter needs.

### What counts

- *"Praktikant Strategy"* at Bain → **Strategy** ✓
- *"Werkstudent Risk Analytics"* at Allianz → **Risk Management** ✓
- *"Praktikant M&A"* at Goldman Sachs → **Mergers and Acquisitions** ✓
- Full-time role with responsibilities that clearly match the function → ✓

### What does NOT count

- MBA specializations or fields of study (*"Strategy"* in MBA ≠ Strategy)
- Mentions of related terms (*"regulated takeovers"* ≠ Risk Management)
- Industry knowledge alone (someone who works for banks doesn't automatically have *"Banking"* as functional expertise — that's industry, not functional)
- Study projects, bachelor's theses, or master's theses
- *"Praktikant"* without a functional title and without a clear functional description
- Generic responsibilities that don't map to a canonical taxonomy entry

### Mapping rules

- *"Strategy"* and *"Corporate Strategy"* / *"Growth Strategy"* are counted separately when both are recognizable
- When only generic *"Strategie"* is mentioned → only *"Strategy"*
- The function must map to a canonical taxonomy entry — generic terms (*"Analyst"*, *"Consultant"*) don't qualify

## Career Level (Standard Path)

- **Entry:** 0-2 years full-time experience, recent graduate or first permanent role
- **Mid:** 2-4 years full-time experience
- **Senior:** 5-8 years full-time experience
- **Lead level (8+ years):** out of scope, handled via executive search
- **Internships and working student roles do NOT count** toward years of experience
- **Gaps (parental leave, sabbatical):** also do not count toward years of experience

## Career Level for Career Switchers

Career switchers (e.g., lawyer → consulting) are classified based on **experience in the target profession (consulting)**, not on total work experience.

- 0-2 years consulting experience (regardless of years in other professions) → Entry/Mid (typically Mid with MBA)
- 2-4 years consulting experience → Mid
- 5-8 years consulting experience → Senior

**Rationale:** Recruiters and hiring managers evaluate career level based on relevant functional context, not on total years.

**Important:** `total_years_experience` remains the **total number** (all years, including prior professions). Only `career_level` follows the target-profession logic.

## Total Years Experience

- Calculated from `employment_history`, excluding internships and working student periods, excluding gaps
- For ongoing positions: counted up to today (May 2026)
- **Mathematical rounding** to whole years: 5.4 years → 5; 5.5 years → 6; 8.5 years → 9

## Part-Time and Years of Experience

- Part-time roles count as **calendar time**, not as FTE-equivalent
- **Rationale:** Standard in HR systems; CVs document calendar time. Example: 4 years part-time (80%) count as 4 years, not as 3.2 years

## Employment History

- Internships and working student roles ARE included in `employment_history` (for completeness)
- They do **not** count toward `total_years_experience` and **not** toward career level calculation
- Gaps (parental leave, sabbatical) are NOT listed as employment_history entries — they appear as gaps between entries

## Responsibilities

- Keep brief: 1-3 sentences per position
- Summarize substantive focus areas, don't list every individual task
- For very thin CVs (cv_19): null when no substantial descriptions are available

## Education

- All mentioned credentials are included, including the bachelor's when mentioned
- When multiple credentials: chronological descending (highest/most recent first)
- `field_of_study`: main subject. For specializations, in parentheses, e.g. *"Business Administration, focus Finance"*

## Education Credentials Mapping

- **MBA:** all bachelor-of-business-administration variants and MBAs from any school
- **Executive MBA:** explicitly marked as EMBA
- **Master of Science:** M.Sc. in any subject
- **Diplom:** old German Diplom credentials (Diplom-Kaufmann, Diplom-Wirtschaftsingenieur, Diplom-Volkswirt)
- **Staatsexamen:** First or Second German Legal Bar Exam, German Medical Licensing Exam
- **PhD:** all doctorates (Dr. rer. pol., Dr. rer. nat., Dr. Ing., Doctor of Philosophy)
- **Master of Laws (LL.M.):** explicitly marked as LL.M.

## Industries Mapping

- *"Banking"* and *"Asset Management"* can both be counted when both are mentioned
- *"Pharmaceuticals"* + *"MedTech"* + *"Healthcare"* — counted separately when separately mentioned
- *"Industrial Goods"* covers classical machinery and industrial manufacturing
- *"Automotive"* only explicitly for car manufacturers and suppliers

## Functional Expertise Mapping

- *"M&A"* and *"Mergers and Acquisitions"* → canonical *"Mergers and Acquisitions"*
- *"PMI"* and *"Post-Merger Integration"* → canonical *"Post-Merger Integration"*
- *"Performance Improvement"* covers cost optimization, efficiency programs, restructuring
- *"Digital Transformation"* only when explicitly mentioned — do not derive from *"digital project"*

## Methods Mapping

- *"Lean Six Sigma"* covers both pure Lean and Six Sigma methods, plus all belt levels
- *"Agile"* + *"Scrum"* counted separately when both mentioned
- Generic *"Projektmanagement"* / *"project management"* doesn't map — only concrete frameworks

## Tools Mapping

- *"Excel"* → *"Microsoft Excel"*
- *"PowerPoint"* / *"PPT"* → *"Microsoft PowerPoint"*
- *"think-cell"* exactly as written (with hyphen, lowercase)
- *"Power BI"* with space
- *"R"* only when explicitly mentioned as a tool/language — do not derive from *"R&D"*

## Skill Levels for Tools

- **Skill levels are NOT recorded in v1** (e.g., *"Python (advanced)"* → only *"Python"*)
- **Rationale:** Self-assessments are unreliable (everyone rates themselves differently) and not standardized
- **v2 roadmap:** record levels only when based on standardized credentials (e.g., CEFR for languages, vendor certifications for tools)

## Languages

- Use CEFR level directly when given (e.g., *"C2"* → *"German (C2)"*)
- *"Muttersprache"* / *"Mother tongue"* / *"Native"* → Native
- *"Verhandlungssicher"* / *"business fluent"* → C2
- *"Fließend"* / *"fluent"* → C1
- *"Gut"* / *"good"* → B2
- *"Grundkenntnisse"* / *"basics"* / *"a little [language]"* → don't include or map as unmapped
- **German (B2) and below:** not in v1 taxonomy (persona decision: German consulting firms rarely receive serious applications with German below C1) → map to `unmapped`
- Languages outside the taxonomy (Hindi, Dutch, etc.) → map to `unmapped`

## Certifications

- Free-text, no mapping
- Spell out belt levels: *"Lean Six Sigma Green Belt"* not *"LSS GB"*
- **Only completed certifications** — not *"in preparation"* or *"Candidate"* (e.g., *"CFA Level II Candidate"* does NOT count, *"CFA Level I (passed)"* counts)

## Email, Phone, Location

- **Email:** exactly as in CV, lowercase if ambiguous
- **Phone:** keep CV format (varies internationally)
- **Location:** *"City, Country"* when both given, otherwise city only

## Academic Grades

- **Grades are NOT recorded in v1** (also not *"summa cum laude"*, *"First Class Honours"*, *"Distinction"*, GPA numbers)
- **Rationale:** Grades are coded differently across regions (DE: 1.0-5.0, UK: First/Upper Second, US: 4.0 scale) — normalization is v2 work
- **Documented in README:** for consulting recruiting, grades are a primary filter (top-3 firms screen top decile) — therefore v2 roadmap item

## Date Format

- Preferred **YYYY-MM** (e.g., *"2022-03"*)
- When only year is given in CV: **YYYY** (e.g., *"2022"*)
- For ongoing positions: **end_date = null**
- Month names converted to numbers (*"März"* → *"03"*, *"April"* → *"04"*)

## For Very Thin CVs (e.g., cv_19)

- Fields that cannot be extracted: **null** (for strings) or **empty array []** (for lists)
- `name` is required — if the name is missing, the profile is invalid (schema failure)
- `total_years_experience`: 0 when no experience is identifiable (not null), null when unclear

## For Very Long CVs (e.g., cv_20)

- All mentioned industries / methods / tools are recorded, even if the list grows long
- Employment history: all positions, including older ones
- No consolidation — ground truth is the *complete truth*, not a summary

---

## Change Log of This Document

- **2026-05-07 (initial):** Initial version based on cv_01 labeling
- **2026-05-07 (review pass):** Additions from cv_02-cv_18 review:
  - Functional expertise strict interpretation (cv_15: no hallucinations from related terms)
  - Career switcher convention (View B: experience in target profession counts)
  - Part-time as calendar time
  - Mathematical rounding (8.5 → 9)
  - Skill levels for tools out of scope for v1
  - Academic grades out of scope for v1
  - CFA Candidate excluded, CFA passed included
  - German B2 and below as unmapped
- **2026-05-08 (pipeline run):** Functional expertise changed from strict to liberal interpretation (with role evidence). Rationale: customer use case practice routing — pre-full-time functional exposure is a recruiter signal, not a mastery claim. Surfaced by first end-to-end pipeline run with cv_05.