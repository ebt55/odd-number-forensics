"""Run prompt conditions across models; one JSONL row per sample.

Examples
    python run.py --models ollama:qwen3:14b --conditions spine_ieven_rodd --n 3 --out runs/smoke.jsonl
    python run.py --models ollama:qwen3:14b --conditions all_spine --n 10 --out runs/pilot.jsonl
    python run.py --followup runs/pilot.jsonl --k 10 --models ollama:qwen3:14b \
        --conditions spine_ieven_rodd --out runs/followup.jsonl
    python run.py --print-prompt abl_inert --paraphrase 3
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

import conditions as C
import providers as P
from extract import extract_answer, split_thinking

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "runs" / "manifest.log"
MAX_TOKENS_THINK = 6000


@dataclass
class Job:
    model: str
    spec: P.ModelSpec
    condition: str
    paraphrase: int
    sample_idx: int
    messages: list[dict[str, str]]
    system: str | None
    max_tokens: int
    source_condition: str | None = None
    source_run_id: str | None = None


@dataclass
class Writer:
    path: Path
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def write(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=True)
        async with self.lock:
            with self.path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def job_key(model: str, condition: str, paraphrase: int, sample_idx: int,
            source_condition: str | None) -> tuple:
    return (model, condition, paraphrase, sample_idx, source_condition)


def load_done_keys(path: Path) -> set[tuple]:
    """Keys already recorded with error == null, so a re-run resumes."""
    done: set[tuple] = set()
    if not path.exists():
        return done
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("error") is None:
                done.add(job_key(row.get("model", ""), row.get("condition", ""),
                                 int(row.get("paraphrase", 0)), int(row.get("sample_idx", 0)),
                                 row.get("source_condition")))
    return done


def read_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows


def build_jobs(models: list[str], condition_ids: list[str], n: int) -> list[Job]:
    jobs: list[Job] = []
    for model in models:
        spec = P.parse_model_spec(model)
        for condition in condition_ids:
            for sample_idx in range(n):
                # Fixed-text cells have exactly one prompt form, so they record P1
                # rather than rotating through paraphrases that do not exist.
                paraphrase = 1 if C.is_fixed_text(condition) else C.paraphrase_for(sample_idx)
                prompt = C.build_prompt(condition, paraphrase)
                max_tokens = MAX_TOKENS_THINK if spec.think else prompt.max_tokens
                jobs.append(Job(model=model, spec=spec, condition=condition,
                                paraphrase=paraphrase, sample_idx=sample_idx,
                                messages=[{"role": "user", "content": prompt.user}],
                                system=prompt.system, max_tokens=max_tokens))
    return jobs


def build_followup_jobs(models: list[str], condition_ids: list[str], src: Path,
                        k: int) -> list[Job]:
    """Replay completed transcripts from `src` and append the compliance question."""
    rows = read_rows(src)
    jobs: list[Job] = []
    for model in models:
        spec = P.parse_model_spec(model)
        for condition in condition_ids:
            matched = [r for r in rows
                       if r.get("model") == model and r.get("condition") == condition
                       and r.get("error") is None and (r.get("response_text") or "").strip()]
            if not matched:
                print(f"[warn] no source rows for {model} / {condition} in {src}")
            for row in matched[:k]:
                reply, _ = split_thinking(row.get("response_text") or "")
                messages = list(row.get("messages") or [])
                messages.append({"role": "assistant", "content": reply})
                messages.append({"role": "user", "content": C.FOLLOWUP_QUESTION})
                jobs.append(Job(model=model, spec=spec, condition="followup_compliance",
                                paraphrase=int(row.get("paraphrase", 1)),
                                sample_idx=int(row.get("sample_idx", 0)),
                                messages=messages, system=row.get("system"),
                                max_tokens=MAX_TOKENS_THINK if spec.think else C.MAX_TOKENS_LONG,
                                source_condition=condition,
                                source_run_id=row.get("run_id")))
    return jobs


async def run_job(client: httpx.AsyncClient, job: Job, run_id: str, temperature: float,
                  writer: Writer) -> dict[str, Any]:
    started = time.perf_counter()
    # Fixed-text replication cells can trigger very long thinking on reasoning models.
    timeout_s = P.TIMEOUT_THINK_S if C.is_fixed_text(job.condition) else None
    result = await P.call_model(client, job.spec, job.messages, job.system,
                                temperature, job.max_tokens, timeout_s)
    latency = round(time.perf_counter() - started, 3)

    content = result.response_text or ""
    thinking = result.thinking_text or ""
    if not thinking:
        _, embedded = split_thinking(content)
        thinking = embedded
    mode = C.extract_mode_for(job.source_condition or job.condition)
    ext = extract_answer(content, mode)

    record: dict[str, Any] = {
        "run_id": run_id,
        "ts": now_iso(),
        "model": job.model,
        "provider": job.spec.provider,
        "condition": job.condition,
        "paraphrase": job.paraphrase,
        "sample_idx": job.sample_idx,
        "temperature": temperature,
        "messages": job.messages,
        "system": job.system,
        "response_text": content,
        "thinking_text": thinking,
        "extracted_number": ext.extracted_number,
        "parity": ext.parity,
        "in_range": ext.in_range,
        "extraction": ext.extraction,
        "extract_mode": mode,
        "ambiguous": ext.ambiguous,
        "error": result.error,
        "usage": result.usage,
        "latency_s": latency,
    }
    if result.reasoning_unsupported:
        record["reasoning_unsupported"] = True
    if result.bumped_max_tokens:
        record["bumped_max_tokens"] = True
    if result.reasoning_effort is not None:
        record["reasoning_effort"] = result.reasoning_effort
    if result.thinking_shape is not None:
        record["thinking_shape"] = result.thinking_shape
    if result.served_model is not None:
        record["served_model"] = result.served_model
    if job.source_condition is not None:
        record["source_condition"] = job.source_condition
        record["source_run_id"] = job.source_run_id

    await writer.write(record)
    status = "err" if result.error else "ok "
    detail = (result.error or "")[:90] if result.error else \
        f"{ext.extracted_number} ({ext.parity}) [{ext.extraction}]" \
        + (" +bump" if result.bumped_max_tokens else "")
    print(f"[{status}] {job.model} {job.condition} P{job.paraphrase} "
          f"#{job.sample_idx} {latency:6.1f}s -> {detail}", flush=True)
    return record


async def run_all(jobs: list[Job], out: Path, temperature: float) -> list[dict[str, Any]]:
    run_id = datetime.now().strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:6]
    writer = Writer(out)
    print(f"run_id={run_id} jobs={len(jobs)} out={out}")
    async with httpx.AsyncClient() as client:
        tasks = [run_job(client, job, run_id, temperature, writer) for job in jobs]
        return list(await asyncio.gather(*tasks))


def append_manifest(argv: list[str]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"{now_iso()}\t{' '.join(argv)}\n")


def ollama_reachable() -> bool:
    try:
        httpx.get("http://localhost:11434/api/tags", timeout=5.0)
        return True
    except Exception:  # noqa: BLE001
        return False


def preflight(models: list[str]) -> list[P.ModelSpec]:
    """Parse specs and fail fast on missing keys / unreachable ollama."""
    specs = [P.parse_model_spec(m) for m in models]
    problems = [msg for msg in (P.missing_key_message(s) for s in specs) if msg]
    if any(s.provider == "ollama" for s in specs) and not ollama_reachable():
        problems.append("ollama: http://localhost:11434 is unreachable. "
                        "Start it with `ollama serve` and re-run.")
    if problems:
        print("Cannot start:")
        for msg in problems:
            print("  - " + msg)
        sys.exit(2)
    return specs


def parse_args(argv: list[str]) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Odd-number condition runner")
    ap.add_argument("--models", help="comma list of provider:model_id[@think]")
    ap.add_argument("--conditions", help="all_spine | all_abl | all_probe | all | comma list")
    ap.add_argument("--n", type=int, default=10, help="samples per cell (default 10)")
    ap.add_argument("--out", help="output jsonl path")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--followup", help="source jsonl to replay for followup_compliance")
    ap.add_argument("--k", type=int, default=10, help="followup: rows per model/condition")
    ap.add_argument("--print-prompt", dest="print_prompt",
                    help="print one assembled prompt and exit")
    ap.add_argument("--paraphrase", type=int, default=1, help="with --print-prompt (1|2|3)")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = parse_args(argv)

    if args.print_prompt:
        prompt = C.build_prompt(args.print_prompt, args.paraphrase)
        print(f"=== condition={args.print_prompt} paraphrase=P{args.paraphrase} "
              f"max_tokens={prompt.max_tokens} ===")
        if prompt.system:
            print(f"--- system ---\n{prompt.system}")
            print("--- user ---")
        print(prompt.user)
        print("=== end ===")
        return 0

    missing = [name for name in ("models", "conditions", "out") if not getattr(args, name)]
    if missing:
        print("missing required argument(s): " + ", ".join("--" + m for m in missing))
        return 2

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    condition_ids = C.resolve_conditions(args.conditions)
    append_manifest(["run.py"] + argv)
    preflight(models)

    out = Path(args.out)
    if not out.is_absolute():
        out = Path.cwd() / out
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.followup:
        src = Path(args.followup)
        if not src.is_absolute():
            src = Path.cwd() / src
        if not src.exists():
            print(f"followup source not found: {src}")
            return 2
        jobs = build_followup_jobs(models, condition_ids, src, args.k)
    else:
        jobs = build_jobs(models, condition_ids, args.n)

    done = load_done_keys(out)
    todo = [j for j in jobs
            if job_key(j.model, j.condition, j.paraphrase, j.sample_idx,
                       j.source_condition) not in done]
    skipped = len(jobs) - len(todo)
    if skipped:
        print(f"resume: skipping {skipped} already-complete sample(s)")
    if not todo:
        print("nothing to do")
        return 0

    records = asyncio.run(run_all(todo, out, args.temperature))
    errors = sum(1 for r in records if r.get("error"))
    print(f"done: {len(records)} sample(s), {errors} error(s) -> {out}")
    return 1 if errors == len(records) and records else 0


if __name__ == "__main__":
    sys.exit(main())
