"""Read-only subscription diagnostic; never prints key, headers, or raw response."""
import json
import os
import httpx


def main():
    key = (os.environ.get("RUMOR_LLM_API_KEY") or "").strip()
    if not key:
        raise SystemExit("No key in this PowerShell session. Run ./Configure-MiniMax.ps1 first.")
    if key.startswith("Bearer ") or key[:1] in ("\"", "'") or any(c.isspace() for c in key):
        raise SystemExit("Key includes Bearer, quotes or whitespace. Re-enter only the key itself.")
    url = "https://www.minimax.cn/v1/token_plan/remains"
    try:
        response = httpx.get(url, headers={"Authorization": "Bearer " + key}, timeout=30,
                             follow_redirects=False)
    except httpx.HTTPError as exc:
        print(json.dumps({"check": "subscription_status", "error_type": type(exc).__name__}))
        return
    try:
        body = response.json()
    except ValueError:
        body = {}
    base = body.get("base_resp", {}) if isinstance(body, dict) else {}
    code = base.get("status_code") if isinstance(base, dict) else None
    if not isinstance(code, int):
        code = None
    result = {"check": "subscription_status", "http_status": response.status_code,
              "service_status_code": code, "generation_requests": 0}
    if response.status_code == 200 and code == 0:
        result["interpretation"] = "Subscription endpoint accepted the key. Chat/model permission remains untested."
    elif response.status_code == 401 or code in (1004, 2049):
        result["interpretation"] = "Subscription endpoint rejected authentication. Check key validity and CN/global issuing region."
    else:
        result["interpretation"] = "Not enough evidence to confirm authentication; inspect status codes with provider support."
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
