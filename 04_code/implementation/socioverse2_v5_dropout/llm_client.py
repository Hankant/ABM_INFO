"""Opt-in gateway calls, bounded attempts, persistent accounting, no fallback."""
from __future__ import annotations
import copy
import json
import os
import re
import time
from pathlib import Path
from model import dump, digest, read_json
from functools import lru_cache


class AgentRequestFailure(RuntimeError):
    """Persisted or current repeated transport failure."""


class QuotaPause(RuntimeError):
    """Rate/quota refusal: stop without automatic generation polling."""


class UncertainRequest(RuntimeError):
    """A dispatched request has no durable response; billing/outcome unknown."""


class FormatAttemptsExhausted(ValueError):
    """All permitted generations produced invalid JSON/schema."""


def parse_and_validate(text, ob, feed, memory):
    """Return a response or raise; semantic/visibility errors are NOT format retries."""
    answer = parse_json_object(text)
    validate_response(answer, ob, feed, memory)
    return answer


def is_format_error(exc):
    return isinstance(exc, json.JSONDecodeError) or str(exc) in {
        "LLM JSON root must be object", "LLM must return a judged belief",
        "invalid belief", "invalid action schema", "empty enabled comment", "invalid/invisible evidence"}


@lru_cache(maxsize=1)
def token_estimator():
    import tiktoken
    return tiktoken.get_encoding("cl100k_base")


def estimated_input_tokens(prompt):
    # Proxy tokenizer, NOT MiniMax's official tokenizer. Reserve 15% + chat overhead.
    import math
    return math.ceil(len(token_estimator().encode(prompt, disallowed_special=())) * 1.15) + 64


def validate_response(answer, ob, feed, memory):
    if ob.agent_id == "TEST":
        if answer != {"ok": True}:
            raise ValueError("synthetic connection check schema mismatch")
        return
    from model import normalize_answer
    if answer.get("belief") not in ("believe", "uncertain", "reject"):
        raise ValueError("LLM must return a judged belief")
    normalize_answer(answer, feed, memory, ob.local_physical["already_reposted"])


def parse_json_object(text):
    """Accept one JSON object, optionally wrapped in a single Markdown fence.

    Never extract an arbitrary object from prose or repair malformed JSON.
    The caller preserves the original response in the request audit.
    """
    text = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n\s*```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    answer = json.loads(text)
    if not isinstance(answer, dict):
        raise ValueError("LLM JSON root must be object")
    return answer


def request_options(config):
    options = dict(temperature=.7, top_p=.8, max_tokens=512)
    if config.get("api_profile") == "minimax_m3":
        if config["model"] != "MiniMax-M3":
            raise ValueError("minimax_m3 profile requires MiniMax-M3; review thinking/budget for another model")
        # Official MiniMax docs: M3 supports disabled thinking; M2.x/M3.1 do not.
        # JSON is requested by the V4 prompt and strictly parsed locally. Do not
        # assume an undocumented response_format parameter enforces JSON.
        options["extra_body"] = {"thinking": {"type": "disabled"}, "reasoning_split": True}
    else:
        options["response_format"] = {"type": "json_object"}
    return options


def render_prompt(template, ob, feed, memory, include_evidence=True):
    row = ob.local_physical["persona"]
    fields = ("sex", "location", "following_count", "followers_count", "statuses_count",
              "pre_event_experience", "sharing_habit", "initial_source_evaluation", "initial_government_evaluation")
    persona = {k: row.get(k) or "未提供" for k in fields}
    persona["关注原帖发布者"] = row["group"] == "inside"
    values = {"agent_id": ob.agent_id, "稳定个人资料": persona,
              "当前信念": ob.local_physical["current_belief"], "个人记忆": memory or "暂无",
              "当前观察": {"posts": feed, "eligible_repost_content_ids": [p["content_id"] for p in feed if p["can_repost"]]}}
    prompt = template
    for k, v in values.items():
        prompt = prompt.replace("{" + k + "}", v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))
    from model import exposure_summary
    summary = exposure_summary(ob.local_physical.get("exposure_history", {}), feed, ob.step)
    prompt += "\n【累计实际接触（包含本轮实际展示内容）】\n" + json.dumps(summary, ensure_ascii=False)
    prompt += "\n这些计数只包含你实际读到的帖子，不是全平台热度。各根内容分别统计，不能把转发次数直接视为支持次数。不同作者数不代表独立证实来源数；转发也不必表示赞同。结合具体文本、来源、已有判断和接触经历自行决定是否改变判断，不要求重复越多越相信，也不要求坚持原判断。"
    if include_evidence:
        from model import allowed_evidence_ids
        prompt += "\nallowed_evidence_ids=" + json.dumps(sorted(allowed_evidence_ids(feed, memory)), ensure_ascii=False) + "\nChoose evidence_ids only from this list."
    return prompt + "\n同一root_content_id全程最多转发一次；can_repost=false时不得再次转发，但仍可判断和评论。评论默认针对本轮第一条帖子。"


def prepare_prompt(template, ob, limit=4096, include_evidence=True):
    feed = copy.deepcopy(ob.local_information["posts"])
    memory = copy.deepcopy(ob.local_physical["memory"])
    while True:
        prompt = render_prompt(template, ob, feed, memory, include_evidence)
        reserved = estimated_input_tokens(prompt)
        if reserved <= limit:
            return prompt, feed, memory, reserved
        if memory:
            memory.pop(0)
        elif any(p["comments"] for p in feed):
            next(p for p in reversed(feed) if p["comments"])["comments"].pop()
        elif len(feed) > 1:
            feed.pop()
        else:
            raise ValueError("prompt_input_guard_exceeded_with_first_post")


class LiveClient:
    def __init__(self, config, audit_dir):
        from openai import OpenAI
        key = (os.environ.get("RUMOR_LLM_API_KEY") or "").strip()
        if not key:
            raise ValueError("Set RUMOR_LLM_API_KEY in the environment; no paid request was made")
        self.cfg = config
        self.audit = Path(audit_dir)
        self.cache = self.audit / "response_cache"
        self.cache.mkdir(parents=True, exist_ok=True)
        self.budget_path = self.audit / "budget.json"
        self.budget = read_json(self.budget_path) if self.budget_path.exists() else {
            "requests": 0, "input_reserved_units": 0, "output_reserved_tokens": 0,
            "actual_input_tokens": 0, "actual_output_tokens": 0, "usage_unknown_requests": 0}
        import httpx
        self.context = {}
        self.client = OpenAI(api_key=key, base_url=config["base_url"], timeout=90, max_retries=0,
            http_client=httpx.Client(event_hooks={"request": [self.on_request], "response": [self.on_response]}))

    def event(self, stage, **fields):
        from datetime import datetime, timezone
        with (self.audit / "request-events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps({"time":datetime.now(timezone.utc).isoformat(), **getattr(self,"context",{}),
                               "stage":stage, **fields}, ensure_ascii=True)+"\n")
            f.flush()
            os.fsync(f.fileno())

    def on_request(self, request):
        self.event("http_dispatch")

    def on_response(self, response):
        # Do not log any headers: they can include cookies or other secrets.
        self.event("response_headers_received", http_status=response.status_code)


    def decide(self, ob, template):
        prompt, feed, memory, reserved = prepare_prompt(template, ob)
        options = request_options(self.cfg)
        signature = digest({"prompt": prompt, "model": self.cfg["model"], "base_url": self.cfg["base_url"],
                            "request_options": options,
                            "agent_id": ob.agent_id, "step": ob.step})
        # Preserve exact prior prompts, cached responses and generation counts.
        legacy = prepare_prompt(template, ob, include_evidence=False)
        legacy_signature = digest({"prompt": legacy[0], "model": self.cfg["model"], "base_url": self.cfg["base_url"],
                                   "request_options": options, "agent_id": ob.agent_id, "step": ob.step})
        prior = [read_json(p) for p in self.audit.glob("request-*.json")]
        if any(p.get("prompt_sha256") == legacy_signature for p in prior):
            prompt, feed, memory, reserved = legacy
            signature = legacy_signature
        self.context = {"agent_id":ob.agent_id, "tick":ob.step, "prompt_sha256":signature}
        self.event("decision_start", memory_ticks=[m["tick"] for m in memory],
                   observed_ids=[p["content_id"] for p in feed], prompt_chars=len(prompt))
        cache_path = self.cache / f"{signature}.json"
        if cache_path.exists():
            saved = read_json(cache_path)
            validate_response(saved["answer"], ob, feed, memory)
            self.event("cache_reused")
            return saved["answer"], feed, {**saved["metadata"], "cached": True}
        # Count persisted generations across restarts; a restart never resets the limit.
        generations = 0
        max_generations = int(self.cfg.get("format_max_attempts", 4))
        for previous in sorted(self.audit.glob("request-*.json")):
            saved = read_json(previous)
            if saved.get("prompt_sha256") != signature:
                continue
            if saved.get("status") == "response_received" and saved.get("finish_reason") == "stop":
                generations += 1
                try:
                    answer = parse_and_validate(saved["raw_response"], ob, feed, memory)
                except ValueError as exc:
                    if not is_format_error(exc):
                        raise
                    dump(self.audit / "validation" / (previous.stem + ".json"), {
                        "status": "format_error", "error_type": type(exc).__name__,
                        "generation_attempt": generations, "prompt_sha256": signature})
                    continue
                recovered = {k: v for k, v in saved.items() if k not in ("prompt", "raw_response")}
                dump(cache_path, {"answer": answer, "metadata": recovered, "validation_status": "valid"})
                return answer, feed, {**recovered, "cached": True}
            if saved.get("status") == "pending_usage_unknown":
                raise UncertainRequest("Request outcome unknown; inspect audit before explicitly authorizing reissue")
            if saved.get("status") == "response_received":
                raise ValueError("LLM empty/refused/truncated response; no state committed")
        failed_transport = [r for r in prior if r.get("prompt_sha256") == signature
            and r.get("status") == "request_error"
            and r.get("diagnostic", {}).get("exception_type") in ("APITimeoutError", "APIConnectionError")]
        if len(failed_transport) >= 2:
            self.event("persisted_transport_exhausted", failures=len(failed_transport))
            raise AgentRequestFailure("Persisted repeated transport failure")
        if generations >= max_generations:
            raise FormatAttemptsExhausted(f"Format generation limit reached ({max_generations}); preserved for review")
        transport_retries = 0
        while generations < max_generations:
            b = self.budget
            if (b["requests"] >= self.cfg["max_requests"] or
                max(b["input_reserved_units"], b["actual_input_tokens"]) + reserved > 49_971_200 or
                b["output_reserved_tokens"] + 512 > 6_246_400):
                raise RuntimeError("LLM hard budget reached; preserve completed steps")
            b["requests"] += 1
            b["input_reserved_units"] += reserved
            b["output_reserved_tokens"] += 512
            dump(self.budget_path, b)  # persist BEFORE dispatch, including process interruption
            metadata = dict(agent_id=ob.agent_id, tick=ob.step, attempt=generations + 1,
                format_max_attempts=max_generations,
                request_number=b["requests"], requested_model=self.cfg["model"],
                prompt_sha256=signature, input_reserved_units=reserved,
                request_options=options,
                input_count_method="cl100k_base_estimate_15percent_plus64_not_minimax_tokenizer",
                trimmed_memory_count=len(ob.local_physical["memory"]) - len(memory),
                trimmed_post_count=len(ob.local_information["posts"]) - len(feed),
                trimmed_comment_count=sum(len(p["comments"]) for p in ob.local_information["posts"]) - sum(len(p["comments"]) for p in feed),
                used_memory_ticks=[m["tick"] for m in memory], cached=False)
            print(f"LLM request {b['requests']}: tick={ob.step}, agent={ob.agent_id}, memory={len(memory)}", flush=True)
            audit_path = self.audit / f"request-{b['requests']:06d}.json"
            self.context["request_number"] = b["requests"]
            self.event("request_start", generation_attempt=generations+1, transport_retry=transport_retries)
            started = time.monotonic()
            dump(audit_path, {**metadata, "status": "pending_usage_unknown", "prompt": prompt})
            try:
                response = self.client.chat.completions.create(
                    model=self.cfg["model"], messages=[{"role": "user", "content": prompt}],
                    **options)
            except Exception as exc:
                b["usage_unknown_requests"] += 1
                status = getattr(exc, "status_code", None)
                code = getattr(exc, "code", None)
                body = getattr(exc, "body", None)
                service_code = body.get("base_resp", {}).get("status_code") if isinstance(body, dict) and isinstance(body.get("base_resp"), dict) else None
                if not isinstance(service_code, int):
                    service_code = None
                # Whitelist machine-safe codes only: no raw headers, exception text or body.
                code = code if isinstance(code, str) and re.fullmatch(r"[a-zA-Z0-9_.-]{1,80}", code) else None
                diagnostic = dict(exception_type=type(exc).__name__, status_code=status,
                                  error_code=code, service_status_code=service_code, elapsed_seconds=round(time.monotonic() - started, 3))
                chain = []
                node = exc
                while node is not None and len(chain) < 8 and id(node) not in [x[0] for x in chain]:
                    chain.append((id(node), type(node).__name__))
                    node = node.__cause__ or node.__context__
                diagnostic["exception_chain"] = [x[1] for x in chain]
                diagnostic["timeout_phase"] = next((x[1] for x in chain if x[1] in ("ConnectTimeout", "ReadTimeout", "WriteTimeout", "PoolTimeout")), "unknown")
                self.event("request_error", **diagnostic)
                dump(audit_path, {**metadata, "status": "request_error", "diagnostic": diagnostic,
                                  "prompt": prompt})
                dump(self.budget_path, b)
                if status == 429 or service_code in (1002, 2056):
                    raise QuotaPause("Provider rate/quota limit; resume after quota is available") from None
                retryable = status in (429, 500, 502, 503, 504) or type(exc).__name__ in ("APITimeoutError", "APIConnectionError")
                # Unknown 570 is NOT automatically treated as transient.
                if transport_retries == 0 and retryable:
                    transport_retries += 1
                    time.sleep(1)
                    continue
                if type(exc).__name__ in ("APITimeoutError", "APIConnectionError"):
                    raise AgentRequestFailure("Repeated transport failure") from None
                hint = " Authentication failed: re-enter the API key and check its issuing platform/endpoint." if status == 401 else ""
                raise RuntimeError(
                    f"LLM request failed: HTTP {status}, {type(exc).__name__}."
                    f"{hint} Diagnostic: {audit_path}"
                ) from None
            self.event("response_body_received", elapsed_seconds=round(time.monotonic()-started,3))
            usage = response.usage
            base = getattr(response, "base_resp", None)
            if isinstance(base, dict) and base.get("status_code") in (1002, 2056):
                b["usage_unknown_requests"] += 1
                dump(self.budget_path, b)
                dump(audit_path, {**metadata, "status": "quota_paused", "service_status_code": base["status_code"]})
                raise QuotaPause("Provider rate/quota limit; resume after quota is available")
            it = getattr(usage, "prompt_tokens", None)
            ot = getattr(usage, "completion_tokens", None)
            if it is not None and ot is not None:
                b["actual_input_tokens"] += it
                b["actual_output_tokens"] += ot
                # Reservations remain a conservative spending guard, not reported usage.
            else:
                b["usage_unknown_requests"] += 1
            dump(self.budget_path, b)
            metadata.update(returned_model=response.model, actual_input_tokens=it, actual_output_tokens=ot,
                            elapsed_seconds=round(time.monotonic() - started, 3))
            choice = response.choices[0] if response.choices else None
            text = choice.message.content if choice else None
            dump(audit_path, {**metadata, "status": "response_received", "prompt": prompt,
                              "raw_response": text, "finish_reason": getattr(choice, "finish_reason", None)})
            if choice is None or choice.finish_reason != "stop" or not text:
                raise ValueError("LLM empty/refused/truncated response; no state committed")
            generations += 1
            try:
                answer = parse_and_validate(text, ob, feed, memory)
            except ValueError as exc:
                self.event("validation_failed", error_type=type(exc).__name__, retryable=is_format_error(exc))
                if not is_format_error(exc):
                    raise
                dump(self.audit / "validation" / (audit_path.stem + ".json"), {
                    "status": "format_error", "error_type": type(exc).__name__,
                    "generation_attempt": generations, "prompt_sha256": signature})
                if generations >= max_generations:
                    raise FormatAttemptsExhausted(f"Format generation limit reached ({max_generations}); preserved for review") from None
                print(f"Format retry: {ob.agent_id} tick={ob.step}, next attempt={generations + 1}/{max_generations}", flush=True)
                continue
            self.event("validation_passed")
            dump(cache_path, {"answer": answer, "metadata": metadata, "validation_status": "valid"})
            return answer, feed, metadata
        raise RuntimeError("unreachable")
