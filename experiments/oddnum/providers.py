"""Model providers: ollama (local), openrouter, anthropic.

A model is named by a spec string `provider:model_id[@think]`, split on the FIRST
colon only, e.g. `ollama:qwen3:14b`, `ollama:qwen3:14b@think`,
`openrouter:openai/gpt-5-mini`, `anthropic:claude-haiku-4-5`.

API keys are read from the process environment first, then from a `.env` file at
the repo root. Key values are never printed.
"""

from __future__ import annotations

import asyncio
import os
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"

OLLAMA_URL = "http://localhost:11434/api/chat"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
XAI_URL = "https://api.x.ai/v1/chat/completions"
ANTHROPIC_VERSION = "2023-06-01"

KEY_NAMES = {"openrouter": "OPENROUTER_API_KEY", "anthropic": "ANTHROPIC_API_KEY",
             "openai": "OPENAI_API_KEY", "xai": "XAI_API_KEY"}
PROVIDER_LIMITS = {"ollama": 2, "openrouter": 8, "anthropic": 4, "openai": 8, "xai": 4}

# OpenAI reasoning families: they take max_completion_tokens, reject `temperature`,
# and accept reasoning_effort. Everything else uses the classic parameters.
OPENAI_REASONING_RE = re.compile(r"^(gpt-5|gpt-4\.5|o1|o3|o4)", re.IGNORECASE)
# The o-series rejects effort "minimal", so its floor is "low" instead.
OPENAI_O_SERIES_RE = re.compile(r"^(o1|o3|o4)", re.IGNORECASE)
OPENAI_REASONING_MIN_TOKENS = 8000
EFFORT_DEFAULT = "minimal"
EFFORT_O_DEFAULT = "low"
EFFORT_THINK = "medium"
EFFORT_HIGH = "high"
# Model-spec suffixes. Both switch reasoning ON for every provider; the tier itself is
# only read by openai (see _call_openai), so `@high` behaves exactly like `@think`
# everywhere else.
EFFORT_SUFFIXES = {"@think": EFFORT_THINK, "@high": EFFORT_HIGH}

# Adaptive retry: a reply that stopped on a length limit is retried once with this
# budget (covers reasoning-by-default models we do not know about). On number-only
# cells a *non-empty* truncated reply is retried too, because a number cut in half
# ("24" -> "2") would otherwise be recorded as a clean answer.
BUMP_MAX_TOKENS = 8000
NUMBER_ONLY_MAX_TOKENS = 64   # mirrors conditions.MAX_TOKENS_SHORT
LENGTH_REASONS = {"length", "max_tokens", "max_output_tokens"}

TIMEOUT_S = 120.0
TIMEOUT_THINK_S = 300.0
RETRY_ATTEMPTS = 3
RETRY_STATUS = {408, 409, 425, 429, 500, 502, 503, 504, 529}

ANTHROPIC_THINK_BUDGET = 8000
ANTHROPIC_THINK_MAX_TOKENS = 12000

# The Claude 5 family rejects thinking.type "enabled" and wants
# thinking={"type":"adaptive"} + output_config={"effort": ...}.
# The version must be matched at the family position: `claude-sonnet-4-5-20250929`
# also contains "-5" but is Claude 4.5 and keeps the old enabled+budget shape.
ANTHROPIC_ADAPTIVE_RE = re.compile(r"^claude-[a-z]+-5(?:[-.]|$)", re.IGNORECASE)
ANTHROPIC_EFFORT_VOCAB = ("none", "minimal", "low", "medium", "high", "max")


# --------------------------------------------------------------------------- env


_dotenv_cache: dict[str, str] | None = None


def _load_dotenv() -> dict[str, str]:
    """Parse simple KEY=VALUE lines from the repo-root .env (cached)."""
    global _dotenv_cache
    if _dotenv_cache is None:
        values: dict[str, str] = {}
        if ENV_PATH.exists():
            for line in ENV_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                val = val.strip().strip('"').strip("'")
                values[key.strip()] = val
        _dotenv_cache = values
    return _dotenv_cache


def get_key(name: str) -> str | None:
    """Return an API key from process env, else from .env. Never logged."""
    val = os.environ.get(name)
    if val:
        return val.strip()
    val = _load_dotenv().get(name)
    return val.strip() if val else None


# ---------------------------------------------------------------- model specs


@dataclass(frozen=True)
class ModelSpec:
    raw: str
    provider: str
    model_id: str
    think: bool
    effort_tier: str | None = None   # "medium" (@think) / "high" (@high); openai only


def parse_model_spec(spec: str) -> ModelSpec:
    raw = spec.strip()
    body = raw
    think = False
    effort_tier: str | None = None
    for suffix, tier in EFFORT_SUFFIXES.items():
        if body.endswith(suffix):
            think = True
            effort_tier = tier
            body = body[: -len(suffix)]
            break
    provider, sep, model_id = body.partition(":")
    if not sep or not provider or not model_id:
        raise ValueError(f"bad model spec {spec!r}; "
                         f"expected provider:model_id[@think|@high]")
    if provider not in PROVIDER_LIMITS:
        raise ValueError(f"unknown provider {provider!r} in {spec!r}; "
                         f"expected one of {sorted(PROVIDER_LIMITS)}")
    return ModelSpec(raw=raw, provider=provider, model_id=model_id, think=think,
                     effort_tier=effort_tier)


def missing_key_message(spec: ModelSpec) -> str | None:
    """Return a human-readable problem string if this model cannot be called."""
    key_name = KEY_NAMES.get(spec.provider)
    if key_name is None:
        return None
    if get_key(key_name) is None:
        return (f"{spec.raw}: {key_name} is not set. Checked the process environment "
                f"and {ENV_PATH}. Add the key and re-run.")
    return None


# ---------------------------------------------------------------- concurrency


_semaphores: dict[str, asyncio.Semaphore] = {}


def semaphore_for(provider: str) -> asyncio.Semaphore:
    """Per-provider concurrency limit (created lazily inside the running loop)."""
    if provider not in _semaphores:
        _semaphores[provider] = asyncio.Semaphore(PROVIDER_LIMITS[provider])
    return _semaphores[provider]


# -------------------------------------------------------------------- calling


@dataclass
class Result:
    response_text: str = ""
    thinking_text: str = ""
    usage: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    reasoning_unsupported: bool = False
    bumped_max_tokens: bool = False
    effective_max_tokens: int = 0   # what we actually asked the provider for
    reasoning_effort: str | None = None   # the effort actually sent, when applicable
    thinking_shape: str | None = None     # anthropic: "adaptive" | "enabled"
    served_model: str | None = None       # model id the provider says actually answered


class HttpError(Exception):
    def __init__(self, status: int, body: str) -> None:
        super().__init__(f"HTTP {status}: {body[:400]}")
        self.status = status
        self.body = body


async def _post(client: httpx.AsyncClient, url: str, headers: dict[str, str],
                payload: dict[str, Any], timeout: float) -> dict[str, Any]:
    """POST with retries on transport errors, 5xx and 429. Raises on failure."""
    last: Exception | None = None
    for attempt in range(RETRY_ATTEMPTS):
        try:
            resp = await client.post(url, json=payload, headers=headers, timeout=timeout)
            if resp.status_code in RETRY_STATUS:
                raise HttpError(resp.status_code, resp.text)
            if resp.status_code >= 400:
                raise HttpError(resp.status_code, resp.text)
            return resp.json()
        except (httpx.TransportError, httpx.TimeoutException) as exc:
            last = exc
        except HttpError as exc:
            if exc.status not in RETRY_STATUS:
                raise
            last = exc
        if attempt < RETRY_ATTEMPTS - 1:
            await asyncio.sleep(2.0 ** attempt + random.random() * 0.25)
    assert last is not None
    raise last


def _looks_truncated(usage: dict[str, Any]) -> bool:
    """True when the provider says generation stopped at a token limit."""
    reasons = (usage.get("finish_reason"), usage.get("done_reason"), usage.get("stop_reason"))
    return any(str(r) in LENGTH_REASONS for r in reasons if r)


async def _dispatch(client: httpx.AsyncClient, spec: ModelSpec,
                    messages: list[dict[str, str]], system: str | None,
                    temperature: float, max_tokens: int, timeout: float) -> Result:
    if spec.provider == "ollama":
        return await _call_ollama(client, spec, messages, system, temperature, max_tokens, timeout)
    if spec.provider == "openrouter":
        return await _call_openrouter(client, spec, messages, system, temperature, max_tokens, timeout)
    if spec.provider == "anthropic":
        return await _call_anthropic(client, spec, messages, system, temperature, max_tokens, timeout)
    if spec.provider == "openai":
        return await _call_openai(client, spec, messages, system, temperature, max_tokens, timeout)
    if spec.provider == "xai":
        return await _call_xai(client, spec, messages, system, temperature, max_tokens, timeout)
    return Result(error=f"unknown provider {spec.provider!r}")


async def call_model(client: httpx.AsyncClient, spec: ModelSpec,
                     messages: list[dict[str, str]], system: str | None,
                     temperature: float, max_tokens: int,
                     timeout_s: float | None = None) -> Result:
    """Send one single-shot chat request. Never raises; errors land in Result.error.

    Retry once with a bigger budget when generation hit the token limit and either
    (a) the reply is empty (reasoning models burn the whole budget on hidden
    reasoning), or (b) this is a number-only cell, where a truncated non-empty reply
    is a half-written number masquerading as a clean answer.

    `timeout_s` overrides the per-call timeout (callers use it for cells that are
    expected to think for a long time).
    """
    timeout = timeout_s or (TIMEOUT_THINK_S if spec.think else TIMEOUT_S)
    async with semaphore_for(spec.provider):
        try:
            result = await _dispatch(client, spec, messages, system,
                                     temperature, max_tokens, timeout)
            empty = not (result.response_text or "").strip()
            number_only = max_tokens == NUMBER_ONLY_MAX_TOKENS
            needs_bump = (result.error is None
                          and _looks_truncated(result.usage)
                          and result.effective_max_tokens < BUMP_MAX_TOKENS
                          and (empty or number_only))
            if needs_bump:
                retry = await _dispatch(client, spec, messages, system, temperature,
                                        BUMP_MAX_TOKENS, TIMEOUT_THINK_S)
                if retry.error is None:
                    retry.bumped_max_tokens = True
                    return retry
            return result
        except Exception as exc:  # noqa: BLE001 - one row must not kill the run
            return Result(error=f"{type(exc).__name__}: {exc}"[:800])


async def _call_ollama(client: httpx.AsyncClient, spec: ModelSpec,
                       messages: list[dict[str, str]], system: str | None,
                       temperature: float, max_tokens: int, timeout: float) -> Result:
    msgs: list[dict[str, str]] = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    payload = {
        "model": spec.model_id,
        "messages": msgs,
        "stream": False,
        "think": spec.think,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    data = await _post(client, OLLAMA_URL, {}, payload, timeout)
    message = data.get("message") or {}
    content = message.get("content") or ""
    thinking = message.get("thinking") or ""
    usage = {k: data.get(k) for k in
             ("prompt_eval_count", "eval_count", "total_duration", "done_reason")
             if data.get(k) is not None}
    return Result(response_text=content, thinking_text=thinking, usage=usage,
                  effective_max_tokens=max_tokens, served_model=data.get("model"))


async def _call_openrouter(client: httpx.AsyncClient, spec: ModelSpec,
                           messages: list[dict[str, str]], system: str | None,
                           temperature: float, max_tokens: int, timeout: float) -> Result:
    key = get_key(KEY_NAMES["openrouter"])
    if not key:
        return Result(error=f"OPENROUTER_API_KEY is not set (checked env and {ENV_PATH})")
    msgs: list[dict[str, str]] = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    payload: dict[str, Any] = {
        "model": spec.model_id,
        "messages": msgs,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    reasoning_unsupported = False
    if spec.think:
        payload["reasoning"] = {"effort": "medium"}
        try:
            data = await _post(client, OPENROUTER_URL, headers, payload, timeout)
        except HttpError:
            payload.pop("reasoning", None)
            reasoning_unsupported = True
            data = await _post(client, OPENROUTER_URL, headers, payload, timeout)
    else:
        data = await _post(client, OPENROUTER_URL, headers, payload, timeout)

    if "error" in data and not data.get("choices"):
        return Result(error=f"openrouter error: {str(data['error'])[:400]}",
                      reasoning_unsupported=reasoning_unsupported)
    result = _parse_openai_response(data, max_tokens)
    result.reasoning_unsupported = reasoning_unsupported
    return result


def _parse_openai_response(data: dict[str, Any], effective_max_tokens: int) -> Result:
    """Parse an OpenAI-compatible chat completion (openai, openrouter, xai).

    Reasoning text may arrive as `message.reasoning` (openrouter),
    `message.reasoning_content` (xai) or a list of `reasoning_details`.
    """
    choices = data.get("choices") or [{}]
    message = choices[0].get("message") or {}
    content = message.get("content") or ""
    thinking = message.get("reasoning") or message.get("reasoning_content") or ""
    if not thinking and message.get("reasoning_details"):
        parts = [d.get("text", "") for d in message["reasoning_details"] if isinstance(d, dict)]
        thinking = "\n".join(p for p in parts if p)
    # finish_reason travels in `usage` so truncation is visible in every row.
    usage = dict(data.get("usage") or {})
    usage["finish_reason"] = choices[0].get("finish_reason")
    return Result(response_text=content, thinking_text=thinking, usage=usage,
                  effective_max_tokens=effective_max_tokens,
                  served_model=data.get("model"))


async def _call_openai(client: httpx.AsyncClient, spec: ModelSpec,
                       messages: list[dict[str, str]], system: str | None,
                       temperature: float, max_tokens: int, timeout: float) -> Result:
    key = get_key(KEY_NAMES["openai"])
    if not key:
        return Result(error=f"OPENAI_API_KEY is not set (checked env and {ENV_PATH})")
    msgs: list[dict[str, str]] = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    payload: dict[str, Any] = {"model": spec.model_id, "messages": msgs}
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}

    reasoning_family = bool(OPENAI_REASONING_RE.match(spec.model_id))
    effort: str | None = None
    if reasoning_family:
        # These models reject `temperature` and spend the budget on hidden reasoning,
        # so they get max_completion_tokens with a floor of 8000.
        effective = max(max_tokens, OPENAI_REASONING_MIN_TOKENS)
        payload["max_completion_tokens"] = effective
        if spec.effort_tier:
            effort = spec.effort_tier     # @think -> medium, @high -> high
        elif OPENAI_O_SERIES_RE.match(spec.model_id):
            effort = EFFORT_O_DEFAULT     # o-series rejects "minimal"
        else:
            effort = EFFORT_DEFAULT
        payload["reasoning_effort"] = effort
    else:
        effective = max_tokens
        payload["max_tokens"] = effective
        payload["temperature"] = temperature

    try:
        data = await _post(client, OPENAI_URL, headers, payload, timeout)
        reasoning_unsupported = False
    except HttpError as exc:
        if not (reasoning_family and "reasoning_effort" in exc.body):
            raise
        payload.pop("reasoning_effort", None)   # older reasoning models reject the field
        effort = None
        data = await _post(client, OPENAI_URL, headers, payload, timeout)
        reasoning_unsupported = True

    result = _parse_openai_response(data, effective)
    result.reasoning_unsupported = reasoning_unsupported
    result.reasoning_effort = effort
    return result


async def _call_xai(client: httpx.AsyncClient, spec: ModelSpec,
                    messages: list[dict[str, str]], system: str | None,
                    temperature: float, max_tokens: int, timeout: float) -> Result:
    """xAI is OpenAI-compatible. Grok-4+ reasons by default with no effort control,
    so an empty reply is handled by the adaptive bump in call_model()."""
    key = get_key(KEY_NAMES["xai"])
    if not key:
        return Result(error=f"XAI_API_KEY is not set (checked env and {ENV_PATH})")
    msgs: list[dict[str, str]] = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.extend(messages)
    payload: dict[str, Any] = {
        "model": spec.model_id,
        "messages": msgs,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    data = await _post(client, XAI_URL, headers, payload, timeout)
    if "error" in data and not data.get("choices"):
        return Result(error=f"xai error: {str(data['error'])[:400]}")
    return _parse_openai_response(data, max_tokens)


def _pick_effort_from_error(body: str, requested: str | None) -> str | None:
    """Pick a different effort value that the error message says is valid, if any."""
    if "effort" not in body.lower():
        return None
    quoted = re.findall(r'"([a-z_]+)"', body)
    found = [v for v in quoted if v in ANTHROPIC_EFFORT_VOCAB]
    if not found:
        found = [v for v in ANTHROPIC_EFFORT_VOCAB if re.search(rf"\b{v}\b", body)]
    found = [v for v in found if v != requested]
    if not found:
        return None
    for preferred in (EFFORT_THINK, EFFORT_HIGH, EFFORT_O_DEFAULT):
        if preferred in found:
            return preferred
    return found[0]


async def _call_anthropic(client: httpx.AsyncClient, spec: ModelSpec,
                          messages: list[dict[str, str]], system: str | None,
                          temperature: float, max_tokens: int, timeout: float) -> Result:
    key = get_key(KEY_NAMES["anthropic"])
    if not key:
        return Result(error=f"ANTHROPIC_API_KEY is not set (checked env and {ENV_PATH})")
    payload: dict[str, Any] = {
        "model": spec.model_id,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if system:
        payload["system"] = system

    adaptive = bool(ANTHROPIC_ADAPTIVE_RE.match(spec.model_id))
    thinking_shape: str | None = None
    effort: str | None = None
    if spec.think:
        # Extended thinking requires the default temperature, so it is omitted here.
        payload["max_tokens"] = ANTHROPIC_THINK_MAX_TOKENS
        if adaptive:
            thinking_shape = "adaptive"
            effort = spec.effort_tier or EFFORT_THINK
            payload["thinking"] = {"type": "adaptive"}
            payload["output_config"] = {"effort": effort}
        else:
            thinking_shape = "enabled"
            payload["thinking"] = {"type": "enabled",
                                   "budget_tokens": ANTHROPIC_THINK_BUDGET}
    else:
        payload["temperature"] = temperature
    headers = {
        "x-api-key": key,
        "anthropic-version": ANTHROPIC_VERSION,
        "Content-Type": "application/json",
    }

    try:
        data = await _post(client, ANTHROPIC_URL, headers, payload, timeout)
    except HttpError as exc:
        # The API may enumerate the effort values it accepts; adapt once.
        alt = _pick_effort_from_error(exc.body, effort) if thinking_shape == "adaptive" else None
        if alt is None:
            raise
        effort = alt
        payload["output_config"] = {"effort": alt}
        data = await _post(client, ANTHROPIC_URL, headers, payload, timeout)

    text_parts, think_parts = [], []
    for block in data.get("content") or []:
        if block.get("type") == "text":
            text_parts.append(block.get("text", ""))
        elif block.get("type") == "thinking":
            think_parts.append(block.get("thinking", ""))
    usage = dict(data.get("usage") or {})
    usage["stop_reason"] = data.get("stop_reason")
    return Result(response_text="".join(text_parts), thinking_text="\n".join(think_parts),
                  usage=usage, effective_max_tokens=payload["max_tokens"],
                  reasoning_effort=effort, thinking_shape=thinking_shape,
                  served_model=data.get("model"))
