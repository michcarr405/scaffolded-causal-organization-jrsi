from pathlib import Path
import csv, hashlib, json, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def sha256(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def expected_figures():
    return [f'Figure_{i}' for i in range(1,6)] + [f'Figure_S{i}' for i in range(1,7)]

# Asset existence and format checks.
try:
    import fitz
except Exception as e:
    errors.append(f'PyMuPDF unavailable: {e}')
    fitz=None
try:
    from PIL import Image
except Exception as e:
    errors.append(f'Pillow unavailable: {e}')
    Image=None

for fig in expected_figures():
    base=ROOT/'publication'/('supplementary_figures' if fig.startswith('Figure_S') else 'main_figures')
    pdf=base/f'{fig}.pdf'; png=base/f'{fig}.png'
    for p in [pdf,png]:
        if not p.exists() or p.stat().st_size==0: errors.append(f'missing/empty asset {p.relative_to(ROOT)}')
    if fitz and pdf.exists():
        try:
            d=fitz.open(pdf)
            if len(d)!=1: errors.append(f'{pdf.relative_to(ROOT)} has {len(d)} pages, expected 1')
            if len(d)==1 and (d[0].rect.width < 100 or d[0].rect.height < 100): errors.append(f'implausible PDF geometry {pdf.relative_to(ROOT)}')
            d.close()
        except Exception as e: errors.append(f'invalid PDF {pdf.relative_to(ROOT)}: {e}')
    if Image and png.exists():
        try:
            with Image.open(png) as im:
                im.verify()
            with Image.open(png) as im:
                if im.width < 400 or im.height < 150: errors.append(f'implausible PNG geometry {png.relative_to(ROOT)}')
        except Exception as e: errors.append(f'invalid PNG {png.relative_to(ROOT)}: {e}')

# Asset hash inventory.
asset_manifest=ROOT/'publication/provenance/FIGURE_ASSET_SHA256.csv'
if not asset_manifest.exists(): errors.append('missing publication/provenance/FIGURE_ASSET_SHA256.csv')
else:
    rows=list(csv.DictReader(asset_manifest.open()))
    if len(rows)!=22: errors.append(f'figure asset hash inventory has {len(rows)} rows, expected 22')
    for r in rows:
        p=ROOT/r['relative_path']
        if not p.exists(): errors.append('hash inventory missing '+r['relative_path']); continue
        if sha256(p)!=r['sha256'] or p.stat().st_size!=int(r['bytes']): errors.append('figure asset hash mismatch '+r['relative_path'])

# Compact source table hashes.
st_manifest=ROOT/'publication/provenance/SOURCE_TABLE_SHA256.csv'
if not st_manifest.exists(): errors.append('missing publication/provenance/SOURCE_TABLE_SHA256.csv')
else:
    rows=list(csv.DictReader(st_manifest.open()))
    for r in rows:
        p=ROOT/r['relative_path']
        if not p.exists(): errors.append('source table missing '+r['relative_path']); continue
        if sha256(p)!=r['sha256'] or p.stat().st_size!=int(r['bytes']): errors.append('source table hash mismatch '+r['relative_path'])

# Panel mapping: figure coverage, publication-source paths, canonical-source paths, and builders where claimed.
mp=ROOT/'publication/provenance/FIGURE_PROVENANCE_MAP.csv'
if not mp.exists(): errors.append('missing publication/provenance/FIGURE_PROVENANCE_MAP.csv')
else:
    rows=list(csv.DictReader(mp.open()))
    figures={r['figure'] for r in rows}
    missing=set(expected_figures())-figures
    if missing: errors.append('provenance map missing figures: '+','.join(sorted(missing)))
    for r in rows:
        for fld in ['asset_pdf','asset_png']:
            p=ROOT/r[fld]
            if not p.exists(): errors.append(f"provenance {r['figure']}{r['panel']}: missing {r[fld]}")
        for fld in ['publication_source_paths','canonical_source_paths']:
            value=r[fld].strip()
            if value in {'','not_applicable'}: continue
            for rel in value.split(';'):
                rel=rel.strip()
                if rel and not (ROOT/rel).exists(): errors.append(f"provenance {r['figure']}{r['panel']}: absent {fld} path {rel}")
        b=r['builder_path_or_status'].strip()
        if b and b not in {'not_available_current','not_applicable','artwork_exception_no_native_builder'} and not (ROOT/b).exists(): errors.append(f"provenance {r['figure']}{r['panel']}: absent builder {b}")

# Extraction manifest must cover all figures.
em=ROOT/'publication/provenance/EXTRACTION_MANIFEST.json'
if not em.exists(): errors.append('missing publication/provenance/EXTRACTION_MANIFEST.json')
else:
    try:
        j=json.loads(em.read_text())
        got=set(j.get('figures',{}))
        missing=set(expected_figures())-got
        if missing: errors.append('extraction manifest missing: '+','.join(sorted(missing)))
    except Exception as e: errors.append(f'invalid extraction manifest: {e}')

print('PUBLICATION FIGURE VALIDATION:', 'PASS' if not errors else 'FAIL')
print(' - expected reader-facing figures: 11')
print(' - expected reader-facing figure assets: 22')
if errors:
    for e in errors[:100]: print(' -',e)
sys.exit(1 if errors else 0)
