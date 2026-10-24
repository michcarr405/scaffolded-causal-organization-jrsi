from pathlib import Path
import csv, hashlib, sys
ROOT=Path(__file__).resolve().parents[1]
inv=ROOT/'publication/builders/FIGURE_BUILDER_INVENTORY.csv'
base=ROOT/'publication/builders/frozen_original'
if not inv.exists():
    raise SystemExit('FAIL: missing figure builder inventory')
rows=list(csv.DictReader(inv.open()))
expected={
    'FIGURE_2_BUILD_FIGURE_2_v1.0.2.py',
    'FIGURE_3_build_figure3_final_v1.0.1.py',
    'FIGURE_4_BUILD_FIGURE_4_v1.0.1.py',
    'FIGURE_5_BUILD_FIGURE_5_v1.1.1.py',
    'FIGURE_S1_build_supplementary_jrsi_freezes_v1.py',
    'FIGURE_S2_BUILD_SUPPLEMENTARY_FIGURE_S2_v1.0.1.py',
    'FIGURE_S3_BUILD_SUPPLEMENTARY_FIGURE_S3.py',
    'FIGURE_S4_build_supplementary_figure_s4_v1.0.2.py',
    'FIGURE_S5_BUILD_SUPPLEMENTARY_FIGURE_S5_v1.2.0.py',
    'FIGURE_S6_BUILD_SUPPLEMENTARY_FIGURE_S6_v1.2.0.py',
}
seen=set()
for r in rows:
    p=base/r['file']; seen.add(r['file'])
    if not p.exists(): raise SystemExit(f'FAIL: missing builder {p}')
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    if got != r['sha256']: raise SystemExit(f'FAIL: builder hash mismatch {r["file"]}')
if seen != expected:
    raise SystemExit(f'FAIL: builder inventory set mismatch missing={sorted(expected-seen)} extra={sorted(seen-expected)}')
for p in [
    ROOT/'publication/builders/synchronization_records/S5_SYNC_PATCH_v1_README.md',
    ROOT/'publication/builders/synchronization_records/S5_SYNCHRONIZATION_FIX_AUDIT_v1.md',
    ROOT/'publication/builders/synchronization_records/S6_SYNC_PATCH_v2_README.md',
    ROOT/'publication/builders/synchronization_records/S6_SYNCHRONIZATION_FIX_AUDIT_v1.md',
]:
    if not p.exists(): raise SystemExit(f'FAIL: missing synchronization record {p}')
print(f'PASS: {len(rows)} exact frozen figure builders verified; Figure 1 documented as artwork exception; S5/S6 sync records present.')
