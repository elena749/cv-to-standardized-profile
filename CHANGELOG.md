# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned
- Pipeline implementation (n8n workflow)
- Instrumentation (cost, latency, token tracking)
- Eval against ground truth (Field-Level F1)
- v2 with mitigations from BREAK session

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