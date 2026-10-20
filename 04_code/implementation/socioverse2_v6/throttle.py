"""Shared durable rate-limit gate. No credentials, response text or raw headers."""
import math
import threading
import time
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from pathlib import Path

from model import dump, read_json


def safe_response_metadata(response):
    headers = getattr(response, "headers", {}) or {}
    result = {}
    # Parse only a retry duration. Never retain arbitrary header values.
    value = headers.get("retry-after")
    if value is not None:
        try:
            seconds = float(value)
        except (TypeError, ValueError):
            try:
                seconds = parsedate_to_datetime(value).timestamp() - time.time()
            except (TypeError, ValueError, OverflowError):
                seconds = None
        if seconds is not None and math.isfinite(seconds):
            result["retry_after_seconds"] = max(0., seconds)
    return result


class RateGate:
    def __init__(self, config, audit, event):
        self.cfg, self.event = config, event
        self.path = Path(audit) / "rate-limit-state.json"
        self.cv = threading.Condition()
        self.active = 0
        self.halted = False
        self.state = read_json(self.path) if self.path.exists() else {
            "effective_concurrency": config.get("max_concurrency", 1),
            "cooldown_until": 0., "next_dispatch_at": 0., "limit_events": 0}
        self.state["effective_concurrency"] = min(
            self.state["effective_concurrency"], config.get("max_concurrency", 1))

        self.state.setdefault("success_streak", 0)
        self.state.setdefault("recovery_since", time.time())
        self.state.setdefault("success_times", [])
        self.state.setdefault("dispatch_spacing", config.get("rate_limit_spacing_seconds", 1.) if self.state["limit_events"] else 0.)

    def failed(self):
        with self.cv:
            self.state["success_streak"] = 0
            self.state["recovery_since"] = time.time()
            dump(self.path, self.state)

    def succeeded(self):
        # Only new validated/cached decisions count, never cache replay or HTTP200 alone.
        with self.cv:
            now = time.time()
            self.state["success_times"] = [t for t in self.state["success_times"] if now-60 < t <= now] + [now]
            self.state["success_streak"] += 1
            old = self.state["effective_concurrency"]
            ceiling = self.cfg.get("max_concurrency", 1)
            if (not self.halted and old < ceiling and now >= self.state["cooldown_until"]
                    and self.state["success_streak"] >= self.cfg.get("rate_recovery_successes", 20)
                    and now-self.state["recovery_since"] >= self.cfg.get("rate_recovery_seconds", 60.)):
                self.state["effective_concurrency"] = old+1
                self.state["success_streak"] = 0
                self.state["recovery_since"] = now
                self.state["dispatch_spacing"] = 0. if old+1 == ceiling else self.state["dispatch_spacing"] / 2
                self.event("rate_concurrency_recovered", old_concurrency=old,
                           effective_concurrency=old+1, dispatch_spacing=self.state["dispatch_spacing"])
                self.cv.notify_all()
            self.event("decision_throughput", validated_decisions_last_60s=len(self.state["success_times"]),
                       effective_concurrency=self.state["effective_concurrency"], success_streak=self.state["success_streak"])
            dump(self.path, self.state)

    @contextmanager
    def slot(self):
        start = time.monotonic()
        with self.cv:
            announced = False
            while True:
                if self.halted:
                    raise RuntimeError("Global request gate halted; preserve cached outcomes")
                now = time.time()
                delay = max(self.state["cooldown_until"], self.state["next_dispatch_at"]) - now
                if delay <= 0 and self.active < self.state["effective_concurrency"]:
                    break
                if not announced:
                    self.event("rate_gate_wait", active_requests=self.active,
                               effective_concurrency=self.state["effective_concurrency"],
                               wait_seconds=max(0., delay))
                    announced = True
                self.cv.wait(timeout=min(max(delay, .05), 1.))
            self.active += 1
            spacing = self.state["dispatch_spacing"]
            self.state["next_dispatch_at"] = time.time() + spacing
            self.event("rate_gate_admitted", active_requests=self.active,
                       effective_concurrency=self.state["effective_concurrency"],
                       waited_seconds=round(time.monotonic()-start, 3))
        try:
            yield
        finally:
            with self.cv:
                self.active -= 1
                self.cv.notify_all()

    def limited(self, failures, retry_after=None):
        with self.cv:
            old = self.state["effective_concurrency"]
            self.state["effective_concurrency"] = max(1, old//2)
            base = self.cfg.get("rate_limit_wait_seconds", 2.)
            maximum = self.cfg.get("rate_limit_max_wait_seconds", 60.)
            delay = min(maximum, base * 2**min(failures-1, 8))
            if retry_after is not None:
                delay = max(delay, retry_after)  # Honor the provider; no short-circuit cap.
            self.state["cooldown_until"] = max(self.state["cooldown_until"], time.time()+delay)
            self.state["success_streak"] = 0
            self.state["recovery_since"] = self.state["cooldown_until"]
            self.state["dispatch_spacing"] = self.cfg.get("rate_limit_spacing_seconds", 1.)
            self.state["limit_events"] += 1
            dump(self.path, self.state)
            self.event("rate_limit_cooldown", retry_index=failures, wait_seconds=delay,
                       old_concurrency=old, effective_concurrency=self.state["effective_concurrency"],
                       active_requests=self.active, cooldown_until=self.state["cooldown_until"])
            print(f"Rate limit: global wait {delay:.1f}s; concurrency {old}->{self.state['effective_concurrency']}", flush=True)
            self.cv.notify_all()

    def halt(self):
        with self.cv:
            self.halted = True
            self.cv.notify_all()
