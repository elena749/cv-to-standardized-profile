"""Generate a markdown evaluation report from eval/results/metrics_v1.json.

Reads the metrics JSON and writes eval/results/EVAL_REPORT.md — a standalone
artifact suitable for linking from README or copying into pre-sales material.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path

EVAL_DIR = Path(__file__).parent
RESULTS_DIR = EVAL_DIR / "results"
METRICS_PATH = RESULTS_DIR / "metrics_v1.json"
OUTPUT_PATH = RESULTS_DIR / "EVAL_REPORT.md"

FORMAT_TOLERANT_FIELDS = {"certifications", "languages"}
FAIL_F1_THRESHOLD = 0.7
NOTABLE_CAP = 3
RECALL_GAP_TOP_N = 5


# ---------- helpers ----------

def f2(x: float) -> str:
    return f"{x:.2f}"


def _mean(vals: list[float]) -> float:
    return statistics.fmean(vals) if vals else 0.0


def set_field_normalized_f1(field: str, result: dict) -> float:
    if field in FORMAT_TOLERANT_FIELDS:
        return result["normalized"]["f1"]
    return result["f1"]


def cv_components(scores: dict) -> tuple[float, float, float, float]:
    """(overall, set_f1, list_f1, str_f1) — normalized for format-tolerant set fields."""
    str_vals = list(scores["string_fields"].values()) + list(scores["integer_fields"].values())
    set_vals = [set_field_normalized_f1(f, v) for f, v in scores["set_fields"].items()]
    list_vals = [v["f1"] for v in scores["list_fields"].values()]
    return (
        _mean(str_vals + set_vals + list_vals),
        _mean(set_vals),
        _mean(list_vals),
        _mean(str_vals),
    )


def notable_failures(scores: dict) -> list[str]:
    out: list[str] = []
    for f, v in scores["string_fields"].items():
        if v == 0:
            out.append(f)
    for f, v in scores["integer_fields"].items():
        if v == 0:
            out.append(f)
    for f, v in scores["set_fields"].items():
        if set_field_normalized_f1(f, v) < FAIL_F1_THRESHOLD:
            out.append(f)
    return out[:NOTABLE_CAP]


def cv_list(ids: list[str]) -> str:
    return ", ".join(f"`{cv}`" for cv in ids)


# ---------- sections ----------

def section_header(meta: dict) -> str:
    scope = meta.get("scope_note") or meta.get("v1_scope_note", "")
    return (
        "# CV-to-Standardized-Profile — v1 Evaluation Report\n"
        "\n"
        f"**Run:** `{meta['run_id']}` | **N CVs:** {meta['n_cvs']} | "
        f"**Scope:** {scope}\n"
    )


def section_tldr(agg: dict) -> str:
    return (
        "## TL;DR\n"
        "\n"
        f"- **Overall macro F1 (raw):** {f2(agg['overall_f1_macro_raw'])}\n"
        f"- **Overall macro F1 (normalized):** {f2(agg['overall_f1_macro_normalized'])}\n"
        "- Normalized score reflects format-tolerant matching on `certifications` and `languages`. "
        "See [Methodology Notes](#methodology-notes) below.\n"
    )


def section_aggregate(agg: dict) -> str:
    rows: list[tuple[str, str, float, str, str, str, str]] = []
    for f, v in agg["string_fields"].items():
        rows.append((f, "string", v, f2(v), "—", "—", ""))
    for f, v in agg["integer_fields"].items():
        note = "LLM date arithmetic unreliable; see Failure Modes" if f == "total_years_experience" else ""
        rows.append((f, "integer", v, f2(v), "—", "—", note))
    for f, v in agg["set_fields"].items():
        if f in FORMAT_TOLERANT_FIELDS:
            n, r = v["normalized"], v["raw"]
            rows.append((
                f, "set", n["mean_f1"],
                f"{f2(n['mean_f1'])} (raw: {f2(r['mean_f1'])})",
                f"{f2(n['mean_precision'])} (raw: {f2(r['mean_precision'])})",
                f"{f2(n['mean_recall'])} (raw: {f2(r['mean_recall'])})",
                "Format-tolerant matching active",
            ))
        else:
            rows.append((f, "set", v["mean_f1"],
                         f2(v["mean_f1"]), f2(v["mean_precision"]), f2(v["mean_recall"]), ""))
    for f, v in agg["list_fields"].items():
        rows.append((f, "list", v["mean_f1"], f2(v["mean_f1"]), "—", "—",
                     "Employer/institution coverage only (v1)"))

    rows.sort(key=lambda r: r[2])

    lines = [
        "## Aggregate Field Performance",
        "",
        "Sorted by F1 ascending (weakest first).",
        "",
        "| Field | Type | F1 | Precision | Recall | Notes |",
        "|---|---|---|---|---|---|",
    ]
    for name, t, _, f1_cell, p_cell, r_cell, note in rows:
        lines.append(f"| `{name}` | {t} | {f1_cell} | {p_cell} | {r_cell} | {note} |")
    return "\n".join(lines) + "\n"


def section_per_cv(per_cv: dict) -> str:
    rows = []
    for cv_id, scores in per_cv.items():
        overall, set_f1, list_f1, str_f1 = cv_components(scores)
        rows.append((cv_id, overall, set_f1, list_f1, str_f1, notable_failures(scores)))
    rows.sort(key=lambda r: r[1])

    lines = [
        "## Per-CV Performance",
        "",
        ("Sorted by overall F1 ascending. Notable failures: string/integer fields with score 0, "
         "or set fields with F1 < 0.7 (normalized where applicable); capped at "
         f"{NOTABLE_CAP} per CV."),
        "",
        "| CV | Overall F1 | Set F1 | List F1 | String F1 | Notable failures |",
        "|---|---|---|---|---|---|",
    ]
    for cv_id, overall, set_f1, list_f1, str_f1, nf in rows:
        nf_cell = ", ".join(f"`{x}`" for x in nf) if nf else "—"
        lines.append(
            f"| `{cv_id}` | {f2(overall)} | {f2(set_f1)} | {f2(list_f1)} | {f2(str_f1)} | {nf_cell} |"
        )
    return "\n".join(lines) + "\n"


def section_failure_modes(fm: dict) -> str:
    lines = ["## Failure Modes", ""]

    lines.append("### Missing Extractions")
    lines.append("")
    if not fm["missing_extractions"]:
        lines.append("None.")
    else:
        for field, cvs in sorted(fm["missing_extractions"].items()):
            lines.append(f"- **`{field}`** ({len(cvs)} CVs): {cv_list(cvs)}")
            if field == "total_years_experience":
                lines.append(
                    "  - Pipeline emits a value in most cases but LLM date arithmetic over "
                    "employment ranges is unreliable. Deterministic post-processing is a v2 candidate."
                )
            else:
                lines.append("  - Pipeline emitted an empty value while ground truth had content.")
    lines.append("")

    lines.append("### Unmapped Fallback Occurrences")
    lines.append("")
    if not fm["unmapped_occurrences"]:
        lines.append("None.")
    else:
        for field, cvs in sorted(fm["unmapped_occurrences"].items()):
            lines.append(f"- **`{field}`** ({len(cvs)} CVs): {cv_list(cvs)}")
            lines.append(
                "  - The `\"unmapped\"` fallback fires when the LLM encounters a value "
                "outside its known taxonomy."
            )
    lines.append("")

    lines.append("### Recall Gaps by Field")
    lines.append("")
    if not fm["recall_gaps_by_field"]:
        lines.append("None.")
    else:
        lines.append(
            f"Top {RECALL_GAP_TOP_N} most-missed items per field, sorted by miss count (descending). "
            "For format-tolerant fields, gaps are reported on raw (strict exact-match) misses to "
            "surface format drift."
        )
        lines.append("")
        for field, items in sorted(fm["recall_gaps_by_field"].items()):
            top = sorted(items.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:RECALL_GAP_TOP_N]
            lines.append(f"**`{field}`**")
            lines.append("")
            for item, cvs in top:
                lines.append(f"- `{item}` (missed in {len(cvs)} CVs: {cv_list(cvs)})")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def section_methodology() -> str:
    return (
        "## Methodology Notes\n"
        "\n"
        "### Scoring approach\n"
        "\n"
        "- **String-identity fields** (`name`, `current_role`, `career_level`): exact match after "
        "whitespace normalization. `name` and `current_role` are case-sensitive; `career_level` "
        "is case-insensitive.\n"
        "- **Integer fields** (`total_years_experience`): equality. Empty or unparseable pipeline "
        "values score 0 and are logged as missing extractions.\n"
        "- **Set-valued fields** (`industries`, `functional_expertise`, `methods`, `tools`, "
        "`languages`, `certifications`): precision, recall, and F1 on lowercased members. "
        "The `\"unmapped\"` fallback token is stripped before scoring and tracked separately.\n"
        "- **List-of-object fields** (`employment_history`, `education`): F1 on "
        "employer/institution name coverage. Role-title, date-range, and responsibility-extraction "
        "scoring is deferred to v2.\n"
        "\n"
        "### Format-tolerant matching\n"
        "\n"
        "`certifications` and `languages` carry metadata in annotations — e.g., ground truth "
        "`\"CFA Level I (passed, 2024)\"` versus pipeline `\"CFA Level I\"`. For these two "
        "fields the comparison generates up to three match-set variants per string:\n"
        "\n"
        "1. Original (lowercased, stripped)\n"
        "2. Parenthetical content removed: `\"cfa level i (passed, 2024)\"` → `\"cfa level i\"`\n"
        "3. Parenthesis characters removed but content preserved: "
        "`\"scrum master (psm i)\"` → `\"scrum master psm i\"`\n"
        "\n"
        "A pred-string matches a gold-string when their variant sets intersect. This avoids "
        "penalizing annotation-format drift while keeping strict-vocabulary fields "
        "(`industries`, `functional_expertise`, `methods`, `tools`) under exact-match comparison. "
        "Raw scores (strict exact-match) are reported alongside normalized scores for transparency.\n"
        "\n"
        "### Known limitations\n"
        "\n"
        "- Eval set: 11 synthetic PDF CVs. DOCX (8 CVs) and TXT (1 CV) are deferred to v2 "
        "(see README *Architecture Decisions*).\n"
        "- Ground truth was iteratively refined during build; corrections are documented in "
        "`REVIEW_LOG.md` and justified against CV content rather than against pipeline output.\n"
        "- No baseline comparison in this report. Zero-shot GPT-4o-without-schema baseline is "
        "a separate concern and a separate run.\n"
    )


def section_v2_roadmap() -> str:
    return (
        "## What v2 Will Improve\n"
        "\n"
        "- **Deterministic computation of `total_years_experience`** from extracted "
        "`employment_history` dates. LLM date arithmetic is the dominant integer-field failure mode "
        "(see `FAILURE_LOG.md` 2026-05-07).\n"
        "- **DOCX and TXT support.** Extends from 11/20 to 20/20 eval CVs. Compliance path "
        "(OpenAI Responses, AWS Textract Frankfurt, or AWS European Sovereign Cloud) is selected "
        "per customer tier — see README *Compliance and Sovereignty*.\n"
        "- **Audited synonym normalization** for set-valued fields. Data-driven lookup table "
        "built from observed pipeline-vs-ground-truth mismatches, with an audit trail per mapping.\n"
        "- **Sub-field F1 for `employment_history` and `education`.** Adds role-title, "
        "date-range, and responsibility-extraction scoring alongside the current "
        "employer/institution coverage.\n"
        "- **Adversarial test set.** Heavily formatted PDFs, scanned/image PDFs (OCR path), "
        "multi-language CVs, and intentional ambiguities (gap years, freelance + employed parallel).\n"
    )


# ---------- main ----------

def load_metrics() -> dict:
    return json.loads(METRICS_PATH.read_text(encoding="utf-8"))


def build_report(metrics: dict) -> str:
    return "\n".join([
        section_header(metrics["meta"]),
        section_tldr(metrics["aggregate"]),
        section_aggregate(metrics["aggregate"]),
        section_per_cv(metrics["per_cv"]),
        section_failure_modes(metrics["failure_modes"]),
        section_methodology(),
        section_v2_roadmap(),
    ])


def main() -> None:
    metrics = load_metrics()
    report = build_report(metrics)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    n_lines = len(report.splitlines())
    print(f"Wrote {OUTPUT_PATH.relative_to(EVAL_DIR.parent)} ({n_lines} lines)")


if __name__ == "__main__":
    main()
