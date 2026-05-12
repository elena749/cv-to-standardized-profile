# CV-to-Standardized-Profile — v1 Evaluation Report

**Run:** `v1_2026-05-12` | **N CVs:** 11 | **Scope:** PDF only; DOCX/TXT deferred to v2

## TL;DR

- **Overall macro F1 (raw):** 0.80
- **Overall macro F1 (normalized):** 0.86
- Normalized score reflects format-tolerant matching on `certifications` and `languages`. See [Methodology Notes](#methodology-notes) below.

## Aggregate Field Performance

Sorted by F1 ascending (weakest first).

| Field | Type | F1 | Precision | Recall | Notes |
|---|---|---|---|---|---|
| `total_years_experience` | integer | 0.00 | — | — | LLM date arithmetic unreliable; see Failure Modes |
| `career_level` | string | 0.82 | — | — |  |
| `functional_expertise` | set | 0.86 | 1.00 | 0.79 |  |
| `industries` | set | 0.88 | 1.00 | 0.80 |  |
| `current_role` | string | 0.91 | — | — |  |
| `certifications` | set | 0.94 (raw: 0.24) | 0.95 (raw: 0.27) | 0.95 (raw: 0.23) | Format-tolerant matching active |
| `education` | list | 0.95 | — | — | Employer/institution coverage only (v1) |
| `methods` | set | 0.97 | 1.00 | 0.95 |  |
| `languages` | set | 0.99 (raw: 0.99) | 0.98 (raw: 0.98) | 1.00 (raw: 1.00) | Format-tolerant matching active |
| `name` | string | 1.00 | — | — |  |
| `tools` | set | 1.00 | 1.00 | 1.00 |  |
| `employment_history` | list | 1.00 | — | — | Employer/institution coverage only (v1) |

## Per-CV Performance

Sorted by overall F1 ascending. Notable failures: string/integer fields with score 0, or set fields with F1 < 0.7 (normalized where applicable); capped at 3 per CV.

| CV | Overall F1 | Set F1 | List F1 | String F1 | Notable failures |
|---|---|---|---|---|---|
| `cv_12` | 0.76 | 0.85 | 1.00 | 0.50 | `career_level`, `total_years_experience`, `certifications` |
| `cv_20` | 0.80 | 0.93 | 1.00 | 0.50 | `current_role`, `total_years_experience`, `functional_expertise` |
| `cv_06` | 0.83 | 1.00 | 1.00 | 0.50 | `career_level`, `total_years_experience` |
| `cv_17` | 0.84 | 0.92 | 0.75 | 0.75 | `total_years_experience`, `functional_expertise` |
| `cv_11` | 0.85 | 0.87 | 1.00 | 0.75 | `total_years_experience`, `certifications` |
| `cv_07` | 0.88 | 0.92 | 1.00 | 0.75 | `total_years_experience` |
| `cv_10` | 0.88 | 0.93 | 1.00 | 0.75 | `total_years_experience`, `industries` |
| `cv_16` | 0.90 | 0.96 | 1.00 | 0.75 | `total_years_experience` |
| `cv_03` | 0.90 | 0.98 | 1.00 | 0.75 | `total_years_experience` |
| `cv_05` | 0.90 | 0.98 | 1.00 | 0.75 | `total_years_experience` |
| `cv_14` | 0.92 | 1.00 | 1.00 | 0.75 | `total_years_experience` |

## Failure Modes

### Missing Extractions

- **`total_years_experience`** (2 CVs): `cv_05`, `cv_10`
  - Pipeline emits a value in most cases but LLM date arithmetic over employment ranges is unreliable. Deterministic post-processing is a v2 candidate.

### Unmapped Fallback Occurrences

- **`methods`** (1 CVs): `cv_07`
  - The `"unmapped"` fallback fires when the LLM encounters a value outside its known taxonomy.

### Recall Gaps by Field

Top 5 most-missed items per field, sorted by miss count (descending). For format-tolerant fields, gaps are reported on raw (strict exact-match) misses to surface format drift.

**`certifications`**

- `lean six sigma black belt` (missed in 4 CVs: `cv_03`, `cv_16`, `cv_17`, `cv_20`)
- `lean six sigma green belt` (missed in 3 CVs: `cv_06`, `cv_11`, `cv_14`)
- `scrum master psm i` (missed in 2 CVs: `cv_14`, `cv_17`)
- `bloomberg market concepts (2023)` (missed in 1 CVs: `cv_05`)
- `cfa level i (passed, 2024)` (missed in 1 CVs: `cv_05`)

**`functional_expertise`**

- `organization design` (missed in 3 CVs: `cv_07`, `cv_17`, `cv_20`)
- `performance improvement` (missed in 3 CVs: `cv_07`, `cv_16`, `cv_20`)
- `growth strategy` (missed in 2 CVs: `cv_17`, `cv_20`)
- `mergers and acquisitions` (missed in 2 CVs: `cv_11`, `cv_17`)
- `strategy` (missed in 2 CVs: `cv_12`, `cv_16`)

**`industries`**

- `financial services` (missed in 2 CVs: `cv_07`, `cv_12`)
- `retail` (missed in 2 CVs: `cv_10`, `cv_20`)
- `automotive` (missed in 1 CVs: `cv_10`)
- `chemicals` (missed in 1 CVs: `cv_17`)
- `consumer goods` (missed in 1 CVs: `cv_17`)

**`methods`**

- `scrum` (missed in 2 CVs: `cv_11`, `cv_12`)

## Methodology Notes

### Scoring approach

- **String-identity fields** (`name`, `current_role`, `career_level`): exact match after whitespace normalization. `name` and `current_role` are case-sensitive; `career_level` is case-insensitive.
- **Integer fields** (`total_years_experience`): equality. Empty or unparseable pipeline values score 0 and are logged as missing extractions.
- **Set-valued fields** (`industries`, `functional_expertise`, `methods`, `tools`, `languages`, `certifications`): precision, recall, and F1 on lowercased members. The `"unmapped"` fallback token is stripped before scoring and tracked separately.
- **List-of-object fields** (`employment_history`, `education`): F1 on employer/institution name coverage. Role-title, date-range, and responsibility-extraction scoring is deferred to v2.

### Format-tolerant matching

`certifications` and `languages` carry metadata in annotations — e.g., ground truth `"CFA Level I (passed, 2024)"` versus pipeline `"CFA Level I"`. For these two fields the comparison generates up to three match-set variants per string:

1. Original (lowercased, stripped)
2. Parenthetical content removed: `"cfa level i (passed, 2024)"` → `"cfa level i"`
3. Parenthesis characters removed but content preserved: `"scrum master (psm i)"` → `"scrum master psm i"`

A pred-string matches a gold-string when their variant sets intersect. This avoids penalizing annotation-format drift while keeping strict-vocabulary fields (`industries`, `functional_expertise`, `methods`, `tools`) under exact-match comparison. Raw scores (strict exact-match) are reported alongside normalized scores for transparency.

### Known limitations

- Eval set: 11 synthetic PDF CVs. DOCX (8 CVs) and TXT (1 CV) are deferred to v2 (see README *Architecture Decisions*).
- Ground truth was iteratively refined during build; corrections are documented in `REVIEW_LOG.md` and justified against CV content rather than against pipeline output.
- No baseline comparison in this report. Zero-shot GPT-4o-without-schema baseline is a separate concern and a separate run.

## What v2 Will Improve

- **Deterministic computation of `total_years_experience`** from extracted `employment_history` dates. LLM date arithmetic is the dominant integer-field failure mode (see `FAILURE_LOG.md` 2026-05-07).
- **DOCX and TXT support.** Extends from 11/20 to 20/20 eval CVs. Compliance path (OpenAI Responses, AWS Textract Frankfurt, or AWS European Sovereign Cloud) is selected per customer tier — see README *Compliance and Sovereignty*.
- **Audited synonym normalization** for set-valued fields. Data-driven lookup table built from observed pipeline-vs-ground-truth mismatches, with an audit trail per mapping.
- **Sub-field F1 for `employment_history` and `education`.** Adds role-title, date-range, and responsibility-extraction scoring alongside the current employer/institution coverage.
- **Adversarial test set.** Heavily formatted PDFs, scanned/image PDFs (OCR path), multi-language CVs, and intentional ambiguities (gap years, freelance + employed parallel).
