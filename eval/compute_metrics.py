"""Compute per-CV and aggregate F1 against ground truth for v1 eval set.

Reads paired CVs from eval/raw_outputs/ and eval/ground_truth/, scores each
field per its type (string-identity, integer, set-valued, list-of-objects),
and writes eval/results/metrics_v1.json for downstream reporting.

v1 scope: PDF only (11 of 20 CVs). List-of-objects scoring covers
employer/institution coverage only; role-title and date-range scoring is
v2 (see README "v2 Architecture Roadmap").
"""
from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

EVAL_DIR = Path(__file__).parent
RAW_DIR = EVAL_DIR / "raw_outputs"
GT_DIR = EVAL_DIR / "ground_truth"
RESULTS_DIR = EVAL_DIR / "results"
OUTPUT_PATH = RESULTS_DIR / "metrics_v1.json"

RUN_ID = "v1_2026-05-12"
V1_SCOPE_NOTE = "PDF only; DOCX/TXT deferred to v2"

STRING_FIELDS_CASE_SENSITIVE = ["name", "current_role"]
STRING_FIELDS_CASE_INSENSITIVE = ["career_level"]
INTEGER_FIELDS = ["total_years_experience"]
SET_FIELDS = [
    "industries",
    "functional_expertise",
    "methods",
    "tools",
    "languages",
    "certifications",
]
LIST_FIELDS = {
    "employment_history": "employer",
    "education": "institution",
}

UNMAPPED_TOKEN = "unmapped"
CV_NAME_RE = re.compile(r"^cv_\d+\.json$")
ENTRY_SEPARATOR_RE = re.compile(r"\s+—\s+")
WS_RE = re.compile(r"\s+")

# Set fields where annotations may carry metadata (dates, level codes, etc.)
# that shouldn't penalize a correct extraction. Other set fields are clean
# taxonomy terms — parentheses there would be a real difference.
FORMAT_TOLERANT_FIELDS = {"certifications", "languages"}

PAREN_BLOCK_RE = re.compile(r"\s*\([^)]*\)\s*")


def match_set(value: str) -> set[str]:
    """Generate matching variants for format-tolerant comparison.

    Variants:
    1. base (lowercased, stripped)
    2. parenthetical blocks removed: "cfa level i (passed, 2024)" -> "cfa level i"
    3. paren chars removed, content kept: "scrum master (psm i)" -> "scrum master psm i"
    """
    base = value.strip().lower()
    variants = {base}
    stripped = WS_RE.sub(" ", PAREN_BLOCK_RE.sub(" ", base)).strip()
    if stripped:
        variants.add(stripped)
    no_parens = WS_RE.sub(" ", base.replace("(", "").replace(")", "")).strip()
    if no_parens:
        variants.add(no_parens)
    return variants


# ---------- I/O ----------

def find_paired_cvs() -> list[str]:
    raw = {p.name for p in RAW_DIR.glob("cv_*.json") if CV_NAME_RE.match(p.name)}
    gt = {p.name for p in GT_DIR.glob("cv_*.json") if CV_NAME_RE.match(p.name)}
    return sorted(raw & gt)


def load_pipeline(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data[0] if data else {}
    return data


def load_ground_truth(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------- Normalization ----------

def normalize_string(value) -> str:
    if value is None:
        return ""
    return WS_RE.sub(" ", str(value).strip())


def parse_set_field(value) -> tuple[list[str], bool]:
    """Return (lowercased members with unmapped stripped, unmapped_flag)."""
    if isinstance(value, list):
        items = [str(v) for v in value if isinstance(v, str) and v.strip()]
    elif isinstance(value, str) and value.strip():
        items = [part for part in value.split(", ") if part.strip()]
    else:
        items = []
    lowered = [item.strip().lower() for item in items]
    unmapped = UNMAPPED_TOKEN in lowered
    return [x for x in lowered if x != UNMAPPED_TOKEN], unmapped


def extract_anchors_from_pipeline(value) -> list[str]:
    """Pull employer/institution names from a multi-line pipeline string.

    Any line containing ' — ' is treated as an entry header; the part before
    the em-dash is the anchor. Handles both layouts (employment_history with
    \\n\\n separators and education with single \\n).
    """
    if not isinstance(value, str):
        return []
    anchors = []
    for line in value.splitlines():
        if not line.strip():
            continue
        parts = ENTRY_SEPARATOR_RE.split(line, maxsplit=1)
        if len(parts) == 2:
            anchors.append(parts[0].strip().lower())
    return anchors


def extract_anchors_from_gt(value, key: str) -> list[str]:
    if not isinstance(value, list):
        return []
    out = []
    for entry in value:
        if isinstance(entry, dict) and isinstance(entry.get(key), str):
            out.append(entry[key].strip().lower())
    return out


def parse_integer(value) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            return int(s)
        except ValueError:
            return None
    return None


# ---------- Scoring ----------

def score_string_field(pred, gold, case_sensitive: bool) -> tuple[int, bool]:
    """Return (score, is_missing). is_missing: pred empty AND gold non-empty."""
    p = normalize_string(pred)
    g = normalize_string(gold)
    if not case_sensitive:
        p, g = p.lower(), g.lower()
    score = 1 if p == g else 0
    is_missing = (p == "") and (g != "")
    return score, is_missing


def score_integer_field(pred, gold) -> tuple[int, bool]:
    p = parse_integer(pred)
    if p is None:
        return 0, True
    return (1 if p == gold else 0), False


def prf1(pred: list[str], gold: list[str]) -> dict:
    pred_set = set(pred)
    gold_set = set(gold)
    if not pred_set and not gold_set:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0,
                "missed": [], "extra": []}
    if not pred_set or not gold_set:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0,
                "missed": sorted(gold_set - pred_set),
                "extra": sorted(pred_set - gold_set)}
    tp = len(pred_set & gold_set)
    precision = tp / len(pred_set)
    recall = tp / len(gold_set)
    f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1,
            "missed": sorted(gold_set - pred_set),
            "extra": sorted(pred_set - gold_set)}


def prf1_normalized(pred: list[str], gold: list[str]) -> dict:
    """Soft P/R/F1: a pred-item matches a gold-item if their match-sets intersect."""
    pred_set = set(pred)
    gold_set = set(gold)
    if not pred_set and not gold_set:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "missed": [], "extra": []}
    if not pred_set or not gold_set:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0,
                "missed": sorted(gold_set - pred_set),
                "extra": sorted(pred_set - gold_set)}

    pred_variants = {p: match_set(p) for p in pred_set}
    gold_variants = {g: match_set(g) for g in gold_set}

    matched_pred = {p for p in pred_set
                    if any(pred_variants[p] & gold_variants[g] for g in gold_set)}
    matched_gold = {g for g in gold_set
                    if any(pred_variants[p] & gold_variants[g] for p in pred_set)}

    precision = len(matched_pred) / len(pred_set)
    recall = len(matched_gold) / len(gold_set)
    f1 = 0.0 if (precision + recall) == 0 else 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1,
            "missed": sorted(gold_set - matched_gold),
            "extra": sorted(pred_set - matched_pred)}


# ---------- Per-CV ----------

def score_cv(cv_id: str, pipeline: dict, gt: dict) -> dict:
    string_scores: dict[str, int] = {}
    missing: list[str] = []

    for field in STRING_FIELDS_CASE_SENSITIVE:
        score, miss = score_string_field(pipeline.get(field), gt.get(field), case_sensitive=True)
        string_scores[field] = score
        if miss:
            missing.append(field)
    for field in STRING_FIELDS_CASE_INSENSITIVE:
        score, miss = score_string_field(pipeline.get(field), gt.get(field), case_sensitive=False)
        string_scores[field] = score
        if miss:
            missing.append(field)

    integer_scores: dict[str, int] = {}
    for field in INTEGER_FIELDS:
        score, miss = score_integer_field(pipeline.get(field), gt.get(field))
        integer_scores[field] = score
        if miss:
            missing.append(field)

    set_scores: dict[str, dict] = {}
    unmapped_flags: dict[str, bool] = {}
    for field in SET_FIELDS:
        pred, unmapped = parse_set_field(pipeline.get(field))
        gold, _ = parse_set_field(gt.get(field))
        raw = prf1(pred, gold)
        if field in FORMAT_TOLERANT_FIELDS:
            normalized = prf1_normalized(pred, gold)
            set_scores[field] = {
                "raw": raw,
                "normalized": normalized,
                "pred": sorted(set(pred)),
                "gold": sorted(set(gold)),
            }
        else:
            raw["pred"] = sorted(set(pred))
            raw["gold"] = sorted(set(gold))
            set_scores[field] = raw
        unmapped_flags[field] = unmapped

    list_scores: dict[str, dict] = {}
    for field, key in LIST_FIELDS.items():
        pred_anchors = extract_anchors_from_pipeline(pipeline.get(field))
        gold_anchors = extract_anchors_from_gt(gt.get(field), key)
        result = prf1(pred_anchors, gold_anchors)
        result[f"pred_{key}s"] = sorted(set(pred_anchors))
        result[f"gold_{key}s"] = sorted(set(gold_anchors))
        list_scores[field] = result

    return {
        "string_fields": string_scores,
        "integer_fields": integer_scores,
        "set_fields": set_scores,
        "list_fields": list_scores,
        "unmapped_flags": unmapped_flags,
        "missing_extractions": missing,
    }


def _set_field_f1(field: str, result: dict, mode: str) -> float:
    """Pick raw or normalized F1 for a set field. Non-tolerant fields have one score."""
    if field in FORMAT_TOLERANT_FIELDS:
        return result[mode]["f1"]
    return result["f1"]


def per_cv_overall(scores: dict, mode: str = "normalized") -> tuple[float, float, float, float]:
    """Return (overall, set_mean, list_mean, str_mean) for the summary line."""
    str_vals = list(scores["string_fields"].values()) + list(scores["integer_fields"].values())
    set_vals = [_set_field_f1(f, v, mode) for f, v in scores["set_fields"].items()]
    list_vals = [v["f1"] for v in scores["list_fields"].values()]
    str_mean = statistics.fmean(str_vals) if str_vals else 0.0
    set_mean = statistics.fmean(set_vals) if set_vals else 0.0
    list_mean = statistics.fmean(list_vals) if list_vals else 0.0
    all_vals = str_vals + set_vals + list_vals
    overall = statistics.fmean(all_vals) if all_vals else 0.0
    return overall, set_mean, list_mean, str_mean


# ---------- Aggregate ----------

def aggregate(per_cv: dict[str, dict]) -> dict:
    cvs = list(per_cv.values())

    def mean(vals: list[float]) -> float:
        return statistics.fmean(vals) if vals else 0.0

    string_agg = {f: mean([c["string_fields"][f] for c in cvs])
                  for f in STRING_FIELDS_CASE_SENSITIVE + STRING_FIELDS_CASE_INSENSITIVE}
    integer_agg = {f: mean([c["integer_fields"][f] for c in cvs]) for f in INTEGER_FIELDS}
    def _set_block(field: str, key: str | None) -> dict:
        """Build {mean_f1, mean_precision, mean_recall} for a field, optionally under raw/normalized."""
        def pick(c: dict) -> dict:
            return c["set_fields"][field][key] if key else c["set_fields"][field]
        return {
            "mean_f1": mean([pick(c)["f1"] for c in cvs]),
            "mean_precision": mean([pick(c)["precision"] for c in cvs]),
            "mean_recall": mean([pick(c)["recall"] for c in cvs]),
        }

    set_agg: dict[str, dict] = {}
    for f in SET_FIELDS:
        if f in FORMAT_TOLERANT_FIELDS:
            set_agg[f] = {"raw": _set_block(f, "raw"), "normalized": _set_block(f, "normalized")}
        else:
            set_agg[f] = _set_block(f, None)

    list_agg = {f: {"mean_f1": mean([c["list_fields"][f]["f1"] for c in cvs])}
                for f in LIST_FIELDS}

    def _overall(mode: str) -> float:
        set_f1s = [
            set_agg[f][mode]["mean_f1"] if f in FORMAT_TOLERANT_FIELDS else set_agg[f]["mean_f1"]
            for f in SET_FIELDS
        ]
        return mean(
            list(string_agg.values())
            + list(integer_agg.values())
            + set_f1s
            + [v["mean_f1"] for v in list_agg.values()]
        )

    return {
        "string_fields": string_agg,
        "integer_fields": integer_agg,
        "set_fields": set_agg,
        "list_fields": list_agg,
        "overall_f1_macro_raw": _overall("raw"),
        "overall_f1_macro_normalized": _overall("normalized"),
    }


def collect_failure_modes(per_cv: dict[str, dict]) -> dict:
    unmapped_occurrences: dict[str, list[str]] = {}
    for cv_id, scores in per_cv.items():
        for field, flag in scores["unmapped_flags"].items():
            if flag:
                unmapped_occurrences.setdefault(field, []).append(cv_id)

    missing_extractions: dict[str, list[str]] = {}
    for cv_id, scores in per_cv.items():
        for field in scores["missing_extractions"]:
            missing_extractions.setdefault(field, []).append(cv_id)

    recall_gaps: dict[str, dict[str, list[str]]] = {}
    for cv_id, scores in per_cv.items():
        for field, result in scores["set_fields"].items():
            missed = result["raw"]["missed"] if field in FORMAT_TOLERANT_FIELDS else result["missed"]
            for missed_item in missed:
                recall_gaps.setdefault(field, {}).setdefault(missed_item, []).append(cv_id)

    return {
        "unmapped_occurrences": {k: sorted(v) for k, v in sorted(unmapped_occurrences.items())},
        "missing_extractions": {k: sorted(v) for k, v in sorted(missing_extractions.items())},
        "recall_gaps_by_field": {
            field: {item: sorted(cvs) for item, cvs in sorted(items.items())}
            for field, items in sorted(recall_gaps.items())
        },
    }


# ---------- Reporting ----------

def print_per_cv(cv_id: str, scores: dict) -> None:
    overall, set_mean, list_mean, str_mean = per_cv_overall(scores)
    print(f"{cv_id}: overall F1 = {overall:.2f} "
          f"(set fields: {set_mean:.2f}, list: {list_mean:.2f}, str: {str_mean:.2f})")


def print_top_weakest(per_cv: dict[str, dict], agg: dict) -> None:
    cv_overall = sorted(
        ((cv_id, per_cv_overall(scores)[0]) for cv_id, scores in per_cv.items()),
        key=lambda x: x[1],
    )
    print("\nTop 3 weakest CVs:")
    for cv_id, score in cv_overall[:3]:
        print(f"  {cv_id}: {score:.2f}")

    field_scores: list[tuple[str, float]] = []
    for f, v in agg["string_fields"].items():
        field_scores.append((f, v))
    for f, v in agg["integer_fields"].items():
        field_scores.append((f, v))
    for f, v in agg["set_fields"].items():
        if f in FORMAT_TOLERANT_FIELDS:
            field_scores.append((f, v["normalized"]["mean_f1"]))
        else:
            field_scores.append((f, v["mean_f1"]))
    for f, v in agg["list_fields"].items():
        field_scores.append((f, v["mean_f1"]))
    field_scores.sort(key=lambda x: x[1])
    print("\nTop 3 weakest fields:")
    for f, score in field_scores[:3]:
        print(f"  {f}: {score:.2f}")


# ---------- Main ----------

def main() -> None:
    paired = find_paired_cvs()
    print(f"Paired CVs: {len(paired)}\n")

    per_cv: dict[str, dict] = {}
    for name in paired:
        cv_id = name.removesuffix(".json")
        pipeline = load_pipeline(RAW_DIR / name)
        gt = load_ground_truth(GT_DIR / name)
        scores = score_cv(cv_id, pipeline, gt)
        per_cv[cv_id] = scores
        print_per_cv(cv_id, scores)

    agg = aggregate(per_cv)
    failure_modes = collect_failure_modes(per_cv)

    output = {
        "meta": {
            "run_id": RUN_ID,
            "n_cvs": len(paired),
            "v1_scope_note": V1_SCOPE_NOTE,
        },
        "per_cv": per_cv,
        "aggregate": agg,
        "failure_modes": failure_modes,
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nWrote {OUTPUT_PATH.relative_to(EVAL_DIR.parent)}")
    print(f"Overall macro F1 (raw):        {agg['overall_f1_macro_raw']:.2f}")
    print(f"Overall macro F1 (normalized): {agg['overall_f1_macro_normalized']:.2f}")
    print_top_weakest(per_cv, agg)


if __name__ == "__main__":
    main()
