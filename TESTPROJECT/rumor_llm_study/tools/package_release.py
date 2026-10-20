"""Build a whitelisted archive, then execute its offline tests from a fresh folder."""
from pathlib import Path
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "deliverables"
out.mkdir(exist_ok=True)
destination = out / "LLM_Agent_代码与数据_ZetaTechs.zip"
files = [ROOT / name for name in [".gitignore", "README.md", "MODEL_GUIDE.md", "provider_notes.md",
    "requirements.txt", "pyproject.toml", "run.py", "test_all.py", "start.ps1",
    "开始离线验证.cmd", "开始API测试.cmd"]]
for folder, patterns in {"src":["*.py"], "tests":["*.py"], "tools":["*.py"],
                         "config":["*.json"], "verification":["*.json", "*.log", "*.md"]}.items():
    for pattern in patterns:
        files.extend((ROOT / folder).rglob(pattern))
data = ROOT / "data/imported"
files.extend(data / name for name in ["import_report.json", "ready_events.json", "missing_source_text.csv", "event_index.csv"])
for event in sorted(data.glob("event_*")):
    if event.is_dir(): files.extend([event / "event.json", event / "profiles.jsonl"])
files = sorted(set(p for p in files if p.name != "packaging_report.json"))
for path in files:
    if not path.is_file(): raise FileNotFoundError(path)
    rel = path.relative_to(ROOT)
    assert not {"_private", "outputs", "__pycache__", ".audit_dependencies"}.intersection(rel.parts)
    # Only print filenames on detection; never echo possible credentials.
    if re.search(rb"sk-[A-Za-z0-9]{24,}", path.read_bytes()):
        raise RuntimeError(f"Potential credential detected; archive not created: {rel}")
manifest = [{"path":p.relative_to(ROOT).as_posix(), "bytes":p.stat().st_size,
             "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for path in files: z.write(path, "rumor_llm_study/" + path.relative_to(ROOT).as_posix())
    z.writestr("rumor_llm_study/FILE_MANIFEST.json", json.dumps(manifest, ensure_ascii=False, indent=2))
with tempfile.TemporaryDirectory(prefix="rumor_release_") as tmp:
    with zipfile.ZipFile(destination) as z:
        assert z.testzip() is None
        z.extractall(tmp)
    unpacked = Path(tmp) / "rumor_llm_study"
    env = dict(os.environ); env["PYTHONDONTWRITEBYTECODE"] = "1"
    for name, args in [("unit_tests", ["test_all.py"]),
                       ("event_check", ["run.py", "check", "--event", "data/imported/event_052/event.json"]),
                       ("batch_estimate", ["run.py", "estimate", "--events", "75"])]:
        result = subprocess.run([sys.executable, *args], cwd=unpacked, env=env,
            capture_output=True, encoding="utf-8", errors="replace")
        if result.returncode:
            raise RuntimeError(f"Extracted {name} failed: {result.stdout}\n{result.stderr}")
        print(f"Extracted {name}: PASS", flush=True)
    ready = json.loads((unpacked / "data/imported/ready_events.json").read_text())
    assert len(ready) == 75 and all((unpacked / "data/imported" / p).exists() for p in ready)
report = {"archive":destination.name, "file_count_before_manifest":len(files),
          "extracted_unit_tests_passed":True, "extracted_event_check_passed":True,
          "extracted_estimate_passed":True, "ready_event_paths":75,
          "private_archives_included":False, "credential_pattern_scan_passed":True,
          "http_requests_during_packaging":0}
report_text = json.dumps(report, ensure_ascii=False, indent=2)
(ROOT / "verification/packaging_report.json").write_text(report_text, encoding="utf-8")
with zipfile.ZipFile(destination, "a", zipfile.ZIP_DEFLATED) as z:
    z.writestr("rumor_llm_study/verification/packaging_report.json", report_text)
digest = hashlib.sha256(destination.read_bytes()).hexdigest()
(out / "SHA256.txt").write_text(digest + "  " + destination.name + "\n", encoding="utf-8")
print(json.dumps({"archive":str(destination), "bytes":destination.stat().st_size,
                  "sha256":digest, **report}, ensure_ascii=True, indent=2))
