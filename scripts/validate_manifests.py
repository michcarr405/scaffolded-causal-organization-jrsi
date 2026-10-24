from pathlib import Path
import csv, hashlib, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'manifests/SHA256_MANIFEST.csv'
EXCLUDED = {'manifests/SHA256_MANIFEST.csv', '.github/workflows/rc4-clean-room-v2.yml'}

def tracked_paths():
    raw = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT)
    return {x.decode('utf-8') for x in raw.split(b'\0') if x and x.decode('utf-8') not in EXCLUDED}

def main():
    errors = []
    rows = list(csv.DictReader(MANIFEST.open(newline='')))
    listed = {r['relative_path'] for r in rows}
    tracked = tracked_paths()
    for row in rows:
        name = row['relative_path']
        file = ROOT / name
        if not file.is_file():
            errors.append('missing ' + name)
            continue
        data = file.read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256'] or len(data) != int(row['bytes']):
            errors.append('mismatch ' + name)
    for name in sorted(tracked - listed):
        errors.append('unlisted tracked ' + name)
    for name in sorted(listed - tracked):
        errors.append('listed not tracked ' + name)
    print('MANIFEST VALIDATION:', 'PASS' if not errors else 'FAIL', f'({len(rows)} files)')
    for error in errors[:50]:
        print(' -', error)
    if len(errors) > 50:
        print(f' ... {len(errors)-50} more errors')
    return bool(errors)

if __name__ == '__main__':
    sys.exit(main())
