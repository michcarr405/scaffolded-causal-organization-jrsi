#!/usr/bin/env python3
"""Run the complete publication-figure rebuild and require render-equivalent output."""
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.call([sys.executable, str(ROOT/'scripts/build_publication_figures.py')]))
