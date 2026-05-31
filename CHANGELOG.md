# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026-05-31

### Added
- `eval/run_multi_eval.py` — multi-run evaluation script (adapted from Build 1 pattern)
- Multi-Run Reliability section in `eval/results/EVAL_REPORT.md`
- Multi-run aggregate in `README.md` Eval Results section
- Raw multi-run artifacts in `eval/multi_runs/20260531_165630/` (55 pipeline + 55 baseline outputs + `summary.json`)
- `FAILURE_LOG.md` entry: "Multi-eval script lacks in-run progress logging"

### Changed
- Eval Results table in README now reports Mean F1 ± Stdev across N=5 runs (was: single-run point estimate)
- Single-run snapshot from 2026-05-12 retained as source of per-field and per-CV detail

### Eval results (N=5 runs over 11 PDF CVs)
- Pipeline F1: **0.809 ± 0.006** raw / **0.861 ± 0.0004** normalized
- Baseline F1: 0.567 ± 0.005 raw / 0.618 ± 0.005 normalized
- Lift: **+0.241 raw / +0.243 normalized**
- Ranges overlap: false (both raw and normalized) — lift is resolvable at n=5

## [1.0.0] — 2026-05-12

### Added
- v1 pipeline shipped end-to-end (n8n webhook → text extraction → GPT-4o structured output → Google Sheets)
- Pipeline instrumentation: latency_ms, input_tokens, output_tokens, cost_usd, model per CV
- Single-run eval on 11 PDF CVs: macro F1 = 0.80 raw / 0.86 normalized
- Zero-shot baseline comparison: macro F1 = 0.58 raw / 0.63 normalized
- `eval/run_pipeline.py`, `eval/run_baseline.py`, `eval/compute_metrics.py`, `eval/generate_report.py`
- `eval/results/EVAL_REPORT.md` with per-field and per-CV breakdown
- `FAILURE_LOG.md` with 5 failure modes catalogued
- README sections: Who this is for, Architecture Decisions, Schema, Compliance and Sovereignty, Security and Governance, Eval Results, ROI math, What this demonstrates (resume bullet + pre-sales framing)
- Customer persona section with budget signals and procurement objection mitigations
- v2 Architecture Roadmap (eval-driven): Multi-stage, Self-critique, Provider A/B paths with trigger conditions
- `CONVENTION_DRIFT_REVIEW.md` documenting 5 functional_expertise corrections after labeling-convention change
- ADR: Strict-Mode schema variant (`schema/profile.strict.schema.json`) alongside canonical schema

### Decided
- DOCX (8 CVs) and TXT (1 CV) deferred to v2 — compliance-driven path selection documented (CloudConvert / AWS Textract Frankfurt / AWS European Sovereign Cloud)
- Academic positions (wiss. Mitarbeiter, RA) excluded from `total_years_experience` for non-academic career-track candidates (LABELING_CONVENTIONS update, cv_15 origin)

## [0.5.0] — 2026-05-07

### Added
- Eval set v1 with 20 synthetic CVs (8 DOCX, 10 PDF, 2 TXT) including 5 complex layouts
- Ground truth JSONs for all 20 CVs, hand-validated against sources
- `eval/ground_truth/LABELING_CONVENTIONS.md` with 17 conventions
- `eval/ground_truth/REVIEW_LOG.md` documenting per-CV review with 8 generalized learnings

### Fixed
- cv_11 employment_history: project-to-role attribution corrected
- cv_12 total_years_experience: 4 → 5 (mathematical rounding)
- cv_12 career_level: Mid → Senior
- cv_13 DOCX regenerated to include all fields from markdown source
- cv_15 functional_expertise: removed hallucinations (Risk Management, Strategy)
- cv_15 career_level: Senior → Mid (career-switcher convention)
- cv_20 employment titles: McKinsey-correct (Engagement Manager, Associate)

## [0.4.0] — 2026-05-06

### Added
- JSON Schema v1 (`schema/profile.schema.json`) with 15 fields, name as only required

## [0.3.0] — 2026-05-06

### Added
- Taxonomy v1 (`taxonomy/taxonomy.yaml`) — controlled vocabulary for industries, functional expertise, methods, tools, languages, education credentials

## [0.2.0] — 2026-05-06

### Added
- Customer persona (strategy consulting firm)
- ROI math (3,500 CVs/month × 18 min × 70€/h = ~73,500€/month savings)

## [0.1.0] — 2026-05-06

### Added
- Initial repo setup
- README stub, .gitignore, .env.example