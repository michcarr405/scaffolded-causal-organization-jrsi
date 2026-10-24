#!/usr/bin/env python3
"""RC5 Figure 3c label removal: rebuild, install, and refresh figure integrity records.

Run from repository root: python scripts/rc5_freeze_figure3.py
Requires packages in requirements.txt. Does not modify the historic v1.0.1 builder.
"""
from pathlib import Path
import csv
import hashlib
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "publication/builders/FIGURE_3_build_figure3_final_v1.0.2.py"
SUPPORT = ROOT / "publication/builders/builder_support/Figure_3"
FIG = ROOT / "publication/main_figures"
REFERENCE = SUPPORT / "reference.pdf"
HASHES = ROOT / "publication/provenance/FIGURE_ASSET_SHA256.csv"
ORCHESTRATOR = ROOT / "scripts/build_publication_figures.py"

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    assert BUILDER.exists() and SUPPORT.exists() and HASHES.exists()
    assert not any("ax.text(0.705, 0.825, 'revise'" in line for line in BUILDER.read_text().splitlines()), 'editorial arrow label remains in builder'
    with tempfile.TemporaryDirectory(prefix="rc5_figure3_") as tmp:
        wd = Path(tmp)
        shutil.copytree(SUPPORT / "sources", wd / "sources")
        shutil.copy2(BUILDER, wd / "FIGURE_3_build_figure3_final_v1.0.2.py")
        subprocess.run([sys.executable, str(wd / BUILDER.name)], cwd=wd, check=True)
        pdf = wd / "FIGURE_3_FINAL_v1.0.1.pdf"
        png = wd / "FIGURE_3_FINAL_v1.0.1.png"
        assert pdf.exists() and png.exists(), "builder did not produce Figure 3"
        import fitz
        from PIL import Image
        with fitz.open(pdf) as doc:
            assert len(doc)==1
            assert doc[0].rect.width > 100 and doc[0].rect.height > 100  # Overlaid source PDF retains invisible legacy text
        with Image.open(png) as im:
            im.verify()
        FIG.mkdir(exist_ok=True, parents=True)
        shutil.copy2(pdf, FIG/"Figure_3.pdf")
        shutil.copy2(png, FIG/"Figure_3.png")
        shutil.copy2(pdf, REFERENCE)
    with HASHES.open(newline="") as f:
        rdr=csv.DictReader(f)
        cols=rdr.fieldnames
        rows=list(rdr)
    for row in rows:
        if row["relative_path"] in ("publication/main_figures/Figure_3.pdf","publication/main_figures/Figure_3.png"):
            p=ROOT/row["relative_path"]
            row["sha256"]=digest(p)
            row["bytes"]=str(p.stat().st_size)
            row["source_document"]="RC5_Figure_3_builder_v1.0.2"
            row["source_page_1based"]="1"
            row["source_clip_points"]="not_applicable"
    with HASHES.open("w",newline="") as f:
        wr=csv.DictWriter(f,fieldnames=cols)
        wr.writeheader();wr.writerows(rows)
    s=ORCHESTRATOR.read_text()
    old='"Figure_3": "FIGURE_3_build_figure3_final_v1.0.1.py"'
    new='"Figure_3": "FIGURE_3_build_figure3_final_v1.0.2.py"'
    if old not in s and new not in s:
        raise RuntimeError("unexpected Figure 3 builder mapping")
    s=s.replace(old,new)
    s=s.replace('builder = BUILDERS / BUILDER_FILES[target]', 'builder = (REPO / "publication/builders" / BUILDER_FILES[target]) if target == "Figure_3" else BUILDERS / BUILDER_FILES[target]')
    ORCHESTRATOR.write_text(s)
    # The support-input manifest also freezes the Figure 3 reference PDF.
    manifest=ROOT/"publication/builders/builder_support/BUILDER_SUPPORT_SHA256.csv"
    with manifest.open(newline="") as f:
        rdr=csv.DictReader(f); fields=rdr.fieldnames; entries=list(rdr)
    for row in entries:
        if row["path"].endswith("/Figure_3/reference.pdf"):
            row["sha256"]=digest(REFERENCE)
            if "bytes" in fields:row["bytes"]=str(REFERENCE.stat().st_size)
    with manifest.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader();w.writerows(entries)
    subprocess.run([sys.executable,str(ROOT/"scripts/validate_publication_figures.py")],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/validate_figure_builders.py")],cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts/validate_figure_reproduction.py")],cwd=ROOT,check=True)
    print("RC5 FIGURE 3 REFREEZE PASS")

if __name__=="__main__":
    main()
