#!/usr/bin/env python3
"""Refresh SHA256_MANIFEST.csv from Git-tracked files only (RC6)."""
from pathlib import Path
import csv, hashlib, subprocess
ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifests/SHA256_MANIFEST.csv"
EXCLUDED = {"manifests/SHA256_MANIFEST.csv", ".github/workflows/rc4-clean-room-v2.yml"}

raw = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
paths = sorted(x.decode("utf-8") for x in raw.split(b"\0") if x)
rows = []
for name in paths:
    if name in EXCLUDED:
        continue
    file = ROOT / name
    if not file.is_file():
        raise SystemExit("Missing tracked release file: " + name)
    data = file.read_bytes()
    rows.append({"relative_path": name, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
with MANIFEST.open("w", newline="") as fp:
    writer = csv.DictWriter(fp, fieldnames=["relative_path", "sha256", "bytes"], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
print("REFRESHED SHA256 MANIFEST:", len(rows), "Git-tracked files")
print("Inspect the diff before committing. This operation does not change tracked source assets.")
