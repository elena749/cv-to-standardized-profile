#!/usr/bin/env python3
"""
eval/run_baseline.py — naive zero-shot CV extraction for baseline comparison.

Sends each v1 PDF through gpt-4o-2024-08-06 with no structured outputs, no
schema enforcement, no field-scoped rules, no taxonomy. Output is normalized
to the same JSON shape as the pipeline (eval/raw_outputs/) so the existing
eval/compute_metrics.py can score it without modification:

    python3 eval/compute_metrics.py --raw-dir eval/baseline_outputs \\
        --output-name metrics_baseline.json

Requires:
    pip install openai pypdf python-dotenv

Reads OPENAI_API_KEY from .env (via python-dotenv if installed) or environment.

Usage:
    python eval/run_baseline.py
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    raise SystemExit(
        "Missing dependency: openai. Install with:\n"
        "    pip install openai pypdf python-dotenv"
    )

try:
    from pypdf import PdfReader
except ImportError:
    raise SystemExit(
        "Missing dependency: pypdf. Install with:\n"
        "    pip install openai pypdf python-dotenv"
    )

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# --- Constants ----------------------------------------------------------------

MODEL = "gpt-4o-2024-08-06"
INPUT_PRICE_PER_1M = 2.50
OUTPUT_PRICE_PER_1M = 10.00

REQUEST_TIMEOUT = 60
SLEEP_BETWEEN_REQUESTS = 3

CV_DIR = Path("eval/cvs")
OUTPUT_DIR = Path("eval/baseline_outputs")

SYSTEM_PROMPT = (
    "You are an assistant that extracts structured information from CVs. "
    "Given a CV, return a JSON object with these fields: name, current_role, "
    "total_years_experience, career_level, employment_history, education, "
    "industries, functional_expertise, methods, tools, languages, "
    "certifications. Output valid JSON only, no commentary."
)
RETRY_NUDGE = "Your previous response was not valid JSON. Output valid JSON only."

# response_format={"type": "json_object"} is "JSON mode" — looser than Strict
# Mode Structured Outputs. It guarantees parseable JSON but does NOT enforce
# field names or types. This is the right level for a zero-shot baseline: the
# pipeline's quality advantage from schema enforcement should be visible in
# the comparison, not hidden by the baseline failing to return JSON at all.

EXPECTED_FIELDS = [
    "name", "current_role", "total_years_experience", "career_level",
    "employment_history", "education", "industries", "functional_expertise",
    "methods", "tools", "languages", "certifications",
]
SET_FIELDS = {
    "industries", "functional_expertise", "methods",
    "tools", "languages", "certifications",
}


# --- Helpers ------------------------------------------------------------------

def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _str(v) -> str:
    """Strict scalar-to-string. Empty for None, bool, or non-scalar types."""
    if isinstance(v, str):
        return v.strip()
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return str(v)
    return ""


def _serialize_employment(value) -> str:
    """Serialize employment_history. Only exact keys are honored:
    employer, role, start_date, end_date, responsibilities. Key drift is
    a real baseline failure and is not repaired here."""
    if not isinstance(value, list):
        return value.strip() if isinstance(value, str) else ""
    entries = []
    for item in value:
        if not isinstance(item, dict):
            continue
        emp = _str(item.get("employer"))
        role = _str(item.get("role"))
        start = _str(item.get("start_date"))
        end = _str(item.get("end_date"))
        desc_raw = item.get("responsibilities")
        if isinstance(desc_raw, list):
            desc = ". ".join(_str(x) for x in desc_raw if _str(x))
        else:
            desc = _str(desc_raw)
        header = " — ".join(p for p in (emp, role) if p)
        date_range = f"({start} → {end})" if (start or end) else ""
        line = " ".join(p for p in (header, date_range) if p).strip()
        if desc:
            line = f"{line}\n{desc}" if line else desc
        if line:
            entries.append(line)
    return "\n\n".join(entries)


def _serialize_education(value) -> str:
    """Serialize education. Only exact keys are honored: institution,
    credential or degree (either is accepted as the system prompt did not
    disambiguate), field_of_study, start_date, end_date."""
    if not isinstance(value, list):
        return value.strip() if isinstance(value, str) else ""
    entries = []
    for item in value:
        if not isinstance(item, dict):
            continue
        inst = _str(item.get("institution"))
        cred = _str(item.get("credential")) or _str(item.get("degree"))
        field = _str(item.get("field_of_study"))
        start = _str(item.get("start_date"))
        end = _str(item.get("end_date"))
        cred_part = f"{cred} in {field}" if (cred and field) else (cred or field)
        header = " — ".join(p for p in (inst, cred_part) if p)
        date_range = f"({start} → {end})" if (start or end) else ""
        line = " ".join(p for p in (header, date_range) if p).strip()
        if line:
            entries.append(line)
    return "\n".join(entries)


def _serialize_set(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(x).strip() for x in value if str(x).strip())
    if isinstance(value, str):
        return value.strip()
    return ""


def _serialize_string(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def normalize_to_pipeline_shape(raw: dict, latency_ms: int, usage) -> dict:
    out: dict = {}
    for field in EXPECTED_FIELDS:
        v = raw.get(field, "")
        if field == "employment_history":
            out[field] = _serialize_employment(v)
        elif field == "education":
            out[field] = _serialize_education(v)
        elif field in SET_FIELDS:
            out[field] = _serialize_set(v)
        elif field == "total_years_experience":
            out[field] = v if isinstance(v, (int, float)) and not isinstance(v, bool) else _serialize_string(v)
        else:
            out[field] = _serialize_string(v)

    input_tokens = usage.prompt_tokens
    output_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens
    cost = (input_tokens * INPUT_PRICE_PER_1M + output_tokens * OUTPUT_PRICE_PER_1M) / 1_000_000
    out["latency_ms"] = latency_ms
    out["input_tokens"] = input_tokens
    out["output_tokens"] = output_tokens
    out["total_tokens"] = total_tokens
    out["cost_usd"] = f"{cost:.6f}"
    out["model"] = MODEL
    return out


def _call_openai(client: OpenAI, messages: list[dict]):
    return client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0,
        timeout=REQUEST_TIMEOUT,
    )


def extract_one(client: OpenAI, cv_text: str) -> tuple[dict, int, object, str | None]:
    """Return (parsed_json, latency_ms, usage, error). On any failure, error is set."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": cv_text},
    ]
    start = time.perf_counter()
    try:
        response = _call_openai(client, messages)
    except Exception as e:
        return {}, 0, None, f"openai api error: {e}"

    content = response.choices[0].message.content or ""
    try:
        parsed = json.loads(content)
        return parsed, int((time.perf_counter() - start) * 1000), response.usage, None
    except json.JSONDecodeError:
        pass

    messages.append({"role": "assistant", "content": content})
    messages.append({"role": "system", "content": RETRY_NUDGE})
    try:
        response = _call_openai(client, messages)
    except Exception as e:
        return {}, 0, None, f"retry api error: {e}"

    try:
        parsed = json.loads(response.choices[0].message.content or "")
        return parsed, int((time.perf_counter() - start) * 1000), response.usage, None
    except json.JSONDecodeError as e:
        return {}, 0, None, f"malformed JSON after retry: {e}"


def save_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


# --- Main ---------------------------------------------------------------------

def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set (environment or .env)", file=sys.stderr)
        return 1

    if not CV_DIR.exists():
        print(f"ERROR: {CV_DIR} not found", file=sys.stderr)
        return 1
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    client = OpenAI(api_key=api_key)

    all_cvs = sorted(CV_DIR.iterdir())
    pdfs = [p for p in all_cvs if p.suffix.lower() == ".pdf"]
    skipped = [p for p in all_cvs if p.suffix.lower() != ".pdf"]

    for skip in skipped:
        print(f"SKIP {skip.name} (not PDF — baseline matches v1 pipeline scope)")

    if not pdfs:
        print("No PDFs to process.")
        return 0

    total = len(pdfs)
    successes: list[str] = []
    failures: list[tuple[str, str]] = []
    total_cost = 0.0
    latencies: list[int] = []
    run_start = time.monotonic()

    for i, pdf in enumerate(pdfs, start=1):
        stem = pdf.stem
        try:
            cv_text = extract_pdf_text(pdf)
        except Exception as e:
            err = f"pdf parse error: {e}"
            save_json(OUTPUT_DIR / f"{stem}.error.json", {"file": pdf.name, "error": err})
            print(f"[{i}/{total}] {pdf.name} → FAIL ({err})")
            failures.append((pdf.name, err))
            if i < total:
                time.sleep(SLEEP_BETWEEN_REQUESTS)
            continue

        parsed, latency_ms, usage, err = extract_one(client, cv_text)
        if err is not None:
            save_json(OUTPUT_DIR / f"{stem}.error.json", {"file": pdf.name, "error": err})
            print(f"[{i}/{total}] {pdf.name} → FAIL ({err})")
            failures.append((pdf.name, err))
        else:
            payload = normalize_to_pipeline_shape(parsed, latency_ms, usage)
            save_json(OUTPUT_DIR / f"{stem}.json", [payload])
            cost = float(payload["cost_usd"])
            print(f"[{i}/{total}] {pdf.name} → OK ({latency_ms}ms, ${cost:.4f})")
            successes.append(pdf.name)
            latencies.append(latency_ms)
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
