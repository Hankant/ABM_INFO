# Decision provider contract

`src/rumor_sim/provider.py` uses the Python standard library. The provider tests use injected fake transport or an offline urllib handler and make no network requests. Live endpoint checks, when performed by the orchestrating runner, are separate from these tests.

```python
from pathlib import Path
from rumor_sim.provider import HTTPDecisionProvider, MockDecisionProvider

with HTTPDecisionProvider(llm_config, Path("runs/study-001/provider")) as provider:
    envelope = provider.decide(view, call_identity)
    decision = envelope["decision"]
    audit = envelope["audit"]
```

The caller must close the provider in a `finally` block or use a context manager. `HTTPDecisionProvider` exclusively locks its work directory for its lifetime. After an abnormal process termination, inspect the PID in `.provider.lock` and confirm that process has ended before manually removing that stale lock. Never reset `budget.json` to resume work. `MockDecisionProvider` has the same call interface, consumes no HTTP budget, and returns synthetic protocol fixtures with an explicit `provider_mode="mock"` audit marker.

## Input and validation

`view` is the frozen user input dictionary. It must contain `visible_posts`, a list of post dictionaries containing string `post_id`, and `eligible_repost_post_ids`. An empty visible feed is an engine no-op; do not call the provider. The remainder of the view is included unchanged in the user message. The engine must supply only actually visible information.

`call_identity` is a nonempty stable string incorporating run ID, event, environment/model repeat seed, initial condition, round, and agent. This study's runner includes the policy branch in the run ID: different policy suffixes never share model-response cache entries. Only the pre-intervention parent snapshots are reused. Independent repeats also have different identities. Python's built-in process-dependent `hash()` must not construct the identity.

The returned decision has exactly six fields:

- `belief_score`: integer 0–100; booleans and floats are rejected.
- `action`: `silent`, `comment`, or `repost`.
- `target_post_id`: null for silent; a currently visible post otherwise.
- `public_stance`: `none` for silent; `support`, `oppose`, or `uncertain` otherwise.
- `comment`: empty for silent/repost; a nonempty string of at most 80 Unicode characters for comment.
- `reason`: a nonempty string of at most 40 Unicode characters.

Repost targets must also occur in `eligible_repost_post_ids`. Private scores and public stances are intentionally not forced to agree. Duplicate fields, extra fields and Markdown-wrapped JSON fail validation. `validate_decision(raw_or_dict, view)` is available for a second engine-side check.

## Actual HTTP parameters

Defaults are the requested `https://api.zetatechs.com/v1` endpoint and `deepseek-v4-flash` alias. Credentials are read only from `RUMOR_LLM_API_KEY`; they are not written to configuration, logs, or cache. The client records the actual model identifier returned by the provider, without claiming that it identifies immutable weights or authenticates a third-party alias.

Relevant configuration fields are:

```json
{
  "base_url": "https://api.zetatechs.com/v1",
  "model": "deepseek-v4-flash",
  "temperature": 0.7,
  "top_p": 0.8,
  "max_output_tokens": 384,
  "timeout_seconds": 90,
  "max_retries": 2,
  "max_api_requests": 1000,
  "json_mode": true,
  "extra_body": {"thinking": {"type": "disabled"}}
}
```

The client sends `/chat/completions`, `max_tokens`, and `response_format={"type":"json_object"}`. `extra_body` is merged into the request body but cannot replace model, messages, credentials, controlled sampling fields or tool configuration. It does not silently remove unsupported parameters. Explicit compatibility changes (`json_mode=false`, `omit_temperature=true`, `omit_top_p=true`, or revised `extra_body`) alter the recorded request-parameter hash. On 2026-10-12 the configured ZetaTechs endpoint successfully returned a valid six-field decision with these parameters and model ID. This verifies one request/response, not a full empirical trajectory or the server's internal parameter handling.

## Retry, budget, and recovery

`max_retries=2` means at most three HTTP requests for one decision. Invalid structured output receives a repair request stating the exact validation issue; retryable HTTP failures use the same bounded attempt allowance. HTTP 401 and 403 are terminal: one failed request is counted and automatic retries stop immediately. All redirects are refused, including redirects to the same origin, so the Authorization header cannot be forwarded to another endpoint; a redirect failure is also terminal. Configure a verified intended endpoint explicitly instead of relying on redirection. Failure raises `ProviderError`, and the engine must not commit the incomplete round. There is no rule-based, uncertain-belief, or fabricated-output fallback.

Every HTTP attempt is reserved and durably counted in `budget.json` before network I/O, including failures and repairs. A crash between reservation and I/O can conservatively count one untransmitted request; it cannot reset or evade the cap. `max_api_requests` is the absolute cumulative cap for that work directory. Reopening the provider retains its consumed count. The orchestrator must reuse that directory for all branches of the same capped study.

`http_audit.jsonl` records reserved requests without headers, raw completion content, errors, usage, actual model IDs, repair counts, hashes, and cache hits. If an error echoes the API key, it is redacted. Saved successful responses are replayed only when the frozen input hash, provider/system-prompt parameter hash, and keyed call identity all match. Replayed results consume no HTTP budget. Environment seeds alone do not guarantee deterministic responses from a remote model.

`audit` includes `raw_output`, `provider_model`, `usage`, `input_hash`, `request_hash`, `cache_hit`, `attempts`, requested model, actual request parameters, and cumulative HTTP count. On cache replay, `attempts=0` and `original_attempts` retain the original success metadata. Errors remain in the provider audit even if a complete simulation round was never committed.

## Offline verification

From the project root, with `src` on `PYTHONPATH`:

```powershell
$env:PYTHONPATH = "$PWD/src"
python -m unittest discover -s tests -p test_provider.py -v
```

The tests cover strict field semantics, score boundaries, visibility and repost restrictions, two repairs, failed-call budget accounting across restarts, exclusive locking, cache identity isolation, no-key cache replay, missing-key behavior, secret redaction, blocked request-field overrides, and deterministic mock protocol coverage.
