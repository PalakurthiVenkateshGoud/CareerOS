import re
import os
import time
import asyncio
import hashlib
from abc import ABC, abstractmethod
from typing import Callable, Optional
from pydantic import BaseModel, field_validator
import json
from openai import AsyncOpenAI, RateLimitError
from config import settings

# Persistent on-disk cache for LLM responses, keyed by (agent name + prompt +
# schema). During development you re-run the same resume/role over and over —
# this means identical requests are answered from disk instead of burning
# through Groq/Gemini/OpenRouter's daily free-tier quotas on every restart.
_CACHE_PATH = os.path.join(os.path.dirname(__file__), "..", ".llm_cache.json")


def _cache_key(agent_name: str, user_prompt: str, json_schema_hint: str) -> str:
    raw = f"{agent_name}::{user_prompt}::{json_schema_hint}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _load_cache() -> dict:
    if os.path.exists(_CACHE_PATH):
        try:
            with open(_CACHE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception as e:
        print(f"[base_agent] Failed to write LLM cache: {e}")

# Groq — separate infra from OpenRouter's free pool, low latency. Tried first.
GROQ_CLIENT = (
    AsyncOpenAI(api_key=settings.GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")
    if getattr(settings, "GROQ_API_KEY", "")
    else None
)

# Gemini — Google AI Studio's OpenAI-compatible endpoint. This is your OWN
# dedicated free quota, completely separate from OpenRouter's shared/communal
# free-model pool (the 50-requests/day account-wide cap you kept hitting).
# Tried second, after Groq and before OpenRouter.
GEMINI_CLIENT = (
    AsyncOpenAI(
        api_key=settings.GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    if getattr(settings, "GEMINI_API_KEY", "")
    else None
)

OPENROUTER_CLIENT = AsyncOpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)

GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
]

OPENROUTER_MODELS = [
    "qwen/qwen3-coder:free",
    "nvidia/nemotron-nano-9b-v2:free",
    "nvidia/nemotron-3-nano-30b-a3b:free",
    "meta-llama/llama-3.2-3b-instruct:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "nousresearch/hermes-3-llama-3.1-405b:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-26b-a4b-it:free",
    "google/gemma-4-31b-it:free",
]

# Optional guaranteed safety net, tried only after every free model has
# failed. Set settings.FALLBACK_PAID_MODEL to an OpenRouter model id
# (e.g. "openai/gpt-4o-mini") to enable. Leave unset/empty to disable —
# behavior is then identical to having no safety net.
FALLBACK_PAID_MODEL = getattr(settings, "FALLBACK_PAID_MODEL", "") or None

DEFAULT_COOLDOWN_SECONDS = 45
DEFAULT_TIMEOUT = 15
DEFAULT_MAX_TOKENS = 8000

# Per-model overrides. Smaller / lower-TPM models need smaller token budgets
# and shorter timeouts:
#   - Lower max_tokens avoids tripping Groq's per-model TPM cap (the 413
#     "Request too large" error seen on llama-3.1-8b-instant) and keeps
#     generation fast on small free OpenRouter models.
#   - Shorter timeouts mean a model that's genuinely struggling fails fast
#     instead of eating a full 15s out of an already-long fallback chain.
MODEL_CONFIG: dict[str, dict] = {
    "llama-3.1-8b-instant": {"max_tokens": 2000, "timeout": 10},
    "meta-llama/llama-3.2-3b-instruct:free": {"max_tokens": 1500, "timeout": 10},
    "liquid/lfm-2.5-1.2b-instruct:free": {"max_tokens": 1200, "timeout": 10},
    "nvidia/nemotron-nano-9b-v2:free": {"max_tokens": 2000, "timeout": 10},
    "nvidia/nemotron-3-nano-30b-a3b:free": {"max_tokens": 2000, "timeout": 10},
}

# After this many consecutive rate limits from the SAME client, stop trying
# further models on that client for the rest of THIS call. Seeing back-to-back
# 429s across many different free models on one provider usually means an
# account/IP-wide throttle, not nine independent per-model issues — grinding
# through the rest of that provider's list one by one just adds latency with
# no chance of success.
CONSECUTIVE_RATE_LIMIT_FAIL_FAST = 2

# Shared across every agent/request in this process.
_model_cooldown_until: dict[str, float] = {}


def _config_for(model: str) -> dict:
    cfg = MODEL_CONFIG.get(model, {})
    return {
        "max_tokens": cfg.get("max_tokens", DEFAULT_MAX_TOKENS),
        "timeout": cfg.get("timeout", DEFAULT_TIMEOUT),
    }


def _cooldown_seconds_from_error(e: Exception, default: int) -> int:
    try:
        resp = getattr(e, "response", None)
        if resp is not None:
            data = resp.json()
            retry_after = data.get("error", {}).get("metadata", {}).get("retry_after_seconds")
            if retry_after:
                return min(int(retry_after) + 2, 60)
    except Exception:
        pass
    return default


def _build_candidates() -> list[tuple[AsyncOpenAI, str]]:
    candidates: list[tuple[AsyncOpenAI, str]] = []

    if GROQ_CLIENT is not None:
        candidates += [(GROQ_CLIENT, m) for m in GROQ_MODELS]
    else:
        print("[base_agent] No GROQ_API_KEY set — skipping Groq")

    if GEMINI_CLIENT is not None:
        gemini_models = GEMINI_MODELS.copy()
        configured = getattr(settings, "GEMINI_MODEL", "")
        if configured and configured not in gemini_models:
            gemini_models.insert(0, configured)
        candidates += [(GEMINI_CLIENT, m) for m in gemini_models]
    else:
        print("[base_agent] No GEMINI_API_KEY set — skipping Gemini")

    or_models = OPENROUTER_MODELS.copy()
    if settings.OPENROUTER_MODEL not in or_models:
        or_models.insert(0, settings.OPENROUTER_MODEL)
    candidates += [(OPENROUTER_CLIENT, m) for m in or_models]

    # Guaranteed safety net — only reached once every free option above
    # has already failed.
    if FALLBACK_PAID_MODEL and FALLBACK_PAID_MODEL not in or_models:
        candidates.append((OPENROUTER_CLIENT, FALLBACK_PAID_MODEL))

    return candidates


class AgentResult(BaseModel):
    agent_name: str
    output: dict
    confidence: float
    reasoning: str
    assumptions: list[str] = []
    missing_data: list[str] = []

    @field_validator("assumptions", "missing_data", mode="before")
    @classmethod
    def _coerce_to_string_list(cls, value):
        """
        Weaker fallback models sometimes wrap each item in a dict
        (e.g. {"assumption": "..."} instead of a plain string). This
        normalizes any shape — string, dict, or list of strings/dicts —
        into a clean list[str] before pydantic validates it, so a single
        odd-shaped response doesn't crash the whole pipeline with a 500.
        """
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            for v in value.values():
                if isinstance(v, str):
                    return [v]
            return [json.dumps(value)]
        if isinstance(value, list):
            result = []
            for item in value:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    found = next((v for v in item.values() if isinstance(v, str)), None)
                    result.append(found if found else json.dumps(item))
                else:
                    result.append(str(item))
            return result
        return [str(value)]


class BaseAgent(ABC):
    name: str = "base_agent"
    system_prompt: str = ""

    async def call_llm(
        self,
        user_prompt: str,
        json_schema_hint: str,
        validate: Optional[Callable[[dict], bool]] = None,
    ) -> dict:
        """
        validate: optional callback run against the parsed JSON result.
        If it returns False, the result is treated as unusable (well-formed
        JSON that's empty or low-effort — a common failure mode with weak
        free-tier fallback models) and the next candidate model is tried,
        rather than returning a "successful" but useless result.
        """
        cache_key = _cache_key(self.name, user_prompt, json_schema_hint)
        cache = _load_cache()
        if cache_key in cache:
            print(f"[{self.name}] Cache hit — skipping LLM call entirely")
            return cache[cache_key]

        candidates = _build_candidates()

        now = time.monotonic()
        live = [(c, m) for c, m in candidates if _model_cooldown_until.get(m, 0) <= now]
        skipped = [m for c, m in candidates if (c, m) not in live]
        if skipped:
            print(f"[{self.name}] Skipping models still cooling down: {skipped}")

        ordered = live if live else candidates

        last_error = None
        # Tracks consecutive rate-limit failures per client (keyed by id())
        # within this single call, so we can fail fast on a saturated provider.
        consecutive_rate_limits: dict[int, int] = {}

        for client, model in ordered:
            client_key = id(client)

            if consecutive_rate_limits.get(client_key, 0) >= CONSECUTIVE_RATE_LIMIT_FAIL_FAST:
                print(f"[{self.name}] Skipping {model} — this provider looks rate-limited account-wide this request")
                continue

            cfg = _config_for(model)

            try:
                print(f"[{self.name}] Trying model: {model}")
                response = await asyncio.wait_for(
                    client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": self.system_prompt +
                             "\nAlways respond with ONLY valid, strict JSON (RFC 8259) matching "
                             "this structure: "
                             + json_schema_hint +
                             "\nInclude 'confidence' (0-1), 'reasoning' (string), "
                             "'assumptions' (list), and 'missing_data' (list) fields. "
                             "CRITICAL: Use double quotes for ALL JSON keys and string values. "
                             "Never use single quotes. No markdown code blocks. "
                             "No text before or after the JSON object."},
                            {"role": "user", "content": user_prompt}
                        ],
                        temperature=0.3,
                        max_tokens=cfg["max_tokens"],
                        response_format={"type": "json_object"},
                    ),
                    timeout=cfg["timeout"],
                )
                content = response.choices[0].message.content
                if content is None:
                    raise ValueError("Model returned empty content")
                result = self._extract_json(content)

                if validate is not None and not validate(result):
                    print(f"[{self.name}] {model} returned well-formed but empty/invalid JSON — trying next model")
                    consecutive_rate_limits[client_key] = 0
                    last_error = ValueError("Model returned an empty or invalid structured result")
                    continue

                print(f"[{self.name}] Success with model: {model}")
                _model_cooldown_until.pop(model, None)
                cache[cache_key] = result
                _save_cache(cache)
                return result

            except RateLimitError as e:
                cooldown = _cooldown_seconds_from_error(e, DEFAULT_COOLDOWN_SECONDS)
                print(f"[{self.name}] {model} rate limited — cooling down {cooldown}s")
                _model_cooldown_until[model] = time.monotonic() + cooldown
                consecutive_rate_limits[client_key] = consecutive_rate_limits.get(client_key, 0) + 1
                last_error = e
                continue

            except asyncio.TimeoutError as e:
                print(f"[{self.name}] {model} timed out after {cfg['timeout']}s")
                consecutive_rate_limits[client_key] = 0
                last_error = e
                continue

            except Exception as e:
                last_error = e
                consecutive_rate_limits[client_key] = 0
                print(f"[{self.name}] {model} error: {str(e)[:100]}")
                continue

        raise ValueError(f"[{self.name}] All models failed. Last error: {last_error}")

    @staticmethod
    def _extract_json(content: str) -> dict:
        content = content.strip()

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", content, re.DOTALL)
        if fence_match:
            try:
                return json.loads(fence_match.group(1))
            except json.JSONDecodeError:
                pass

        first_brace = content.find("{")
        last_brace = content.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            candidate = content[first_brace:last_brace + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        cleaned = re.sub(r",\s*([}\]])", r"\1", content)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        repaired = BaseAgent._attempt_truncation_repair(content)
        if repaired is not None:
            return repaired

        normalized = BaseAgent._normalize_quotes(content)
        if normalized != content:
            try:
                return json.loads(normalized)
            except json.JSONDecodeError:
                repaired = BaseAgent._attempt_truncation_repair(normalized)
                if repaired is not None:
                    return repaired

        raise ValueError(f"Could not parse JSON (length {len(content)}): {content[:300]}")

    @staticmethod
    def _normalize_quotes(content: str) -> str:
        result = []
        in_double = False
        escape = False
        for ch in content:
            if escape:
                result.append(ch)
                escape = False
                continue
            if ch == "\\":
                result.append(ch)
                escape = True
                continue
            if ch == '"':
                in_double = not in_double
                result.append(ch)
                continue
            if ch == "'" and not in_double:
                result.append('"')
                continue
            result.append(ch)
        return "".join(result)

    @staticmethod
    def _attempt_truncation_repair(content: str) -> dict | None:
        first_brace = content.find("{")
        if first_brace == -1:
            return None
        snippet = content[first_brace:]
        valid_end_chars = set(',":0123456789truefalsenul}]')

        for end in range(len(snippet) - 1, 0, -1):
            ch = snippet[end]
            if ch not in valid_end_chars:
                continue
            trimmed = snippet[:end + 1].rstrip()
            if trimmed.endswith(","):
                trimmed = trimmed[:-1]

            local_stack = []
            local_in_string = False
            local_escape = False
            valid = True
            for c in trimmed:
                if local_in_string:
                    if local_escape:
                        local_escape = False
                    elif c == "\\":
                        local_escape = True
                    elif c == '"':
                        local_in_string = False
                    continue
                if c == '"':
                    local_in_string = True
                elif c in "{[":
                    local_stack.append(c)
                elif c in "}]":
                    if local_stack:
                        local_stack.pop()
                    else:
                        valid = False
                        break

            if not valid or local_in_string:
                continue

            closing = "".join("}" if b == "{" else "]" for b in reversed(local_stack))
            candidate = trimmed + closing
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

        return None

    @abstractmethod
    async def run(self, *args, **kwargs) -> AgentResult:
        ...