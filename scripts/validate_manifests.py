from pathlib import Path
import csv, hashlib, subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'manifests/SHA256_MANIFEST.csv'
EXCLUDED = {'manifests/SHA256_MANIFEST.csv', '.github/workflows/rc4-clean-room-v2.yml'}
IGNORED_DIRS = {'.git', '.venv', '__pycache__', '.pytest_cache'}
IGNORED_FILES = {'.DS_Store'}

def inventory_paths():
    """Get tracked paths in a checkout or release-package paths without .git."""
    if (ROOT / '.git').exists():
        raw = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT)
        return {x.decode('utf-8') for x in raw.split(b'\0')
                if x and x.decode('utf-8') not in EXCLUDED}
    return {
        p.relative_to(ROOT).as_posix()
        for p in ROOT.rglob('*')
        if p.is_file()
        and not any(part in IGNORED_DIRS for part in p.relative_to(ROOT).parts)
        and p.name not in IGNORED_FILES
        and p.suffix != '.pyc'
        and p.relative_to(ROOT).as_posix() not in EXCLUDED
    }

def main():
    errors = []
    rows = list(csv.DictReader(MANIFEST.open(newline='')))
    listed = {r['relative_path'] for r in rows}
    actual = inventory_paths()
    for row in rows:
        name = row['relative_path']
        file = ROOT / name
        if not file.is_file():
            errors.append('missing ' + name)
            continue
        data = file.read_bytes()
        if hashlib.sha256(data).hexdigest() != row['sha256'] or len(data) != int(row['bytes']):
            errors.append('mismatch ' + name)
    for name in sorted(actual - listed):
        errors.append('unlisted ' + name)
    for name in sorted(listed - actual):
        errors.append('listed absent ' + name)
    print('MANIFEST VALIDATION:', 'PASS' if not errors else 'FAIL', f'({len(rows)} files)')
    for error in errors[:50]:
        print(' -', error)
    if len(errors) > 50:
        print(f' ... {len(errors) - 50} more errors')
    return bool(errors)

if __name__ == '__main__':
    sys.exit(main())
