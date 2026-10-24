from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch
import fitz

PKG = Path(__file__).resolve().parent
SRC_PDF = PKG / 'sources' / 'FIGURE_3_FINAL_v1.0.0.pdf'
OUT_PDF = PKG / 'FIGURE_3_FINAL_v1.0.1.pdf'
OUT_PNG = PKG / 'FIGURE_3_FINAL_v1.0.1.png'
TMP_PANEL = PKG / '_panel_c_replacement_tmp.pdf'

# Layout-only revision: preserve the prior frozen PDF everywhere except panel (c),
# which is replaced by an enlarged vector redraw of the same directional-response schematic.
fig = plt.figure(figsize=(6.90, 4.45))
ax = fig.add_axes([0.06, 0.05, 0.92, 0.88])
ax.set_axis_off()
ax.set_xlim(0, 1.42)
ax.set_ylim(0, 1.0)
ax.set_aspect('equal', adjustable='box')
DARK = '#303030'; BLUE = '#1f77b4'; RED = '#d62728'; GREEN = '#2ca02c'; ORANGE = '#ff7f0e'; PURPLE = '#9467bd'

fig.text(0.008, 0.985, '(c)', ha='left', va='top', fontsize=16, fontweight='bold', family='DejaVu Sans')
fig.text(0.105, 0.985, 'Directional response replaces a distance-only law', ha='left', va='top', fontsize=12.6, fontweight='bold', family='DejaVu Sans')

lc = (0.34, 0.57)
for r in [0.085, 0.155, 0.225, 0.295]:
    ax.add_patch(Circle(lc, r, fill=False, ec='.50', lw=1.1, clip_on=False))
ax.plot([lc[0], lc[0] + 0.235], [lc[1], lc[1] + 0.14], color=BLUE, lw=2.0, solid_capstyle='round', clip_on=False)
ax.text(lc[0], 0.915, 'distance only', ha='center', fontsize=10.5, family='DejaVu Sans')
ax.text(lc[0], 0.155, r'$\mathcal{R}=f(\|\delta\|)$', ha='center', fontsize=12, family='DejaVu Sans')

ax.add_patch(FancyArrowPatch((0.60, 0.78), (0.81, 0.78), arrowstyle='-|>', mutation_scale=14, lw=1.35, color=DARK, clip_on=False))
# RC5 artwork correction: the arrow deliberately has no text label.

rc = (1.10, 0.57)
for w, h in [(0.42, 0.145), (0.335, 0.116), (0.25, 0.087), (0.165, 0.057)]:
    ax.add_patch(Ellipse(rc, w, h, angle=18, fill=False, ec='.50', lw=1.0, clip_on=False))
for col, deg, length in [(RED, 145, 0.22), (GREEN, 60, 0.20), (ORANGE, 15, 0.23), (PURPLE, 210, 0.21)]:
    th = np.deg2rad(deg)
    ax.plot([rc[0], rc[0] + length * np.cos(th)], [rc[1], rc[1] + length * np.sin(th)], color=col, lw=1.6, solid_capstyle='round', clip_on=False)
ax.text(rc[0], 0.915, 'direction matters', ha='center', fontsize=10.5, family='DejaVu Sans')
ax.text(rc[0], 0.155, r'$\mathcal{R}(B_H+\delta)\approx R_0+g_T^T\delta+\frac{1}{2}\,\delta^T H_T\delta$', ha='center', fontsize=10.7, family='DejaVu Sans')
ax.text(0.07, 0.035, 'Prospective failure of the scalar-distance law motivated the revised\nlocal geometry, which permits anisotropic response.', fontsize=8.8, va='bottom', family='DejaVu Sans')
fig.savefig(TMP_PANEL, facecolor='white', bbox_inches=None, pad_inches=0)
plt.close(fig)

# Replace only the lower-left panel (c) region.
doc = fitz.open(SRC_PDF)
page = doc[0]
rect = fitz.Rect(18, 374, 528, 716)
page.draw_rect(rect, color=None, fill=(1, 1, 1), overlay=True)
paneldoc = fitz.open(TMP_PANEL)
page.show_pdf_page(rect, paneldoc, 0, keep_proportion=False, overlay=True)
paneldoc.close()
doc.save(OUT_PDF, garbage=4, deflate=True)
doc.close()
TMP_PANEL.unlink(missing_ok=True)

# Convenience raster export from the final PDF.
doc = fitz.open(OUT_PDF)
pix = doc[0].get_pixmap(matrix=fitz.Matrix(400/72, 400/72), alpha=False)
pix.save(OUT_PNG)
doc.close()
print(OUT_PDF)
print(OUT_PNG)
