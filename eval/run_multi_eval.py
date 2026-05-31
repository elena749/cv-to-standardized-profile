#!/usr/bin/env python3
"""
eval/run_multi_eval.py — multi-run F1 comparison: n8n pipeline vs zero-shot baseline.

Both systems are run N times against the same 11 PDFs. For each system we report
mean ± stddev of macro F1 (raw and normalized) and a ranges-overlap check that
tells us whether the lift is genuine at this N or within measurement noise.

Reuses helpers from run_pipeline.py (n8n webhook), run_baseline.py (OpenAI direct),
and compute_metrics.py (scoring). Does not modify those scripts.

Per-run raw outputs are preserved under eval/multi_runs/<TIMESTAMP>/ so per-CV
stability or other post-hoc analyses can be added later without re-running.

Usage:
    python eval/run_multi_eval.py
"""
from __future__ import annotations

import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path

# Make sibling eval/ modules importable when invoked from the project root.
sys.path.insert(0, str(Path(__file__).parent))

from run_pipeline import post_cv, save_json
from run_baseline import (
    MODEL as BASELINE_MODEL,
    extract_one,
    extract_pdf_text,
    normalize_to_pipeline_shape,
)
from compute_metrics import (
    aggregate,
    find_paired_cvs,
    load_ground_truth,
    load_pipeline,
    score_cv,
)

try:
    from openai import OpenAI
except ImportError:
    raise SystemExit("Missing dependency: openai. Install with: pip install openai")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# --- Constants ----------------------------------------------------------------

N_RUNS = 5

CV_DIR = Path("eval/cvs")
GT_DIR = Path("eval/ground_truth")
MULTI_RUNS_ROOT = Path("eval/multi_runs")

SLEEP_BETWEEN_REQUESTS = 3                # seconds (mirrors single-run scripts)

# Per-CV estimates for the pre-run banner only. Drawn from the n=1 EVAL_REPORT.
PIPELINE_COST_PER_CV_EST = 0.009
BASELINE_COST_PER_CV_EST = 0.005
SEC_PER_PIPELINE_CV_EST = 8
SEC_PER_BASELINE_CV_EST = 7

PIPELINE_LABEL = "gpt-4o-2024-08-06 (via n8n webhook, schema-enforced)"
BASELINE_LABEL = f"{BASELINE_MODEL} (direct, no schema)"


# --- Per-run execution --------------------------------------------------------

def run_pipeline_once(pdfs: list[Path], out_dir: Path) -> None:
    """Send all PDFs through the n8n pipeline; write outputs to out_dir.

    Failures save as cv_NN.error.json so post-hoc stability analysis can
    distinguish 'failed' from 'absent'.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, pdf in enumerate(pdfs):
        parsed, err = post_cv(pdf)
        if err is not None:
            save_json(out_dir / f"{pdf.stem}.error.json",
                      {"file": pdf.name, "error": err})
        else:
            save_json(out_dir / f"{pdf.stem}.json", parsed)
        if i < len(pdfs) - 1:
            time.sleep(SLEEP_BETWEEN_REQUESTS)


def run_baseline_once(pdfs: list[Path], out_dir: Path, client: OpenAI) -> None:
    """Send all PDFs through the zero-shot baseline; write pipeline-shaped outputs."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, pdf in enumerate(pdfs):
        try:
            cv_text = extract_pdf_text(pdf)
        except Exception as e:
            save_json(out_dir / f"{pdf.stem}.error.json",
                      {"file": pdf.name, "error": f"pdf parse error: {e}"})
            if i < len(pdfs) - 1:
                time.sleep(SLEEP_BETWEEN_REQUESTS)
            continue
        parsed, latency_ms, usage, err = extract_one(client, cv_text)
        if err is not None:
            save_json(out_dir / f"{pdf.stem}.error.json",
                      {"file": pdf.name, "error": err})
        else:
            payload = normalize_to_pipeline_shape(parsed, latency_ms, usage)
            save_json(out_dir / f"{pdf.stem}.json", [payload])
        if i < len(pdfs) - 1:
            time.sleep(SLEEP_BETWEEN_REQUESTS)


# --- Scoring ------------------------------------------------------------------

def score_run(raw_dir: Path) -> tuple[float, float, int]:
    """Return (macro_f1_raw, macro_f1_normalized, n_cvs_scored) for one run dir."""
    paired = find_paired_cvs(raw_dir)
    per_cv: dict = {}
    for name in paired:
        cv_id = name.removesuffix(".json")
        pipeline = load_pipeline(raw_dir / name)
        gt = load_ground_truth(GT_DIR / name)
        per_cv[cv_id] = score_cv(cv_id, pipeline, gt)
    agg = aggregate(per_cv)
    return agg["overall_f1_macro_raw"], agg["overall_f1_macro_normalized"], len(paired)


# --- Stats --------------------------------------------------------------------

def summarize(scores: list[float]) -> dict:
    mean = statistics.fmean(scores)
    stdev = statistics.stdev(scores) if len(scores) > 1 else 0.0
    return {
        "mean": mean,
        "stdev": stdev,
        "lo": mean - stdev,
        "hi": mean + stdev,
        "runs": scores,
    }


def ranges_overlap(a: dict, b: dict) -> bool:
    return a["hi"] >= b["lo"] and b["hi"] >= a["lo"]


# --- Reporting ----------------------------------------------------------------

def print_header(n_cvs: int, out_root: Path) -> None:
    total_pipeline_calls = N_RUNS * n_cvs
    total_baseline_calls = N_RUNS * n_cvs
    total_calls = total_pipeline_calls + total_baseline_calls

    sec_per_run = n_cvs * (SEC_PER_PIPELINE_CV_EST + SEC_PER_BASELINE_CV_EST)
    total_sec = N_RUNS * sec_per_run
    cost_est = (
        N_RUNS * n_cvs * PIPELINE_COST_PER_CV_EST
        + N_RUNS * n_cvs * BASELINE_COST_PER_CV_EST
    )

    print("=" * 72)
    print("Multi-Run Evaluation: Pipeline vs Baseline")
    print("=" * 72)
    print(f"Pipeline:        {PIPELINE_LABEL}")
    print(f"Baseline:        {BASELINE_LABEL}")
    print(f"N_RUNS:          {N_RUNS}")
    print(f"N_CVs:           {n_cvs} (PDF only; DOCX/TXT deferred to v2)")
    print(f"Total LLM calls: {total_calls} ({total_pipeline_calls} pipeline + {total_baseline_calls} baseline)")
    print(f"Output dir:      {out_root}")
    print(f"Time estimate:   ~{total_sec // 60} min {total_sec % 60} sec")
    print(f"Cost estimate:   ~${cost_est:.2f}")
    print("=" * 72)
    print()


# --- Main ---------------------------------------------------------------------

def main() -> int:
    if not CV_DIR.exists():
        print(f"ERROR: {CV_DIR} not found", file=sys.stderr)
        return 1

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set (environment or .env)", file=sys.stderr)
        return 1
    client = OpenAI(api_key=api_key)

    all_cvs = sorted(CV_DIR.iterdir())
    pdfs = [p for p in all_cvs if p.suffix.lower() == ".pdf"]
    skipped = [p for p in all_cvs if p.suffix.lower() != ".pdf"]
    if not pdfs:
        print("No PDFs to process.")
        return 0

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_root = MULTI_RUNS_ROOT / timestamp
    out_root.mkdir(parents=True, exist_ok=True)

    print_header(len(pdfs), out_root)
    for skip in skipped:
        print(f"SKIP {skip.name} (not PDF — deferred to v2)")
    if skipped:
        print()

    pipeline_raw: list[float] = []
    pipeline_norm: list[float] = []
    baseline_raw: list[float] = []
    baseline_norm: list[float] = []

    wall_start = time.monotonic()
    for run_idx in range(1, N_RUNS + 1):
        run_label = f"run_{run_idx:02d}"
        pipe_dir = out_root / "pipeline" / run_label
        base_dir = out_root / "baseline" / run_label

        run_start = time.monotonic()

        run_pipeline_once(pdfs, pipe_dir)
        p_raw, p_norm, p_n = score_run(pipe_dir)
        pipeline_raw.append(p_raw)
        pipeline_norm.append(p_norm)

        run_baseline_once(pdfs, base_dir, client)
        b_raw, b_norm, b_n = score_run(base_dir)
        baseline_raw.append(b_raw)
        baseline_norm.append(b_norm)

        elapsed = time.monotonic() - run_start
        print(
            f"  {run_label}  ({elapsed:5.0f}s)  "
            f"pipeline ({p_n}/{len(pdfs)}) raw={p_raw:.3f} norm={p_norm:.3f}  |  "
            f"baseline ({b_n}/{len(pdfs)}) raw={b_raw:.3f} norm={b_norm:.3f}"
        )

    total_elapsed = time.monotonic() - wall_start

    pipe_raw_s = summarize(pipeline_raw)
    pipe_norm_s = summarize(pipeline_norm)
    base_raw_s = summarize(baseline_raw)
    base_norm_s = summarize(baseline_norm)

    overlap_raw = ranges_overlap(pipe_raw_s, base_raw_s)
    overlap_norm = ranges_overlap(pipe_norm_s, base_norm_s)
    lift_raw = pipe_raw_s["mean"] - base_raw_s["mean"]
    lift_norm = pipe_norm_s["mean"] - base_norm_s["mean"]

    print()
    print("=" * 72)
    print(f"Pipeline raw:        mean={pipe_raw_s['mean']:.3f}  stdev={pipe_raw_s['stdev']:.3f}  "
          f"range=[{pipe_raw_s['lo']:.3f}, {pipe_raw_s['hi']:.3f}]")
    print(f"Pipeline normalized: mean={pipe_norm_s['mean']:.3f}  stdev={pipe_norm_s['stdev']:.3f}  "
          f"range=[{pipe_norm_s['lo']:.3f}, {pipe_norm_s['hi']:.3f}]")
    print(f"Baseline raw:        mean={base_raw_s['mean']:.3f}  stdev={base_raw_s['stdev']:.3f}  "
          f"range=[{base_raw_s['lo']:.3f}, {base_raw_s['hi']:.3f}]")
    print(f"Baseline normalized: mean={base_norm_s['mean']:.3f}  stdev={base_norm_s['stdev']:.3f}  "
          f"range=[{base_norm_s['lo']:.3f}, {base_norm_s['hi']:.3f}]")
    print()
    print(f"Lift raw:        +{lift_raw:.3f}")
    print(f"Lift normalized: +{lift_norm:.3f}")
    print()
    verdict_raw = "OVERLAP — within noise at n=5" if overlap_raw else "no overlap — resolvable at n=5"
    verdict_norm = "OVERLAP — within noise at n=5" if overlap_norm else "no overlap — resolvable at n=5"
    print(f"Ranges overlap (raw):        {verdict_raw}")
    print(f"Ranges overlap (normalized): {verdict_norm}")
    print(f"Wall-clock:      {total_elapsed:.0f}s")
    print("=" * 72)

    summary = {
        "model_pipeline": PIPELINE_LABEL,
        "model_baseline": BASELINE_LABEL,
        "n_runs": N_RUNS,
        "n_cvs": len(pdfs),
        "scope_note": "PDF only; DOCX/TXT deferred to v2",
        "timestamp": timestamp,
        "wall_clock_sec": total_elapsed,
        "pipeline": {"raw": pipe_raw_s, "normalized": pipe_norm_s},
        "baseline": {"raw": base_raw_s, "normalized": base_norm_s},
        "lift": {"raw_mean": lift_raw, "normalized_mean": lift_norm},
        "ranges_overlap": {"raw": overlap_raw, "normalized": overlap_norm},
    }
    summary_path = out_root / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"Summary: {summary_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
