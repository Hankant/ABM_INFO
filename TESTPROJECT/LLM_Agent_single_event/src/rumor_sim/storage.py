"""Atomic round journals and reproducible exports. Pure standard library."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import uuid


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def atomic_json(path, value, compressed=False):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        data = (canonical(value) + "\n").encode("utf-8")
        if compressed: data = gzip.compress(data, compresslevel=2, mtime=0)
        with tmp.open("wb") as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists(): tmp.unlink()


def read_json(path):
    path = Path(path)
    if path.suffix == ".gz":
        return json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
    return json.loads(path.read_text(encoding="utf-8-sig"))


class RunStore:
    """Each committed round is one atomic file containing state and its log rows.

    A failed round has no journal file; the provider success cache can safely reuse
    already answered requests after restart. CSV/JSONL are derived exports only.
    """
    def __init__(self, path, manifest, initial, prefix_path=None):
        self.path = Path(path).resolve()
        self.path.mkdir(parents=True, exist_ok=True)
        self.round_dir = self.path / "rounds"; self.round_dir.mkdir(exist_ok=True)
        manifest = dict(manifest)
        manifest["initial_round"] = initial["round"]
        manifest["initial_state_hash"] = digest(initial)
        manifest["prefix_path"] = os.path.relpath(Path(prefix_path).resolve(), self.path) if prefix_path else None
        mp = self.path / "manifest.json"
        if mp.exists():
            if read_json(mp) != manifest:
                raise ValueError("Existing run uses different inputs/code/provider. Use a new output directory; no overwrite.")
            if not (self.path / "initial.json.gz").exists():
                raise ValueError("Existing manifest has no initial snapshot")
            if digest(read_json(self.path / "initial.json.gz")) != manifest["initial_state_hash"]:
                raise ValueError("Initial snapshot hash mismatch")
        else:
            atomic_json(self.path / "initial.json.gz", initial, compressed=True)
            atomic_json(mp, manifest)
        self.manifest = manifest

    def latest(self):
        files = sorted(self.round_dir.glob("*.json.gz"))
        if not files: return read_json(self.path / "initial.json.gz")
        indices = [int(f.name.split(".")[0]) for f in files]
        expected = list(range(self.manifest["initial_round"] + 1, indices[-1] + 1))
        if indices != expected: raise ValueError("Round journal gap detected; refusing an incomplete resume")
        return read_round(files[-1])["state"]

    def state_at(self, t):
        if t == self.manifest["initial_round"]: return read_json(self.path / "initial.json.gz")
        return read_round(self.round_dir / f"{t:05d}.json.gz")["state"]

    def commit(self, envelope):
        t = envelope["state"]["round"]
        dst = self.round_dir / f"{t:05d}.json.gz"
        if dst.exists():
            if digest(read_round(dst)["state"]) != digest(envelope["state"]):
                raise ValueError("Refusing a different second commit for the same round")
            return
        if t != self.latest()["round"] + 1:
            raise ValueError("Round commits must be consecutive")
        atomic_json(dst, {**envelope, "state_hash": digest(envelope["state"])}, compressed=True)

    def set_status(self, status, **details):
        atomic_json(self.path / "status.json", {"status": status, **details})


def read_round(path):
    path = Path(path)
    record = read_json(path)
    state = record["state"]
    expected_round = int(path.name.split(".")[0])
    if state["round"] != expected_round or len(state["round_metrics"]) != expected_round:
        raise ValueError("Checkpoint round or cumulative-metrics length mismatch")
    if digest(state) != record.get("state_hash"):
        raise ValueError("Checkpoint state hash mismatch")
    return record


def _records(path, stop=None):
    path = Path(path).resolve(); manifest = read_json(path / "manifest.json")
    initial_round = manifest["initial_round"]
    if manifest.get("prefix_path"):
        prefix = (path / manifest["prefix_path"]).resolve()
        yield from _records(prefix, stop=initial_round)
    for f in sorted((path / "rounds").glob("*.json.gz")):
        t = int(f.name.split(".")[0])
        if stop is not None and t > stop: break
        yield read_round(f)


def export_run(run_path, summary, individual):
    """Rebuild exports, avoiding duplicate rows even after interruption/restart."""
    run_path = Path(run_path)
    out = run_path / "exports"; out.mkdir(exist_ok=True)
    atomic_json(out / "summary.json", summary)
    json_streams = {name: (out / f"{name}.jsonl").open("w", encoding="utf-8", newline="\n")
                    for name in ("posts", "exposures", "decisions", "round_metrics")}
    state_handle = (out / "states.csv").open("w", encoding="utf-8-sig", newline="")
    writer = None
    try:
        initial = read_json(run_path / "initial.json.gz")
        # The base source post appears once, including for a branch export.
        source_posts = [p for p in initial["posts"].values() if p.get("kind") == "rumor_original"]
        for post in source_posts: json_streams["posts"].write(canonical(post) + "\n")
        for rec in _records(run_path):
            for name in ("posts", "exposures", "decisions"):
                for row in rec[name]: json_streams[name].write(canonical(row) + "\n")
            metrics = rec["state"].get("round_metrics", [])
            if metrics: json_streams["round_metrics"].write(canonical(metrics[-1]) + "\n")
            for row in rec["states"]:
                if writer is None:
                    writer = csv.DictWriter(state_handle, fieldnames=list(row)); writer.writeheader()
                writer.writerow(row)
    finally:
        state_handle.close()
        for handle in json_streams.values(): handle.close()
    fields = ["agent_id", "group", "government_round", "first_reject", "event", "duration", "followup_complete"]
    with (out / "tbu_individual.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(individual)
    return out
