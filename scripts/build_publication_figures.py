#!/usr/bin/env python3
"""Portable one-command rebuild of the manuscript publication figures.

Figure 1 is a documented artwork exception and is copied as a frozen reference.
Figures 2--5 and Supplementary Figures S1--S6 are rebuilt from frozen repository
inputs. The exact recovered builders in publication/builders/frozen_original are
never modified. Where historical scripts contain machine-specific absolute paths,
this orchestrator creates a temporary execution copy with path-only normalization.
The two documented S5/S6 reader-facing synchronization edits are likewise applied
only to temporary execution copies.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import fitz
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
BUILDERS = REPO / "publication" / "builders" / "frozen_original"
SUPPORT = REPO / "publication" / "builders" / "builder_support"
FROZEN_PUBLICATION = REPO / "publication"
DEFAULT_OUTPUT = REPO / "work" / "publication_rebuild"

TARGETS = ["Figure_2", "Figure_3", "Figure_4", "Figure_5",
           "Figure_S1", "Figure_S2", "Figure_S3", "Figure_S4", "Figure_S5", "Figure_S6"]

BUILDER_FILES = {
    "Figure_2": "FIGURE_2_BUILD_FIGURE_2_v1.0.2.py",
    "Figure_3": "FIGURE_3_build_figure3_final_v1.0.1.py",
    "Figure_4": "FIGURE_4_BUILD_FIGURE_4_v1.0.1.py",
    "Figure_5": "FIGURE_5_BUILD_FIGURE_5_v1.1.1.py",
    "Figure_S1": "FIGURE_S1_build_supplementary_jrsi_freezes_v1.py",
    "Figure_S2": "FIGURE_S2_BUILD_SUPPLEMENTARY_FIGURE_S2_v1.0.1.py",
    "Figure_S3": "FIGURE_S3_BUILD_SUPPLEMENTARY_FIGURE_S3.py",
    "Figure_S4": "FIGURE_S4_build_supplementary_figure_s4_v1.0.2.py",
    "Figure_S5": "FIGURE_S5_BUILD_SUPPLEMENTARY_FIGURE_S5_v1.2.0.py",
    "Figure_S6": "FIGURE_S6_BUILD_SUPPLEMENTARY_FIGURE_S6_v1.2.0.py",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def write_exec_copy(src: Path, dst: Path, replacements: list[tuple[str, str]], append_after: tuple[str, str] | None = None) -> list[str]:
    text = src.read_text()
    notes = []
    for old, new in replacements:
        if old not in text:
            raise RuntimeError(f"Expected execution-normalization token absent in {src.name}: {old}")
        text = text.replace(old, new)
        notes.append(f"temporary substitution: {old} -> {new}")
    if append_after:
        needle, addition = append_after
        if needle not in text:
            raise RuntimeError(f"Expected early-stop insertion point absent in {src.name}")
        text = text.replace(needle, needle + addition, 1)
        notes.append("temporary early stop after required figure outputs; plotting code unchanged")
    dst.write_text(text)
    return notes


def copytree_contents(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for p in src.iterdir():
        q = dst / p.name
        if p.is_dir():
            shutil.copytree(p, q, dirs_exist_ok=True)
        else:
            shutil.copy2(p, q)


def verify_support_manifest() -> None:
    manifest = SUPPORT / "BUILDER_SUPPORT_SHA256.csv"
    if not manifest.exists():
        raise RuntimeError("Missing builder support manifest")
    with manifest.open(newline="") as f:
        for row in csv.DictReader(f):
            p = REPO / row["path"]
            if not p.exists():
                raise RuntimeError(f"Missing builder support file: {row['path']}")
            if sha256(p) != row["sha256"]:
                raise RuntimeError(f"Builder support hash mismatch: {row['path']}")


def render_pdf(path: Path, dpi: int = 144) -> np.ndarray:
    doc = fitz.open(path)
    if len(doc) != 1:
        raise RuntimeError(f"Expected one-page figure PDF: {path}")
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(dpi / 72.0, dpi / 72.0), alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    doc.close()
    return arr[:, :, :3]


def compare_pdf_render(generated: Path, reference: Path) -> dict:
    a = render_pdf(generated)
    b = render_pdf(reference)
    if a.shape != b.shape:
        return {"pass": False, "generated_shape": list(a.shape), "reference_shape": list(b.shape),
                "mean_abs_diff": None, "max_abs_diff": None, "changed_pixel_fraction": None}
    d = np.abs(a.astype(np.int16) - b.astype(np.int16))
    changed = np.any(d != 0, axis=2)
    mean = float(d.mean())
    maxd = int(d.max())
    frac = float(changed.mean())
    # Allows tiny cross-platform anti-aliasing differences while rejecting layout/content drift.
    ok = mean <= 0.25 and frac <= 0.02 and maxd <= 96
    return {"pass": ok, "generated_shape": list(a.shape), "reference_shape": list(b.shape),
            "mean_abs_diff": mean, "max_abs_diff": maxd, "changed_pixel_fraction": frac}


def output_dirs(root: Path) -> tuple[Path, Path, Path]:
    main = root / "main_figures"; supp = root / "supplementary_figures"; staging = root / "staging"
    main.mkdir(parents=True, exist_ok=True); supp.mkdir(parents=True, exist_ok=True); staging.mkdir(parents=True, exist_ok=True)
    return main, supp, staging


def copy_result(pdf: Path, png: Path | None, target: str, main: Path, supp: Path) -> tuple[Path, Path | None]:
    outdir = main if target.startswith("Figure_") and not target.startswith("Figure_S") else supp
    outpdf = outdir / f"{target}.pdf"
    shutil.copy2(pdf, outpdf)
    outpng = None
    if png and png.exists():
        outpng = outdir / f"{target}.png"
        shutil.copy2(png, outpng)
    return outpdf, outpng


def build_target(target: str, staging_root: Path, main: Path, supp: Path) -> dict:
    ws = staging_root / target
    if ws.exists(): shutil.rmtree(ws)
    ws.mkdir(parents=True)
    builder = BUILDERS / BUILDER_FILES[target]
    if not builder.exists(): raise RuntimeError(f"Missing frozen builder: {builder}")
    support = SUPPORT / target
    notes: list[str] = []

    if target == "Figure_2":
        copytree_contents(support / "sources", ws / "sources")
        execp = ws / builder.name; shutil.copy2(builder, execp)
        run([sys.executable, str(execp)])
        pdf, png = ws / "FIGURE_2_FINAL_v1.0.2.pdf", ws / "FIGURE_2_FINAL_v1.0.2.png"

    elif target == "Figure_3":
        copytree_contents(support / "sources", ws / "sources")
        execp = ws / builder.name; shutil.copy2(builder, execp)
        run([sys.executable, str(execp)])
        pdf, png = ws / "FIGURE_3_FINAL_v1.0.1.pdf", ws / "FIGURE_3_FINAL_v1.0.1.png"

    elif target == "Figure_4":
        copytree_contents(support / "sources", ws / "sources")
        execp = ws / "BUILD_RELEASE_NORMALIZED.py"
        notes += write_exec_copy(builder, execp, [
            ("Path('/mnt/data/SCO_FIGURE_4_RESULT_FREEZE_JRSI_v1.0.1_REBUILD')", f"Path(r'{ws / 'out'}')")
        ])
        run([sys.executable, str(execp)])
        pdf, png = ws / "out/FIGURE_4_FINAL_v1.0.1.pdf", ws / "out/FIGURE_4_FINAL_v1.0.1.png"

    elif target == "Figure_5":
        shutil.copy2(support / "FIGURE_5A_DIRECTIONAL_PROFILE_T50.csv", ws / "FIGURE_5A_DIRECTIONAL_PROFILE_T50.csv")
        copytree_contents(support / "sources", ws / "sources")
        execp = ws / builder.name; shutil.copy2(builder, execp)
        run([sys.executable, str(execp)])
        pdf, png = ws / "FIGURE_5_FINAL_v1.1.1.pdf", ws / "FIGURE_5_FINAL_v1.1.1.png"

    elif target == "Figure_S1":
        root = ws / "root"
        old = root / "_old_supp_extract/MODEL_B_DCC_MANUSCRIPT_FIGURES_FREEZE_v3.0.0/sources"
        copytree_contents(support / "s1_sources", old / "Supplementary_Figure_S1")
        copytree_contents(support / "s2_sources", old / "Supplementary_Figure_S2")
        copytree_contents(support / "aux", root / "_aux")
        f4 = root / "SCO_FIGURE_4_RESULT_FREEZE_JRSI_v1.0.0/sources"; f4.mkdir(parents=True)
        for n in ("SCAFFOLD_STRENGTH_SUMMARY.csv", "FIDELITY_SUMMARY.csv"):
            shutil.copy2(support / "aux" / n, f4 / n)
        s6 = root / "SCO_FIGURE_4_5_S5_S6_JRSI_RESTRUCTURE_DRAFT_v1.0.0/sources"; s6.mkdir(parents=True)
        for n in ("EXPRESSION_SEPARATION_BY_TIME.csv", "ANISOTROPY_BY_TIME.csv", "LATTICE_MAPPING_RESULT_FREEZE.md", "LATTICE_PRIOR_PROSPECTIVE_RESULT_FREEZE.md"):
            shutil.copy2(support / "aux" / n, s6 / n)
        work = root / "_supp_work"; work.mkdir(parents=True)
        shutil.copy2(support / "s2_sources/PAIRED_BLOCK_ENDPOINTS_v1.0.0.csv", work / "PAIRED_BLOCK_ENDPOINTS_v1.0.0.csv")
        execp = ws / "BUILD_RELEASE_NORMALIZED.py"
        stop = "\nraise SystemExit(0)\n"
        needle = "save_all(fig,out/'SUPPLEMENTARY_FIGURE_S1_FINAL_v1.0.0'); plt.close(fig)"
        notes += write_exec_copy(builder, execp, [("ROOT=Path('/mnt/data')", f"ROOT=Path(r'{root}')")], (needle, stop))
        run([sys.executable, str(execp)])
        base = root / "SCO_SUPPLEMENTARY_FIGURE_S1_RESULT_FREEZE_JRSI_v1.0.0/SUPPLEMENTARY_FIGURE_S1_FINAL_v1.0.0"
        pdf, png = Path(str(base)+'.pdf'), Path(str(base)+'.png')

    elif target == "Figure_S2":
        pkg = ws / "pkg"; copytree_contents(support / "sources", pkg / "sources")
        execp = ws / "BUILD_RELEASE_NORMALIZED.py"
        notes += write_exec_copy(builder, execp, [
            ("ROOT=Path('/mnt/data/SCO_SUPPLEMENTARY_FIGURE_S2_RESULT_FREEZE_JRSI_v1.0.1')", f"ROOT=Path(r'{pkg}')")
        ])
        run([sys.executable, str(execp)])
        pdf, png = pkg / "SUPPLEMENTARY_FIGURE_S2_FINAL_v1.0.1.pdf", pkg / "SUPPLEMENTARY_FIGURE_S2_FINAL_v1.0.1.png"

    elif target == "Figure_S3":
        copytree_contents(support / "sources", ws / "sources")
        execp = ws / builder.name; shutil.copy2(builder, execp)
        run([sys.executable, str(execp)])
        pdf, png = ws / "SUPPLEMENTARY_FIGURE_S3_FINAL_v1.0.0.pdf", ws / "SUPPLEMENTARY_FIGURE_S3_FINAL_v1.0.0.png"

    elif target == "Figure_S4":
        copytree_contents(support / "sources", ws / "sources")
        (ws / "rendered").mkdir()
        execp = ws / builder.name; shutil.copy2(builder, execp)
        run([sys.executable, str(execp)])
        pdf, png = ws / "SUPPLEMENTARY_FIGURE_S4_FINAL_v1.0.2.pdf", ws / "SUPPLEMENTARY_FIGURE_S4_FINAL_v1.0.2.png"

    elif target == "Figure_S5":
        root = ws / "root"; src_pkg = root / "_s5_v111_extract/SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.1.1/sources"
        copytree_contents(support / "sources", src_pkg)
        execp = ws / "BUILD_RELEASE_NORMALIZED_SYNCED.py"
        notes += write_exec_copy(builder, execp, [
            ("ROOT=Path('/mnt/data')", f"ROOT=Path(r'{root}')"),
            ("Path('/mnt/data/_build_s5_v120.py')", f"Path(r'{builder}')"),
            (r"probe direction (degrees; all at $d^2=1$)", r"probe direction (degrees; all at $\|B_P-B_H\|^2=1$)"),
        ], ("plt.close(fig)", "\nraise SystemExit(0)\n"))
        notes.append("documented S5 synchronization v1: explicit squared scaffold norm notation")
        run([sys.executable, str(execp)])
        base = root / "SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.2.0/SUPPLEMENTARY_FIGURE_S5_FINAL_v1.2.0"
        pdf, png = Path(str(base)+'.pdf'), Path(str(base)+'.png')

    elif target == "Figure_S6":
        root = ws / "root"
        for d in ("sources/mapping", "sources/figure5_reference", "sources/prospective", "derived", "qc", "figures"):
            (root / d).mkdir(parents=True, exist_ok=True)
        copytree_contents(support / "mapping", root / "sources/mapping")
        copytree_contents(support / "figure5_reference", root / "sources/figure5_reference")
        copytree_contents(support / "prospective", root / "sources/prospective")
        cfg = json.loads((root / "sources/mapping/CONFIG_v1.0.0.json").read_text())
        (root / "DISPLAY_SPECIFICATION.json").write_text(json.dumps({"mapping_fidelity": cfg["base_p"], "mapping_generation": 50}, indent=2) + "\n")
        rows = []
        for p in sorted((root / "sources").rglob("*")):
            if p.is_file(): rows.append({"bundle_path": str(p.relative_to(root)), "sha256": sha256(p)})
        pd.DataFrame(rows).to_csv(root / "sources/INPUT_SOURCE_MANIFEST.csv", index=False)
        execp = ws / "BUILD_RELEASE_NORMALIZED_SYNCED.py"
        notes += write_exec_copy(builder, execp, [
            (r"$\Delta V_{\rm rel}(\phi=\pi)-\Delta V_{\rm rel}(\phi=0)$", r"$\Delta V_{\rm rel}(\chi=\pi)-\Delta V_{\rm rel}(\chi=0)$"),
        ])
        notes.append("documented S6 synchronization v2: reader-facing probe angle phi -> chi")
        run([sys.executable, str(execp), "--root", str(root)])
        pdf, png = root / "figures/SUPPLEMENTARY_FIGURE_S6_REVIEW_DRAFT_v1.2.0.pdf", root / "figures/SUPPLEMENTARY_FIGURE_S6_REVIEW_DRAFT_v1.2.0.png"

    else:
        raise ValueError(target)

    if not pdf.exists(): raise RuntimeError(f"No rebuilt PDF for {target}: {pdf}")
    outpdf, outpng = copy_result(pdf, png if png.exists() else None, target, main, supp)
    ref = support / "reference.pdf"
    render = compare_pdf_render(outpdf, ref)
    return {
        "target": target,
        "builder": str(builder.relative_to(REPO)),
        "builder_sha256": sha256(builder),
        "execution_notes": notes,
        "output_pdf": str(outpdf.relative_to(REPO)) if outpdf.is_relative_to(REPO) else str(outpdf),
        "output_pdf_sha256": sha256(outpdf),
        "output_png": str(outpng.relative_to(REPO)) if outpng and outpng.is_relative_to(REPO) else (str(outpng) if outpng else None),
        "reference_pdf": str(ref.relative_to(REPO)),
        "render_equivalence": render,
        "status": "PASS" if render["pass"] else "FAIL",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--figures", default="all", help="Comma-separated targets (e.g. Figure_2,Figure_S5) or 'all'.")
    ap.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--keep-staging", action="store_true")
    ap.add_argument("--no-verify", action="store_true", help="Build but do not fail on render-equivalence mismatch.")
    args = ap.parse_args()

    verify_support_manifest()
    selected = TARGETS if args.figures == "all" else [x.strip() for x in args.figures.split(",") if x.strip()]
    unknown = sorted(set(selected) - set(TARGETS))
    if unknown: raise SystemExit(f"Unknown figure target(s): {', '.join(unknown)}")

    out = args.output_root.resolve()
    if out.exists(): shutil.rmtree(out)
    main_dir, supp_dir, staging = output_dirs(out)
    # Figure 1 is an artwork exception: copy the frozen publication reference only.
    shutil.copy2(FROZEN_PUBLICATION / "main_figures/Figure_1.pdf", main_dir / "Figure_1.pdf")
    if (FROZEN_PUBLICATION / "main_figures/Figure_1.png").exists():
        shutil.copy2(FROZEN_PUBLICATION / "main_figures/Figure_1.png", main_dir / "Figure_1.png")

    results = []
    failures = []
    for target in selected:
        print(f"[build] {target}", flush=True)
        try:
            rec = build_target(target, staging, main_dir, supp_dir)
        except Exception as exc:
            rec = {"target": target, "status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}
        results.append(rec)
        if rec["status"] != "PASS": failures.append(target)
        print(f"[{rec['status']}] {target}", flush=True)

    report = {
        "schema_version": "1.0",
        "figure_1_status": "ARTWORK_REFERENCE_ONLY",
        "figure_1_note": "No native computational builder was supplied in the frozen Figure 1 package.",
        "selected_targets": selected,
        "results": results,
        "all_pass": not failures,
    }
    (out / "PUBLICATION_FIGURE_REPRODUCTION_REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
    pd.DataFrame([{**{k:v for k,v in r.items() if k not in ('render_equivalence','execution_notes')},
                   **({f"render_{k}":v for k,v in r.get('render_equivalence',{}).items()} if 'render_equivalence' in r else {})}
                  for r in results]).to_csv(out / "PUBLICATION_FIGURE_REPRODUCTION_SUMMARY.csv", index=False)

    if not args.keep_staging:
        shutil.rmtree(staging, ignore_errors=True)
    if failures and not args.no_verify:
        print("PUBLICATION FIGURE REBUILD: FAIL -> " + ", ".join(failures))
        return 1
    print(f"PUBLICATION FIGURE REBUILD: {'PASS' if not failures else 'BUILT WITH VERIFICATION WARNINGS'}")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
