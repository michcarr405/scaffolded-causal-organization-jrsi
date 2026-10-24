#!/usr/bin/env python3
"""RC5 Table S2 remaining-campaign evidence discovery; never infers a PASS.

Usage: python scripts/rc5_discover_remaining_campaigns.py
Creates work/rc5_s2_discovery.json and prints candidate paths per Table S2 row.
Searches filenames/paths, not content; manual source/parameter matching is still required.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"work/rc5_s2_discovery.json"
CAMPAIGNS={
 "model_b_four_scaffold": ["model_b","four_scaffold"],
 "model_b_primary_7point": ["model_b","scaffold_strength"],
 "model_b_fidelity": ["model_b","transmission_fidelity"],
 "model_b_acquisition_expression": ["reduced_theory","t3"],
 "model_b_scalar_distance": ["reduced_theory","t4"],
 "model_b_directional": ["reduced_theory","t5"],
 "catalytic_initial_prospective": ["catalytic","original_prospective"],
 "lattice_mapping": ["lattice","post_confirmatory_mapping"],
 "lattice_sentinel": ["lattice","post_confirmatory_mapping"],
}
EXTS={".py",".json",".yaml",".yml",".csv",".toml",".md"}
EXCLUDE={"site-packages",".git","__pycache__","work",".venv"}
files=[p for p in ROOT.rglob("*") if p.is_file() and p.suffix.lower() in EXTS and not set(p.relative_to(ROOT).parts).intersection(EXCLUDE)]
report={"schema_version":"1.0","purpose":"discovery not verification","campaigns":{}}
for name,tokens in CAMPAIGNS.items():
    candidates=[]
    for p in files:
        rel=str(p.relative_to(ROOT)); lower=rel.lower()
        if all(t in lower for t in tokens):
            typ=("executable" if p.suffix==".py" else "configuration_or_data")
            candidates.append({"path":rel,"kind":typ})
    report["campaigns"][name]={"status":"DISCOVERY_ONLY","search_tokens":tokens,"candidates":candidates[:250],"candidate_count":len(candidates),"requires":"inspect frozen run configurations, seeds, settings, and inferential code against S2"}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,indent=2)+"\n")
for key,value in report["campaigns"].items():
    print(f"{key}: {value['candidate_count']} candidate paths (NOT VERIFIED)")
print("Wrote",OUT)
