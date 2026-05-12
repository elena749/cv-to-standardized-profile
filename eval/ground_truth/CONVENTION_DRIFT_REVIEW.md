# Convention-Drift Re-Review (2026-05-11, second pass 2026-05-12)

Re-review of all 20 ground-truth JSONs against the updated `LABELING_CONVENTIONS.md` (functional_expertise changed from STRICT → LIBERAL with role evidence on 2026-05-08).

**Scope per CV:**
- **Drift check** (already reviewed under strict): cv_01 (example), cv_02, cv_03, cv_04, cv_05, cv_07, cv_09, cv_10, cv_11, cv_12, cv_14, cv_15, cv_16, cv_17, cv_18
- **Full review** (not previously reviewed): cv_06, cv_08, cv_13, cv_19, cv_20

**Convention applied (Functional Expertise — Liberal):**
- Internship / Werkstudent titles with clear functional names → COUNT
- Responsibilities that clearly map to a canonical function → COUNT
- MBA specializations, study projects, theses → DO NOT count
- Industry knowledge alone → DOES NOT count (industry ≠ functional)
- Generic "Praktikant" / "Consultant" without functional descriptor → DOES NOT count
- Must map to canonical taxonomy entry

Risk legend: **high** = change affects core label set; **low** = additive change with clear evidence; **none** = no change recommended.

---

## Liberal-Convention Adds Found in Second Pass

**Result: zero new additions across the 12 "no change" CVs.**

Targeted re-check of cv_03, cv_04, cv_11, cv_14, cv_15, cv_16, cv_17 (and the remaining "no change" set: cv_01, cv_05, cv_07, cv_19, cv_20) for any Praktikant / Werkstudent / early-career roles whose functional title or stated responsibilities should add a functional_expertise entry under the liberal convention.

| CV | Pre-full-time roles present | Liberal-eligible add? | Why |
|---|---|---|---|
| cv_01 (example) | "Praktikant Strategie" @ Roland Berger | No | Strategy already present |
| cv_03 | None — career starts as full-time Consultant @ McKinsey 2011-09 | No | No internship/Werkstudent roles in CV |
| cv_04 | None — career starts as full-time Associate @ McKinsey London 2017-09 | No | No internship/Werkstudent roles in CV |
| cv_05 | "Praktikant Strategy" Bain, "Werkstudent Risk" Allianz GI, "Praktikant Investment Banking / M&A team" Goldman | No | All three already mapped (Strategy, Risk Management, M&A) |
| cv_07 | None — career starts as full-time Analyst @ Deloitte London 2017-08 | No | No internship/Werkstudent roles in CV |
| cv_11 | "Junior Consultant" @ KPMG Strategy 2018-04 (full-time, not internship) | No | Generic "Junior Consultant" title, null responsibilities. Employer name "KPMG Strategy" is the practice, but the convention requires title or responsibilities, not employer name. Strategy is already present anyway. |
| cv_14 | "Associate" @ Bain London 2013-09 (full-time, not internship), null responsibilities | No | Generic "Associate" title, null responsibilities. Liberal does not promote pure title-implication without a functional descriptor. |
| cv_15 | "Wissenschaftlicher Mitarbeiter" @ Uni Köln 2016-10 (full-time research, not internship), null responsibilities | No | Research-staff role, no consulting function descriptor; "kartellrechtliche Verfahren" at Hengeler Mueller is legal-domain antitrust, not a canonical functional taxonomy entry. |
| cv_16 | "Praktikant" @ BCG 2013-04 — generic title, null responsibilities | No | Convention explicitly excludes generic "Praktikant" without a functional descriptor or clear functional description. |
| cv_17 | "Analyst" @ BNP Paribas Investment Banking 2017-09 (full-time, not internship) | No | Responsibility "M&A advisory primarily for industrial goods and consumer goods clients" → M&A. Already present. |
| cv_19 | "Praktikant Marketing" 3mo, "Praktikant" Steuerbüro 2mo | No | Marketing and Sales already present from the first; second has no functional descriptor. |
| cv_20 | "Research Assistant" @ LSE 2010-09 (PhD period) | No | PhD research, not a consulting role; "PhD research on banking regulation and systemic risk" — Risk Management would be a stretch since this is dissertation/academic work, not operational. Convention excludes theses and PhD research. |

### Summary

The first pass was complete on these CVs. The reason no adds were found:

1. **Most senior CVs do not list internships at all** — cv_03, cv_04, cv_07, cv_14, cv_20 jump straight to full-time consulting/IB roles. The liberal convention applies to a population (early-career CVs) that simply isn't present in these records.
2. **Where pre-full-time roles exist with functional descriptors** (cv_01, cv_05, cv_19), the corresponding labels were already in the GT. The original labelers were not strict about excluding internship-derived expertise — they were strict about *interpreting it correctly*. The drift change matched their existing practice for cv_05; the only case where they were strictly conservative was cv_02 (caught in the first pass).
3. **The genuinely generic / null-responsibility cases** (cv_11 KPMG Junior Consultant, cv_14 first Bain Associate, cv_16 BCG Praktikant, cv_15 Wiss. Mitarbeiter) correctly receive nothing — the convention requires title *or* responsibilities to clearly reflect a function.

**Net effect of the liberal drift on the eval set:** still **+1 entry across 20 CVs** (cv_02 Strategy). The convention change is real and correct, but the pre-existing labels were closer to "liberal" than "strict" in spirit. The four removals from the first pass remain the higher-impact action items.

---

## Action Summary

### functional_expertise — changes recommended (5 CVs)

| CV | Change | Direction | Reason |
|---|---|---|---|
| cv_02 | **+ Strategy** | ADD (drift, liberal) | "Praktikant Strategy" at Simon-Kucher matches canonical liberal example |
| cv_08 | **− Digital Transformation** | REMOVE (strict) | Derived only from "Transformationsprojekte Telekom" — convention forbids |
| cv_09 | **− Supply Chain** | REMOVE (strict) | Only supported by MSc specialization "nachhaltige Lieferketten" |
| cv_10 | **− Innovation** | REMOVE (strict) | Only supported by MSc specialization, no role evidence |
| cv_13 | **− Growth Strategy** | REMOVE (strict) | No role evidence; only PhD dissertation theme + ambiguous "neue Geschäftsmodelle" |

**Direction interpretation:** Only **one** functional_expertise change (cv_02) comes from the 2026-05-08 liberal drift itself. The other four are pre-existing strict-convention violations that surfaced when re-reading every label against the convention. None require *new* convention work.

### functional_expertise — borderline / no action recommended (3 CVs)

| CV | Borderline label | Note |
|---|---|---|
| cv_12 | Strategy | Only Pricing-Strategie + Wachstumsstrategie present; generic Strategy has no standalone evidence. Status quo holds. |
| cv_17 | Organization Design, Growth Strategy | No explicit role evidence; "market entry strategy" → Growth Strategy is a stretch. Status quo holds. |
| cv_18 | Operations | "Operating model redesign" is more naturally Organization Design; Operations is duplicative. Status quo holds. |

### Other fields — issues surfaced during full review (2 CVs)

| CV | Field | Current | Suggested | Reason |
|---|---|---|---|---|
| cv_06 | total_years_experience | 5 | **6** | 2020-09 → 2026-05 = 5.67 yr → mathematical rounding to 6 (same pattern as cv_11/cv_12) |
| cv_08 | total_years_experience | 11 | **12** | 2014-10 → 2026-05 = 11.58 yr → mathematical rounding to 12 |

career_level for both stays "Senior".

### CVs with no recommended change (12)

cv_01 (example), cv_03, cv_04, cv_05, cv_07, cv_11, cv_14, cv_15, cv_16, cv_19, cv_20, plus cv_12/cv_17/cv_18 if borderline flags are not acted on.

### Patterns observed

1. **The liberal drift had small impact on the label set.** Only cv_02 gets a strictly new label (Strategy) from the convention change. The hand-labeled corpus was already largely conservative about internship-derived expertise — the inverse direction (over-including from internships) was not the failure mode.
2. **Pre-existing strict-convention violations are the bigger finding.** cv_08, cv_09, cv_10, cv_13 each have one label derived from MBA specializations, dissertation themes, or related-but-not-mapped terms — the exact failure pattern cv_15 surfaced and the strict review caught only there. This re-review is the first time these survived-strict-but-shouldn't-have cases are audited together.
3. **Date math is the second recurring failure** (cv_06, cv_08 here; previously cv_11, cv_12). Suggest treating as a known pattern in the labeling workflow.

---

## cv_01 — Lukas Hoffmann (Senior Consultant, Strategy&, DE) [EXAMPLE]

**Current functional_expertise:** Strategy, Mergers and Acquisitions, Growth Strategy, Performance Improvement
**Recommended (liberal):** Strategy, Mergers and Acquisitions, Growth Strategy, Performance Improvement
**Reason:** No change. All four supported by full-time role responsibilities (Strategy/Pharma, M&A due diligence, "Wachstumsstrategien", Performance-Improvement Automotive). The "Praktikant Strategie" at Roland Berger only reinforces Strategy, which is already present.
**Risk:** none

---

## cv_02 — Sophie Werner (Entry / pre-graduate, Berlin, DE)

**Current functional_expertise:** Pricing, Operations, Marketing and Sales
**Recommended (liberal):** Strategy, Pricing, Operations, Marketing and Sales
**Reason:** Add **Strategy** — "Praktikant Strategy" at Simon-Kucher matches the canonical liberal example verbatim. Pricing remains via the Pricing-Projekte responsibility; Operations via "Praktikant Operations" title; Marketing and Sales via "Werkstudent Marketing" title.
**Risk:** low (clear title match, additive only)

---

## cv_03 — Dr. Andreas Vogel (Senior Manager, Roland Berger, DE)

**Current functional_expertise:** Mergers and Acquisitions, Sustainability, Strategy, Performance Improvement, Post-Merger Integration
**Recommended (liberal):** Mergers and Acquisitions, Sustainability, Strategy, Performance Improvement, Post-Merger Integration
**Reason:** No change. All five supported by full-time role responsibilities (M&A Energy >500M, Sustainability Practice build-up, Strategie/Performance-Improvement Energy, PMI DAX-Konzern, Performance-Improvement Automotive). No internships in this CV.
**Risk:** none

---

## cv_04 — Marcus Bennett (Engagement Manager, Bain, EN)

**Current functional_expertise:** Post-Merger Integration, Strategy, Digital Transformation, Organization Design, Performance Improvement
**Recommended (liberal):** Post-Merger Integration, Strategy, Digital Transformation, Organization Design, Performance Improvement
**Reason:** No change. All five derive from full-time roles with explicit responsibilities (PMI/financial services, banking strategy, digital transformation insurance, organization design in integration roadmaps, performance improvement asset management). MBA "Finance and Strategy" specialization correctly excluded.
**Risk:** none

---

## cv_05 — Mira Schulz (Entry / pre-graduate, Frankfurt, DE) [PIPELINE-RUN CASE]

**Current functional_expertise:** Strategy, Risk Management, Mergers and Acquisitions
**Recommended (liberal):** Strategy, Risk Management, Mergers and Acquisitions
**Reason:** No change. This is the CV that triggered the convention change; current labels are already aligned with the new liberal convention. "Praktikant Strategy" (Bain) → Strategy; "Werkstudent Risk" (Allianz GI) → Risk Management; "Praktikant Investment Banking" at Goldman with stated work "im M&A-Team" → Mergers and Acquisitions (responsibility-based evidence under liberal convention).
**Risk:** none

---

## cv_06 — Julia Brandt (Consultant, Horváth & Partners, DE) [FULL REVIEW]

**Current functional_expertise:** Performance Improvement, Operations, Strategy
**Recommended (liberal):** Performance Improvement, Operations, Strategy
**Reason for change (or no change):** No change to functional_expertise. Performance Improvement and Operations are clear from the two Horváth roles. **Strategy is borderline** — the BCG internship title is generic "Praktikant" (no functional descriptor), but the stated responsibility is "Strategieprojekt im Konsumgüterbereich", which counts as "stated responsibilities clearly reflect the function" under the liberal convention. Marginal but defensible.
**Risk (functional_expertise):** none

**Additional full-review findings (flag for verification):**
- `total_years_experience`: currently **5**. Calendar math: 2020-09 → 2026-05 = 5 years 8 months ≈ 5.67 years → mathematical rounding to **6**. Suggest 5 → 6 (same date-math pattern as cv_11/cv_12).
- `career_level`: "Senior" — still correct (5-8 years → Senior), whether years is 5 or 6.
- Other fields (industries, methods, tools, languages, certifications) verified against CV — no change.

---

## cv_07 — Olivia Carter (Senior Associate, Oliver Wyman, EN)

**Current functional_expertise:** Strategy, Digital Transformation, Risk Management, Performance Improvement, Organization Design
**Recommended (liberal):** Strategy, Digital Transformation, Risk Management, Performance Improvement, Organization Design
**Reason:** No change. All five derive from full-time role responsibilities (insurance strategy, digital transformation engagement, risk management projects, operating model assessments → Organization Design). **Performance Improvement is borderline** — derived from Deloitte's "process redesign and operating model assessments" / "Banking transformation"; this is the kind of inference that the strict convention flagged, but was kept under previous review. The liberal convention does not loosen this further. Status quo holds.
**Risk:** none

---

## cv_08 — Stefan Klein (Manager, A.T. Kearney, DE) [FULL REVIEW]

**Current functional_expertise:** Supply Chain, Operations, Performance Improvement, Procurement, Strategy, Digital Transformation
**Recommended (liberal):** Supply Chain, Operations, Performance Improvement, Procurement, Strategy
**Reason:** **Remove "Digital Transformation"**. The only evidence is BCG Consultant role's "Strategie- und Transformationsprojekte im Telekommunikationssektor". Convention mapping explicitly states *"Digital Transformation only when explicitly mentioned — do not derive from 'digital project'"* — and bare "Transformationsprojekte" is even weaker. This is the same hallucination pattern that cv_15's strict review caught for "Risk Management". The MBA specialization "Strategy and Innovation" does NOT count under either convention, but Strategy is independently supported by the BCG Consultant role.
**Risk (functional_expertise):** low (removal of unsupported entry; not a drift issue per se but surfaced during full review)

**Additional full-review findings (flag for verification):**
- `total_years_experience`: currently **11**. Calendar math: 2014-10 → 2026-05 = 11 years 7 months ≈ 11.58 → mathematical rounding to **12**. Suggest 11 → 12.
- `career_level`: "Senior" — keeps consistent with cv_03 (14 years → Senior) and cv_17 (9 → Senior); Lead is out of scope per convention.
- BCG "Praktikant" (2013-04 → 2013-09) has no functional title and no responsibilities recorded → correctly does NOT contribute to functional_expertise.
- Other fields verified — no change.

---

## cv_09 — Pia Neumann (Entry / pre-graduate, München, DE)

**Current functional_expertise:** Sustainability, Operations, Supply Chain, Strategy
**Recommended (liberal):** Sustainability, Operations, Strategy
**Reason:** **Remove "Supply Chain"**. Under liberal, the internship/Werkstudent titles each contribute one function: Praktikant Sustainability (BCG) → Sustainability; Werkstudent Operations (Siemens) → Operations; Praktikant Strategie (Roland Berger) → Strategy. **Supply Chain is not supported by any role title or stated responsibility** — its only evidence is the MSc specialization *"Sustainability and Operations Management, Schwerpunkt Kreislaufwirtschaft und nachhaltige Lieferketten"*, which the convention excludes ("MBA specializations or fields of study ≠ functional expertise"). The Siemens Werkstudent description is "Lean Manufacturing / Wertstromanalysen" — that's Operations, not Supply Chain.
**Risk:** low (removal of MBA-specialization-derived entry; same pattern as cv_15)

---

## cv_10 — Daniel Foster (Entry / pre-graduate, Berlin, EN)

**Current functional_expertise:** Digital Transformation, Strategy, Innovation
**Recommended (liberal):** Digital Transformation, Strategy
**Reason:** **Remove "Innovation"**. Digital Transformation is supported under liberal: McKinsey "Summer Associate Intern" title is generic, but the responsibility ("digital transformation project for a mid-sized industrial goods company") clearly reflects the function. Strategy is supported by "Working Student Strategy" at Mercedes-Benz. **Innovation has no role-evidence**: it appears only in the MSc specialization "Digital Transformation and Innovation" — MBA-style specialization, excluded by convention. The "TUM AI Society" activity is not a role with Innovation responsibilities.
**Risk:** low (removal of specialization-derived entry)

---

## cv_11 — Tobias Engel (Senior Consultant, Strategy&, DE, table layout)

**Current functional_expertise:** Mergers and Acquisitions, Performance Improvement, Digital Transformation, Strategy
**Recommended (liberal):** Mergers and Acquisitions, Performance Improvement, Digital Transformation, Strategy
**Reason:** No change. All four supported by explicitly named projects under full-time roles (M&A Auto, Performance Improvement Telecom, Digital Transformation Industrie — *explicit* DT project name, satisfying the strict mapping rule, Strategie-Review Konsumgüter). The KPMG Strategy "Junior Consultant" role has no responsibilities recorded but Strategy is independently supported.
**Risk:** none

---

## cv_12 — Anna-Lena Wolff (Consultant, Bain, DE, table layout)

**Current functional_expertise:** Pricing, Growth Strategy, Digital Transformation, Strategy
**Recommended (liberal):** Pricing, Growth Strategy, Digital Transformation, Strategy (borderline)
**Reason:** No change recommended, but flag **"Strategy"** as **borderline**. Pricing (FMCG Pricing-Strategie) ✓, Growth Strategy (Wachstumsstrategie Pharma) ✓, Digital Transformation (explicit "Digital Transformation Banking" project name) ✓. Generic "Strategy" has no standalone project — only specific Pricing/Growth/DT projects, plus the "Praktikum & Werkstudent" role (generic title, null responsibilities → does NOT count). Per mapping rule *"When only generic 'Strategie' is mentioned → only Strategy"* — the inverse also applies: when only *specific* strategy variants are mentioned, generic Strategy is not separately warranted. Could be argued either way; previous reviewer kept it; the liberal change does not require removal.
**Risk:** borderline (if tightening, remove Strategy; if status quo, no change)

---

## cv_13 — Dr. Christine Bauer (Senior Manager, Bain, DE) [FULL REVIEW]

**Current functional_expertise:** Strategy, Mergers and Acquisitions, Performance Improvement, Sustainability, Growth Strategy
**Recommended (liberal):** Strategy, Mergers and Acquisitions, Performance Improvement, Sustainability
**Reason:** **Remove "Growth Strategy"**. Strategy (Strategieprojekte in Senior Manager role) ✓; M&A (Manager + Senior Consultant roles) ✓; Performance Improvement (Senior Consultant) ✓; Sustainability (Co-Lead Sustainability-Initiative at Senior Manager) ✓. **Growth Strategy has no role-evidence** — there is no project or responsibility describing growth strategy work. The closest text is "Entwicklung neuer Geschäftsmodelle für Omnichannel-Strategien" (new business models for omnichannel) which is closer to Innovation or generic Strategy, not Growth Strategy. The PhD dissertation theme *"Strategische Erneuerung in reifen Konsumgütermärkten"* does not count (dissertation, not role). Same hallucination pattern as cv_15's removed entries.
**Risk (functional_expertise):** low (removal of unsupported entry)

**Additional full-review findings (flag for verification):**
- `total_years_experience`: 13 — math 2013-04 → 2026-05 = 13 years 1 month ≈ 13.08 → 13 ✓
- `career_level`: Senior ✓
- McKinsey "Consultant" role 2013-04 → 2015-08 has null responsibilities → correctly does not contribute.
- Other fields verified — no change.

---

## cv_14 — Rachel Thompson (Manager, McKinsey, EN, modern PDF)

**Current functional_expertise:** Post-Merger Integration, Mergers and Acquisitions, Strategy, Digital Transformation, Performance Improvement
**Recommended (liberal):** Post-Merger Integration, Mergers and Acquisitions, Strategy, Digital Transformation, Performance Improvement
**Reason:** No change. All five derive from full-time roles with explicit responsibilities (PMI pharma/medtech, M&A diligence healthcare/consumer + PE diligence at Bain, Strategy refresh pharma, digital transformation engagement insurance, performance improvement retail/consumer). MBA "general management focus" does not contribute, but every label is independently supported.
**Risk:** none

---

## cv_15 — Markus Reinhardt (Career switcher, DE, edge case)

**Current functional_expertise:** Mergers and Acquisitions
**Recommended (liberal):** Mergers and Acquisitions
**Reason:** No change. Previous strict review correctly removed Strategy (MBA specialization) and Risk Management ("regulated takeovers" ≠ Risk Management). M&A is the only label supported by full-time role responsibilities ("M&A-Transaktionen" at Freshfields, "Unternehmenstransaktionen" at Hengeler Mueller). The liberal convention does not affect this CV: no internship/Werkstudent titles to liberalize, and the MBA at IESE remains excluded.
**Risk:** none

---

## cv_16 — Katharina Maier (Senior with gaps, DE, edge case)

**Current functional_expertise:** Operations, Supply Chain, Performance Improvement, Strategy, Mergers and Acquisitions
**Recommended (liberal):** Operations, Supply Chain, Performance Improvement, Strategy, Mergers and Acquisitions
**Reason:** No change. All five derive from full-time Roland Berger roles with explicit responsibilities (Operations + Supply Chain in current Teilzeit role; Performance Improvement + Operations at earlier Consultant; Strategie- und Operations- + M&A workstreams at 2018 Senior Consultant). BCG "Praktikant" (2013, no responsibilities) correctly does not contribute.
**Risk:** none

---

## cv_17 — Alexandre Dubois (Multi-sector, EN, edge case)

**Current functional_expertise:** Strategy, Operations, Digital Transformation, Performance Improvement, Mergers and Acquisitions, Pricing, Procurement, Organization Design, Growth Strategy
**Recommended (liberal):** Strategy, Operations, Digital Transformation, Performance Improvement, Mergers and Acquisitions, Pricing, Procurement *(Organization Design and Growth Strategy borderline)*
**Reason:** Seven labels are cleanly supported by explicit project lines (Banking DT, Pharma market entry → Strategy, Industrial PI, Telecom Pricing, Defense procurement, Insurance claims redesign → Operations, BNP M&A advisory). **Organization Design** is questionable — no explicit "operating model" or "org design" project; closest is "claims process redesign" which is Operations. **Growth Strategy** is questionable — "market entry strategy" for biotech could be argued as Growth Strategy but is not labeled that way in the CV. MBA INSEAD "Strategy" specialization does NOT count. Both entries pre-date the drift change; the liberal change does not require their removal, but they would not be added under a strict re-read either.
**Risk:** borderline (both flagged entries; tightening, not drift)

---

## cv_18 — Aarav Mehta (International, EN, edge case)

**Current functional_expertise:** Strategy, Growth Strategy, Digital Transformation, Operations, Post-Merger Integration, Mergers and Acquisitions, Organization Design
**Recommended (liberal):** Strategy, Growth Strategy, Digital Transformation, Operations, Post-Merger Integration, Mergers and Acquisitions, Organization Design
**Reason:** No change. Strategy + Growth Strategy ("Growth strategy for a leading Indian retail conglomerate") ✓, Digital Transformation (US healthcare DT) ✓, M&A + PMI ("M&A integration for a software company acquisition, USD 1.5B" → both M&A and the integration component) ✓, Organization Design ("Operating model redesign for a Southeast Asian telecom operator" — operating model maps to Organization Design per cv_04/cv_07 precedent). **Operations is borderline** — no explicit Operations project; "operating model redesign" is more naturally Organization Design than Operations. Previous strict review kept it; liberal does not affect. MBA Wharton "Strategy and Finance" specialization does NOT count, but Strategy is independently supported.
**Risk:** none (Operations borderline but pre-existing)

---

## cv_19 — Tim Becker (Very thin CV, DE, breaking case) [FULL REVIEW]

**Current functional_expertise:** Marketing and Sales
**Recommended (liberal):** Marketing and Sales
**Reason for change (or no change):** No change. "Praktikum im Marketing-Bereich" (3 months at startup) gives clear functional descriptor → Marketing and Sales under the liberal convention. The 2-month Steuerbüro internship has no functional descriptor ("2 Monate Praktikum") → correctly does NOT contribute.
**Risk (functional_expertise):** none

**Additional full-review findings:**
- All other fields verified against the very thin CV: name/location ✓; email/phone null ✓; total_years 0 + career_level Entry ✓; industries [] ✓ (none named); methods/tools/certifications [] ✓; languages ["German (Native)", "unmapped"] correctly handles "ein bisschen Englisch" per the "basics → unmapped" rule.
- Note: employment_history entries use placeholder employer names ("unbenannt (Startup)", "unbenanntes Steuerbüro") with null dates — consistent with the thin-CV convention; no change suggested.

---

## cv_20 — Dr. Patricia Wells (Very long, EN, breaking case) [FULL REVIEW]

**Current functional_expertise:** Strategy, Mergers and Acquisitions, Digital Transformation, Post-Merger Integration, Performance Improvement, Organization Design, Growth Strategy, Pricing
**Recommended (liberal):** Strategy, Mergers and Acquisitions, Digital Transformation, Post-Merger Integration, Performance Improvement, Organization Design, Growth Strategy, Pricing
**Reason for change (or no change):** No change. Every entry is supported by an explicit project line in a full-time role: Strategy (pharma strategy refresh, multiple), M&A (Banking M&A diligence), Digital Transformation (banking DT, insurance DT), PMI (healthcare hospital consolidation, "Designed the integrated organization, EUR 250M synergies, Day 365"), Performance Improvement (UK retail bank PI, "GBP 180M annual savings"), Organization Design (insurance operating model redesign, future-state operating model banking, integrated organization design healthcare), Growth Strategy ("Growth strategy for a global FMCG company"; "three priority growth areas" pharma), Pricing ("Retail pricing strategy for a leading UK supermarket chain"). All eight cleanly traceable.
**Risk (functional_expertise):** none

**Additional full-review findings:**
- `total_years_experience`: 12 — math 2014-08 → 2026-05 = 11 years 9 months ≈ 11.75 → 12 ✓. LSE Research Assistant 2010-09 → 2014-06 is the PhD period and is correctly excluded from total_years (although it appears in employment_history for completeness, which is a borderline call — convention allows it since the role lists real output: "co-authored three peer-reviewed publications").
- `career_level`: Senior ✓ (consistent with cv_03/cv_08/cv_17 — Lead is out of scope per convention).
- `industries`: 9 entries (Pharmaceuticals, Banking, Healthcare, Insurance, Financial Services, Asset Management, Private Equity, Consumer Goods, Retail) — all explicitly named in CV; no double-counting. UK-only/Germany-only project sub-sectors not added separately.
- `methods` / `tools` / `languages` / `certifications` verified — no change.
- Note: tools list correctly strips skill-level qualifiers ("Microsoft Excel (advanced)" → "Microsoft Excel"; "Python (advanced)" → "Python"; "R (intermediate)" → "R") per the v1 convention.

---

