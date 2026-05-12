"""Dump unique vocabulary across pipeline outputs and ground truth.

Reads paired CVs from eval/raw_outputs/ and eval/ground_truth/, collects
unique values per set-valued field, and writes a sorted comparison to
eval/vocabulary_dump.json. Output feeds manual synonym-table construction.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

EVAL_DIR = Path(__file__).parent
RAW_DIR = EVAL_DIR / "raw_outputs"
GT_DIR = EVAL_DIR / "ground_truth"
OUTPUT_PATH = EVAL_DIR / "vocabulary_dump.json"

SET_FIELDS = ["industries", "functional_expertise", "methods", "tools"]

CV_NAME_RE = re.compile(r"^cv_\d+\.json$")


def find_paired_cvs() -> list[str]:
    raw = {p.name for p in RAW_DIR.glob("cv_*.json") if CV_NAME_RE.match(p.name)}
    gt = {p.name for p in GT_DIR.glob("cv_*.json") if CV_NAME_RE.match(p.name)}
    return sorted(raw & gt)


def normalize(value: str) -> str:
    return value.strip().lower()


def parse_pipeline_field(value) -> list[str]:
    if not isinstance(value, str) or not value.strip():
        return []
    return [normalize(part) for part in value.split(", ") if part.strip()]


def parse_ground_truth_field(value) -> list[str]:
    if isinstance(value, list):
        return [normalize(v) for v in value if isinstance(v, str) and v.strip()]
    if isinstance(value, str) and value.strip():
        return [normalize(part) for part in value.split(", ") if part.strip()]
    return []


def load_pipeline(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data[0] if data else {}
    return data


def load_ground_truth(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_vocabulary(paired: list[str]) -> dict[str, dict[str, list[str]]]:
    pipeline_sets: dict[str, set[str]] = {f: set() for f in SET_FIELDS}
    gt_sets: dict[str, set[str]] = {f: set() for f in SET_FIELDS}

    for name in paired:
        pipeline = load_pipeline(RAW_DIR / name)
        gt = load_ground_truth(GT_DIR / name)
        for field in SET_FIELDS:
            pipeline_sets[field].update(parse_pipeline_field(pipeline.get(field)))
            gt_sets[field].update(parse_ground_truth_field(gt.get(field)))

    result: dict[str, dict[str, list[str]]] = {}
    for field in SET_FIELDS:
        p = pipeline_sets[field]
        g = gt_sets[field]
        result[field] = {
            "pipeline_only": sorted(p - g),
            "ground_truth_only": sorted(g - p),
            "both": sorted(p & g),
            "all_pipeline": sorted(p),
            "all_ground_truth": sorted(g),
        }
    return result


def print_summary(vocab: dict[str, dict[str, list[str]]]) -> None:
    for field in SET_FIELDS:
        v = vocab[field]
        print(
            f"{field}: pipeline={len(v['all_pipeline'])} unique, "
            f"gt={len(v['all_ground_truth'])} unique, "
            f"overlap={len(v['both'])}, "
            f"p_only={len(v['pipeline_only'])}, "
            f"gt_only={len(v['ground_truth_only'])}"
        )


def main() -> None:
    paired = find_paired_cvs()
    print(f"Paired CVs: {len(paired)} ({', '.join(paired)})")
    vocab = collect_vocabulary(paired)
    OUTPUT_PATH.write_text(json.dumps(vocab, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.relative_to(EVAL_DIR.parent)}")
    print_summary(vocab)


if __name__ == "__main__":
    main()
