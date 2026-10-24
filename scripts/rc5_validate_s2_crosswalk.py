#!/usr/bin/env python3
"""RC5 source-link consistency gate. Runs offline at repository root.

Checks all 14 Table S2 entries, executable paths, concrete configuration paths,
and locally available explicit seed path references. Does not rerun simulations.
"""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1]
path=root/"docs/RC5_S2_EXECUTABLE_CONFIGURATION_CROSSWALK.json"
x=json.loads(path.read_text())
issues=[]
entries=x.get("entries",[])
ids=[e.get("id") for e in entries]
if len(entries)!=14 or len(ids)!=len(set(ids)):issues.append("Expected 14 unique entries")
if x.get("remaining_s2_rows_not_exhaustively_executable_mapped"):issues.append("Unmapped S2 rows remain")
for e in entries:
    name=e.get("id","UNKNOWN")
    p=e.get("entrypoint")
    if not isinstance(p,str) or not (root/p).is_file():issues.append(name+": missing executable "+repr(p))
    cfg=e.get("configuration")
    if not isinstance(cfg,str) or not cfg.strip():issues.append(name+": empty configuration evidence")
    elif cfg.startswith(("experiments/","provenance/")) and not (root/cfg).is_file():issues.append(name+": missing configuration "+cfg)
    ev=e.get("seed_evidence","")
    if not ev:issues.append(name+": missing seed evidence")
    # A path before an explanatory semicolon is exact and must exist.
    if isinstance(ev,str):
        for piece in ev.split(";"):
            q=piece.strip().split(" (",1)[0]
            if q.startswith(("experiments/","provenance/")) and not (root/q).is_file():
                issues.append(name+": missing seed file "+q)
    if not e.get("verified_fields"):issues.append(name+": missing evidence fields")
print("RC5 S2 LINK VALIDATION:", "PASS" if not issues else "FAIL")
print("Entries:",len(entries),"Unique executables:",len(set(e.get("entrypoint") for e in entries)))
for v in issues: print(" -",v)
sys.exit(bool(issues))
