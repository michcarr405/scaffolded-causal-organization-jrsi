from pathlib import Path
import csv, hashlib
ROOT=Path(__file__).resolve().parents[1]
MP=ROOT/'manifests/SHA256_MANIFEST.csv'
CI_ONLY='.github/workflows/rc4-clean-room-v2.yml'

def ignored(rel):
    parts=rel.parts
    s=rel.as_posix()
    if '.git' in parts or '__pycache__' in parts or '.pytest_cache' in parts: return True
    if s==CI_ONLY or s=='manifests/SHA256_MANIFEST.csv': return True
    if s.endswith('.pyc') or s=='.DS_Store': return True
    return False

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

rows=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file(): continue
    rel=p.relative_to(ROOT)
    if ignored(rel): continue
    rows.append((rel.as_posix(),sha(p),p.stat().st_size))
MP.parent.mkdir(parents=True,exist_ok=True)
with MP.open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['relative_path','sha256','bytes']); w.writerows(rows)
print(f'REFRESHED SHA256 MANIFEST: {len(rows)} files')
