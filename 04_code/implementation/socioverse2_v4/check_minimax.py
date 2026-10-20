"""One opt-in paid request with synthetic input, no account roster or study data."""
import json
from datetime import datetime
from pathlib import Path
from socioverse.schemas import Observation
from llm_client import LiveClient
from run import defaults, LOGS


def main():
    cfg = defaults()
    cfg.update(json.loads(Path(__file__).with_name("minimax.config.json").read_text(encoding="utf-8")))
    cfg["max_requests"] = 1
    audit = LOGS / ("minimax-connection-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f"))
    audit.mkdir(parents=True)
    ob = Observation(agent_id="TEST", step=0,
        local_physical={"persona": {"group": "outside"}, "current_belief": "unjudged", "memory": []},
        local_information={"posts": [{"content_id": "TEST001", "root_content_id": "TEST001",
            "text": "This is a synthetic API connection test.", "comments": [], "can_repost": False}]})
    print(f"Audit: {audit}", flush=True)
    client = LiveClient(cfg, audit)
    answer, _, meta = client.decide(ob, 'This is an API connectivity test. Return exactly this JSON object: {"ok":true}.\n{当前观察}')
    if answer != {"ok": True}:
        raise ValueError("Response arrived but did not pass the synthetic JSON check")
    print(json.dumps({"connection_check": "passed", "requested_model": cfg["model"],
        "returned_model": meta["returned_model"], "input_tokens": meta["actual_input_tokens"],
        "output_tokens": meta["actual_output_tokens"], "note": "Not a simulation or behavioral validation"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
