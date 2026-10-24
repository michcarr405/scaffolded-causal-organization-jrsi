from pathlib import Path
import shutil, hashlib, json, csv, zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path('/mnt/data/SCO_FIGURE_4_RESULT_FREEZE_JRSI_v1.0.0_REBUILD')
SRCROOT = Path(__file__).resolve().parent / 'sources'
REFPDF = Path(__file__).resolve().parent / 'sources' / 'FIGURE_4_RESULT_FREEZE_v1.3.0.pdf'
if OUT.exists(): shutil.rmtree(OUT)
(OUT/'sources').mkdir(parents=True)

strength = pd.read_csv(SRCROOT/'SCAFFOLD_STRENGTH_SUMMARY.csv')
fidelity = pd.read_csv(SRCROOT/'FIDELITY_SUMMARY.csv')
confirm = pd.read_csv(SRCROOT/'CONFIRM_BLOCK_RESULTS.csv')

# Scientific identity checks against the frozen Figure 4 v1.3.0 annotations.
contrast = confirm['DeltaC_probe05'] - confirm['Delta_C_pop']
assert np.allclose(contrast.to_numpy(), confirm['masking_contrast'].to_numpy(), atol=1e-14)
assert int((contrast > 0).sum()) == 25
assert abs(float(contrast.mean()) - 0.0003394400639775995) < 1e-15

plt.rcParams.update({
    'font.family':'DejaVu Sans',
    'font.size':10.5,
    'axes.labelsize':12.5,
    'axes.titlesize':15,
    'axes.titleweight':'bold',
    'xtick.labelsize':10.5,
    'ytick.labelsize':10.5,
    'legend.fontsize':9.5,
    'axes.linewidth':1.0,
    'lines.linewidth':1.8,
    'pdf.fonttype':42,
    'ps.fonttype':42,
})

BLUE='#0072B2'; ORANGE='#E69F00'; GRAY='0.62'
fig, axs = plt.subplots(1,3,figsize=(16.5,5.5))
fig.subplots_adjust(left=0.055,right=0.985,top=0.82,bottom=0.17,wspace=0.30)

def style_axes(ax, zero=False):
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.0); ax.spines['bottom'].set_linewidth(1.0)
    ax.tick_params(direction='out', length=5, width=1.0)
    if zero:
        ax.axhline(0, color=GRAY, linestyle='--', linewidth=1.15, zorder=0)

def panel_title(ax, letter, text):
    ax.text(-0.16,1.30,f'({letter})', transform=ax.transAxes, ha='left', va='bottom',
            fontsize=18, fontweight='bold', clip_on=False)
    ax.text(-0.02,1.17,text, transform=ax.transAxes, ha='left', va='bottom',
            fontsize=15, fontweight='bold', linespacing=0.95, clip_on=False)

# (a) Fitness recovery; same frozen source data as Figure 4 v1.3.0.
ax=axs[0]; style_axes(ax, zero=True)
panel_title(ax,'a','Selection drives fitness recovery\nabove the ancestral baseline')
x=strength['scaffold_strength'].to_numpy()
ys=strength['selected_minus_ancestor_mean'].to_numpy(); ls=strength['selected_minus_ancestor_ci95_lo'].to_numpy(); hs=strength['selected_minus_ancestor_ci95_hi'].to_numpy()
yn=strength['neutral_minus_ancestor_mean'].to_numpy(); ln=strength['neutral_minus_ancestor_ci95_lo'].to_numpy(); hn=strength['neutral_minus_ancestor_ci95_hi'].to_numpy()
ax.errorbar(x,ys,yerr=np.vstack([ys-ls,hs-ys]),fmt='o-',color=BLUE,markerfacecolor=BLUE,markeredgecolor=BLUE,
            markersize=4.3,linewidth=1.8,capsize=2.4,elinewidth=1.0,label='selected - ancestor')
ax.errorbar(x,yn,yerr=np.vstack([yn-ln,hn-yn]),fmt='s--',color=ORANGE,markerfacecolor='white',markeredgecolor=ORANGE,
            markersize=4.1,linewidth=1.5,capsize=2.4,elinewidth=1.0,label='neutral - ancestor')
ax.set_xlabel(r'reaction-field scaffold strength $s$')
ax.set_ylabel('fitness change from ancestral baseline')
ax.set_xlim(-0.1,8.15); ax.set_ylim(-0.045,0.061)
# Requested layout revision: legend moved out of the crowded upper-left data region.
ax.legend(loc='upper right', bbox_to_anchor=(0.995, 1.015), borderaxespad=0.0, frameon=False, handlelength=2.4)

# (b) Adaptive relational value across imperfect heredity domain.
ax=axs[1]; style_axes(ax, zero=True)
panel_title(ax,'b','Reliable heredity amplifies catalytic\nadaptive relational value')
sub=fidelity[(fidelity.endpoint=='Delta_V_rel') & (fidelity.transmission_fidelity<1.0)].copy()
xp=sub.transmission_fidelity.to_numpy(); yy=sub['mean'].to_numpy(); lo=sub.ci95_low.to_numpy(); hi=sub.ci95_high.to_numpy()
ax.errorbar(xp,yy,yerr=np.vstack([yy-lo,hi-yy]),fmt='o-',color=BLUE,markerfacecolor=BLUE,markeredgecolor=BLUE,
            markersize=4.8,linewidth=1.9,capsize=3.0,elinewidth=1.05)
ax.set_xlabel(r'transmission fidelity $p$')
ax.set_ylabel(r'$\Delta V_{\rm rel}$ (fitness units)')
ax.set_xlim(-0.02,0.995); ax.set_xticks([0,0.2,0.4,0.6,0.8,0.975]); ax.set_xticklabels(['0','0.2','0.4','0.6','0.8','0.975']); ax.set_ylim(-0.003,0.053)

# (c) Probe minus training relational effect; same 30 root-seed block values as v1.3.0.
ax=axs[2]; style_axes(ax, zero=True)
panel_title(ax,'c','Expression can be stronger away\nfrom the training field')
y=contrast.to_numpy()
# Deterministic symmetric horizontal jitter is purely presentational; y-values are frozen.
rng=np.random.default_rng(43013)
jitter=rng.uniform(-0.105,0.105,size=len(y))
ax.scatter(jitter,y,s=30,facecolors='none',edgecolors=ORANGE,linewidths=1.35,zorder=3)
ax.hlines(float(y.mean()), -0.29,0.29, color=BLUE, linewidth=2.1, zorder=2)
ax.set_xlim(-0.36,0.36); ax.set_ylim(-0.00024,0.00102)
ax.set_xticks([0]); ax.set_xticklabels(['30 independent\nroot-seed blocks'])
ax.set_ylabel(r'Probe minus training relational effect,\n$\Delta C_{\rm pop}(0.5)-\Delta C_{\rm pop}(2.0)$ (bits)')
# Requested layout revision: no inferential text inside the plotting area.

pdf=OUT/'FIGURE_4_FINAL_v1.0.0.pdf'
png=OUT/'FIGURE_4_FINAL_v1.0.0.png'
fig.savefig(pdf, facecolor='white', bbox_inches='tight')
fig.savefig(png, dpi=400, facecolor='white', bbox_inches='tight')
plt.close(fig)

# Copy the exact frozen source tables used to generate the three panels.
for name in ['SCAFFOLD_STRENGTH_SUMMARY.csv','FIDELITY_SUMMARY.csv','CONFIRM_BLOCK_RESULTS.csv']:
    shutil.copy2(SRCROOT/name, OUT/'sources'/name)
shutil.copy2(REFPDF, OUT/'sources'/REFPDF.name)
shutil.copy2(Path(__file__), OUT/'build_figure4_jrsi_v1.0.0.py')

with open(OUT/'FIGURE_4_SOURCE_MAP_v1.0.0.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['panel','source','scientific_content','layout_revision'])
    w.writerow(['a','SCAFFOLD_STRENGTH_SUMMARY.csv','selected and neutral fitness change from ancestral baseline','legend nudged upward within upper-right corner'])
    w.writerow(['b','FIDELITY_SUMMARY.csv','Delta V_rel across transmission fidelity p<1','none'])
    w.writerow(['c','CONFIRM_BLOCK_RESULTS.csv','DeltaC_probe05 - Delta_C_pop for 30 root-seed blocks','inferential annotation removed from plotting area'])

(OUT/'FIGURE_4_CAPTION_v1.0.0.tex').write_text(r'''\caption{\textbf{A mechanistically distinct catalytic realization reproduces central scaffolded-organization signatures.}
\textbf{(a)} Change from the ancestral fitness baseline across reaction-field scaffold strengths for selected and matched-neutral populations. Selection produces compensatory recovery over an intermediate scaffold-strength regime while matched-neutral populations remain near or below the ancestral baseline.
\textbf{(b)} Adaptive relational value, $\Delta V_{\rm rel}$, across transmission fidelity. The value of preserving evolved catalyst-dimer relations is strongly amplified in the high-fidelity hereditary regime.
\textbf{(c)} Frozen endpoint populations evolved under the training field were evaluated under a weaker probe field. The probe-minus-training relational effect was positive in 25/30 independent root-seed blocks (mean $+0.000339$ bits; exact sign $p=1.62\times10^{-4}$). The inferential summary is reported in the caption rather than inside the plotting area.}''')

(OUT/'README.md').write_text('''# SCO_FIGURE_4_JRSI_RESTRUCTURE_DRAFT_v1.0.0\n\nProgrammatic source-faithful rebuild of the three-panel JRSI Figure 4.\n\nChanges from v1.1.0:\n- panel (a): legend moved to the upper right and nudged upward to clear the data;\n- panel (c): inferential text removed from the plotting area and retained in the caption.\n\nAll scientific y-values, intervals, and block-level observations are read directly from the frozen source tables. No simulations or inferential analyses were rerun.\n''')
(OUT/'RESTRUCTURE_NOTE_v1.0.0.md').write_text('''Layout-only revision requested after inspection, with an additional upward nudge of the panel (a) legend to avoid crowding the curve. The authoritative scientific reference remains user-supplied FIGURE_4_RESULT_FREEZE_v1.3.0.pdf. Panel data are rebuilt from the archived source tables that generated the frozen catalytic figure.\n''')

src_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [REFPDF, SRCROOT/'SCAFFOLD_STRENGTH_SUMMARY.csv', SRCROOT/'FIDELITY_SUMMARY.csv', SRCROOT/'CONFIRM_BLOCK_RESULTS.csv']}
(OUT/'SOURCE_PROVENANCE_v1.0.0.json').write_text(json.dumps({
    'authoritative_visual_reference':REFPDF.name,
    'source_files':src_hashes,
    'transformation':'programmatic rebuild from frozen source tables; layout-only revisions',
    'scientific_changes':'none'
},indent=2))

rows=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name!='SHA256_MANIFEST_v1.0.0.csv':
        rows.append([str(p.relative_to(OUT)),hashlib.sha256(p.read_bytes()).hexdigest()])
with open(OUT/'SHA256_MANIFEST_v1.0.0.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['file','sha256']); w.writerows(rows)

zip_path=Path(str(OUT)+'.zip')
if zip_path.exists(): zip_path.unlink()
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.rglob('*')):
        if p.is_file(): z.write(p, arcname=str(Path(OUT.name)/p.relative_to(OUT)))
print(pdf)
print(png)
print(zip_path)
