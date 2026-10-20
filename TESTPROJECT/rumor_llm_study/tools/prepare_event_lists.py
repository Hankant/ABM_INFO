"""Generate batch lists and missing-text CSV from the imported data, without LLM."""
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / "data/imported"
ready, missing, index = [], [], []
old_index = {}
if (folder / "event_index.csv").exists():
    with (folder / "event_index.csv").open(encoding="utf-8-sig", newline="") as f:
        old_index = {row["event_id"]: row["source_filename"] for row in csv.DictReader(f)}
for path in sorted(folder.glob("event_*/event.json")):
    event = json.loads(path.read_text(encoding="utf-8"))
    provenance = path.parent / "_private/provenance.json"
    source_filename = old_index.get(event["event_id"], "")
    if provenance.exists():
        source_filename = json.loads(provenance.read_text(encoding="utf-8")).get("relative_source_path", "")
    index.append({"event_id": event["event_id"], "source_filename": source_filename,
                  "event_file": str(path.relative_to(folder)).replace("\\", "/"),
                  "status": "has_source_text" if event.get("rumor_text", "").strip() else "missing_source_text"})
    if event.get("rumor_text", "").strip(): ready.append(str(path.relative_to(folder)).replace("\\", "/"))
    else: missing.append({"event_id": event["event_id"], "event_file": str(path.relative_to(folder)),
        "source_filename": source_filename,
        "missing_field": "original_claim / rumor_text", "action": "补充原始正文后生成相同模板的实验纠正刺激"})
(folder / "ready_events.json").write_text(json.dumps(ready, indent=2), encoding="utf-8")
with (folder / "missing_source_text.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["event_id", "event_file", "source_filename", "missing_field", "action"])
    w.writeheader(); w.writerows(missing)
with (folder / "event_index.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["event_id", "source_filename", "event_file", "status"])
    w.writeheader(); w.writerows(index)
print(json.dumps({"ready": len(ready), "missing": len(missing)}))
