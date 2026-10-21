from pathlib import Path
import csv,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]; mp=ROOT/'manifests/SHA256_MANIFEST.csv'; errors=[]
rows=list(csv.DictReader(mp.open()))
for r in rows:
    p=ROOT/r['relative_path']
    if not p.exists(): errors.append('missing '+r['relative_path']); continue
    b=p.read_bytes()
    if hashlib.sha256(b).hexdigest()!=r['sha256'] or len(b)!=int(r['bytes']): errors.append('mismatch '+r['relative_path'])
listed={r['relative_path'] for r in rows}; actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and p!=mp}
for x in sorted(actual-listed): errors.append('unlisted '+x)
for x in sorted(listed-actual): errors.append('listed absent '+x)
print('MANIFEST VALIDATION:', 'PASS' if not errors else 'FAIL', f'({len(rows)} files)')
for e in errors[:50]: print(' -',e)
sys.exit(1 if errors else 0)
