#!/usr/bin/env python3
"""
eval/run_pipeline.py — send v1 PDFs through the n8n CV-extraction webhook
and save raw responses for downstream evaluation.

v1 scope: PDF only (11 of 20 CVs). DOCX/TXT skipped with logging.

Usage:
    python eval/run_pipeline.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import requests

# --- Constants ----------------------------------------------------------------

WEBHOOK_URL = "https://buildersbuilding.app.n8n.cloud/webhook/cv-upload-v2"
REQUEST_TIMEOUT = 60                  # seconds, per HTTP request
SLEEP_BETWEEN_REQUESTS = 3            # seconds, OpenAI rate-limit cushion

CV_DIR = Path("eval/cvs")
OUTPUT_DIR = Path("eval/raw_outputs")


# --- Helpers ------------------------------------------------------------------

def post_cv(pdf_path: Path) -> tuple[list | dict | None, str | None]:
    """POST a PDF; return (parsed_response, error). Exactly one is None."""
    try:
        with pdf_path.open("rb") as f:
            response = requests.post(
                WEBHOOK_URL,
                files={"data": (pdf_path.name, f, "application/pdf")},
                timeout=REQUEST_TIMEOUT,
            )
    except requests.Timeout:
        return None, f"timeout after {REQUEST_TIMEOUT}s"
    except requests.RequestException as e:
        return None, f"request error: {e}"

    if not response.content:
        return None, "empty response body"

    try:
        parsed = response.json()
    except ValueError as e:
        return None, f"malformed JSON: {e}; body[:200]={response.text[:200]!r}"

    return parsed, None


def _to_float(value) -> float | None:
    """Coerce numeric or numeric-string values to float; None otherwise."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def extract_metrics(parsed) -> tuple[float | None, float | None]:
    """Return (latency_ms, cost_usd) from the response, or (None, None).

    Webhook returns cost_usd as a string; latency_ms may also be string-typed.
    """
    if isinstance(parsed, list) and parsed and isinstance(parsed[0], dict):
        record = parsed[0]
    elif isinstance(parsed, dict):
        record = parsed
    else:
        return None, None
    return _to_float(record.get("latency_ms")), _to_float(record.get("cost_usd"))


def save_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


# --- Main ---------------------------------------------------------------------

def main() -> int:
    if not CV_DIR.exists():
        print(f"ERROR: {CV_DIR} not found", file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_cvs = sorted(CV_DIR.iterdir())
    pdfs = [p for p in all_cvs if p.suffix.lower() == ".pdf"]
    skipped = [p for p in all_cvs if p.suffix.lower() != ".pdf"]

    for skip in skipped:
        print(f"SKIP {skip.name} (not PDF — deferred to v2)")

    if not pdfs:
        print("No PDFs to process.")
        return 0

    total = len(pdfs)
    successes: list[str] = []
    failures: list[tuple[str, str]] = []
    total_cost = 0.0
    latencies: list[float] = []

    run_start = time.monotonic()

    for i, pdf in enumerate(pdfs, start=1):
        stem = pdf.stem
        parsed, err = post_cv(pdf)

        if err is not None:
            save_json(OUTPUT_DIR / f"{stem}.error.json",
                      {"file": pdf.name, "error": err})
            print(f"[{i}/{total}] {pdf.name} → FAIL ({err})")
            failures.append((pdf.name, err))
        else:
            save_json(OUTPUT_DIR / f"{stem}.json", parsed)
            latency, cost = extract_metrics(parsed)
            latency_str = f"{latency:.0f}ms" if latency is not None else "?ms"
            cost_str = f"${cost:.4f}" if cost is not None else "$?"
            print(f"[{i}/{total}] {pdf.name} → OK ({latency_str}, {cost_str})")
            successes.append(pdf.name)
            if latency is not None:
                latencies.append(latency)
            if cost is not None:
                total_cost += cost

        if i < total:
            time.sleep(SLEEP_BETWEEN_REQUESTS)

    elapsed = time.monotonic() - run_start
    avg_latency = sum(latencies) / len(latencies) if latencies else 0

    print()
    print("=== Summary ===")
    print(f"Attempted:    {total}")
    print(f"Succeeded:    {len(successes)}")
    print(f"Failed:       {len(failures)}")
    for name, reason in failures:
        print(f"  - {name}: {reason}")
    print(f"Elapsed:      {elapsed:.1f}s")
    print(f"Total cost:   ${total_cost:.4f}")
    print(f"Avg latency:  {avg_latency:.0f}ms")

    return 0


if __name__ == "__main__":
    sys.exit(main())
