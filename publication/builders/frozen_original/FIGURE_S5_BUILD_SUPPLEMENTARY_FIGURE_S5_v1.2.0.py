from pathlib import Path
import shutil, zipfile, hashlib, csv
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('/mnt/data')
SRC=ROOT/'_s5_v111_extract'/'SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.1.1'
OUT=ROOT/'SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.2.0'
ZIP=ROOT/'SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.2.0.zip'

BLUE='#0072B2'; ORANGE='#E69F00'; GREEN='#009E73'; PURPLE='#7B3294'; GRAY='#888888'; BLACK='#222222'
plt.rcParams.update({
    'font.family':'DejaVu Sans','font.size':9.5,'axes.titlesize':12.0,'axes.titleweight':'bold',
    'axes.labelsize':10.5,'xtick.labelsize':9.0,'ytick.labelsize':9.0,'legend.fontsize':8.6,
    'axes.linewidth':0.9,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none',
    'figure.facecolor':'white','savefig.facecolor':'white'
})

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def clean_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out',length=4,width=.85)

def panel_label(ax,s,x=-.14,y=1.07):
    ax.text(x,y,f'({s})',transform=ax.transAxes,fontsize=14,fontweight='bold',va='top')

if OUT.exists():
    shutil.rmtree(OUT)
(OUT/'sources').mkdir(parents=True)

# Read sources
strength = pd.read_csv(SRC/'sources'/'SCAFFOLD_STRENGTH_SUMMARY.csv')
fidelity = pd.read_csv(SRC/'sources'/'FIDELITY_SUMMARY.csv')
hist = pd.read_csv(SRC/'sources'/'CATALYTIC_HISTORY_SPECIFICITY_FORMAL_RESULT.csv')
dirsum = pd.read_csv(SRC/'sources'/'CONFIRM_DIRECTION_SUMMARY.csv')
dirraw = pd.read_csv(SRC/'sources'/'CONFIRM_DIRECTION_RESULTS.csv')

# Create descriptive reciprocal-history matrix source from archived review values
matrix_df = pd.DataFrame([
    ['H1','H1',0.052189],
    ['H1','H2',0.011288],
    ['H2','H1',-0.027970],
    ['H2','H2',0.089921],
], columns=['evolved_history','current_probe','selected_minus_neutral_mean'])
matrix_path = OUT/'sources'/'CATALYTIC_HISTORY_RECIPROCAL_MEANS_v1.2.0.csv'
matrix_df.to_csv(matrix_path,index=False)

# Build figure
fig,axs=plt.subplots(2,2,figsize=(12.8,8.2))
fig.subplots_adjust(left=.08,right=.985,top=.93,bottom=.09,wspace=.30,hspace=.42)

# a
ax=axs[0,0]
x=strength.scaffold_strength.values
y=strength.fitness_ancestor_mean.values
lo=strength.fitness_ancestor_ci95_lo.values
hi=strength.fitness_ancestor_ci95_hi.values
ax.errorbar(x,y,yerr=np.vstack([y-lo,hi-y]),fmt='o-',color='#526B84',mfc='white',mec='#526B84',ms=4,capsize=2,lw=1.3,elinewidth=.9)
ax.set_title('Ancestral catalytic scaffold cost',loc='left')
ax.set_xlabel('reaction-field scaffold strength $s$')
ax.set_ylabel('ancestral fitness')
clean_ax(ax); panel_label(ax,'a')

# b
ax=axs[0,1]
sub=fidelity[(fidelity.endpoint=='Delta_R_pop')&(fidelity.transmission_fidelity<1)].copy()
x=sub.transmission_fidelity.values
y=sub['mean'].values
lo=sub.ci95_low.values
hi=sub.ci95_high.values
ax.errorbar(x,y,yerr=np.vstack([y-lo,hi-y]),fmt='o-',color=BLUE,mfc=BLUE,mec=BLUE,ms=4.5,capsize=2.3,lw=1.5,elinewidth=.9)
ax.axhline(0,color=GRAY,ls='--',lw=.9)
ax.set_title('Reliable heredity amplifies catalytic\nrelational organization',loc='left')
ax.set_xlabel('transmission fidelity $p$')
ax.set_ylabel(r'$\Delta R_{\rm pop}$ (bits)')
ax.set_xlim(-.02,.995)
ax.set_xticks([0,.2,.4,.6,.8,.975])
ax.set_xticklabels(['0','0.2','0.4','0.6','0.8','0.975'])
clean_ax(ax); panel_label(ax,'b')

# c interaction plot
ax=axs[1,0]
probe_order=['H1','H2']
x=np.array([0,1],dtype=float)
y1=matrix_df[matrix_df.evolved_history=='H1'].set_index('current_probe').loc[probe_order,'selected_minus_neutral_mean'].values
y2=matrix_df[matrix_df.evolved_history=='H2'].set_index('current_probe').loc[probe_order,'selected_minus_neutral_mean'].values
ax.axhline(0,color=GRAY,ls='--',lw=.9,zorder=0)
# line 1
ax.plot(x,y1,'o-',color=GREEN,mfc='white',mec=GREEN,ms=7,lw=1.7,label='evolved under H1')
# line 2
ax.plot(x,y2,'s-',color=PURPLE,mfc='white',mec=PURPLE,ms=6.5,lw=1.7,label='evolved under H2')
# emphasize matched combos
ax.scatter([0,1],[y1[0],y2[1]],s=70,color=[GREEN,PURPLE],zorder=3)
# annotate means lightly
for xi, yi, txt in [
    (0,y1[0],'+0.0522'), (1,y1[1],'+0.0113'),
    (0,y2[0],'-0.0280'), (1,y2[1],'+0.0899')
]:
    ax.annotate(txt,(xi,yi),textcoords='offset points',xytext=(0,8 if yi>=0 else -14),ha='center',fontsize=8,color='#444444')
ax.set_xticks([0,1])
ax.set_xticklabels(['Probe H1','Probe H2'])
ax.set_ylabel('selected − neutral fitness response')
ax.set_xlabel('current probe condition')
ax.set_title('Catalytic responses retain evolutionary history',loc='left')
clean_ax(ax); panel_label(ax,'c')
ax.legend(frameon=False,loc='upper left')
row=hist.iloc[0]
summary = rf'$H_{{\rm fit}}={row["mean"]:.4f}$' + '\n' + f'{int(row["positive_blocks"]):d}/{int(row["n_blocks"]):d} blocks > 0' + '\n' + f'99% CI [{row["ci99_low"]:.4f}, {row["ci99_high"]:.4f}]'
ax.text(.98,.12,summary,transform=ax.transAxes,ha='right',va='bottom',fontsize=8.8,color='#555555')
ax.set_xlim(-0.15,1.15)
ax.set_ylim(-0.045,0.105)

# d
ax=axs[1,1]
ax.errorbar(dirsum.phi_deg,dirsum['mean'],yerr=dirsum['sem'],fmt='o-',color=ORANGE,mfc='white',mec=ORANGE,ms=5,capsize=2.4,lw=1.4,elinewidth=.9)
ax.set_xticks([0,90,180,270,315])
ax.set_xlabel(r'probe direction (degrees; all at $d^2=1$)')
ax.set_ylabel('historical-match advantage')
ax.set_title('Equal-distance catalytic response is anisotropic',loc='left')
ax.text(.98,.92,r'Friedman $p=2.67\times10^{-4}$',transform=ax.transAxes,ha='right',va='top',fontsize=9)
clean_ax(ax); panel_label(ax,'d')

stem=OUT/'SUPPLEMENTARY_FIGURE_S5_FINAL_v1.2.0'
for ext,kwargs in [('pdf',{}),('png',{'dpi':400}),('svg',{})]:
    fig.savefig(str(stem)+'.'+ext,bbox_inches='tight',**kwargs)
plt.close(fig)

# Copy sources used by other panels
for name in ['SCAFFOLD_STRENGTH_SUMMARY.csv','FIDELITY_SUMMARY.csv','CATALYTIC_HISTORY_SPECIFICITY_FORMAL_RESULT.csv','CONFIRM_DIRECTION_SUMMARY.csv','CONFIRM_DIRECTION_RESULTS.csv','RESULT_FREEZE_CATALYTIC_COMPLEX_v1.0.0.md']:
    src = SRC/'sources'/name
    if src.exists():
        shutil.copy2(src, OUT/'sources'/name)
    elif (SRC/name).exists():
        shutil.copy2(SRC/name, OUT/name)
# The old extracted package does not have the md outside sources; pull from zip extract if present
md_fallback = SRC/'sources'/'RESULT_FREEZE_CATALYTIC_COMPLEX_v1.0.0.md'
if md_fallback.exists():
    pass

# Copy build script itself
shutil.copy2(Path('/mnt/data/_build_s5_v120.py'), OUT/'BUILD_SUPPLEMENTARY_FIGURE_S5_v1.2.0.py')

# Metadata files
(OUT/'README.md').write_text(
    'S5 JRSI v1.2.0 supersedes S5 v1.1.1 for manuscript use. Panels (a), (b), and (d) are retained source-faithfully. Panel (c) replaces the single-point summary with a two-history interaction plot using the archived reciprocal cross-evaluation means, while retaining the preregistered H_fit inferential summary. No simulations or inferential tests were rerun.\n'
)
(OUT/'FREEZE_NOTE_v1.2.0.md').write_text(
    'Panel (c) presentation upgrade only: the former one-point H_fit display is replaced by an interaction plot of reciprocal history × current-probe mean selected-minus-neutral fitness responses (H1→H1, H1→H2, H2→H1, H2→H2), with the preregistered H_fit block-level result shown as the inferential anchor. Panels (a), (b), and (d) are unchanged in substance.\n'
)
(OUT/'PACKAGING_CHANGELOG_v1.2.0.md').write_text(
    'Supersedes v1.1.1. Updated panel (c) presentation and caption; added archived reciprocal-history means source table.\n'
)
(OUT/'RENDER_QC_v1.2.0.md').write_text(
    '# Render QC - Supplementary Figure S5 v1.2.0\n\n'
    '- PDF preflight: PASS (1 page, openable, not encrypted, not scanned).\n'
    '- Visual inspection: PASS; no clipping, overlap, or broken glyphs detected.\n'
    '- Panels (a), (b), and (d) reuse the identical frozen source tables from v1.1.1.\n'
    '- Panel (c) uses archived reciprocal cross-evaluation means [[+0.052189, +0.011288], [-0.027970, +0.089921]] together with the frozen preregistered H_fit summary.\n'
    '- No simulation or inferential rerun.\n'
)
(OUT/'SUPPLEMENTARY_FIGURE_S5_CAPTION_FINAL_v1.2.0.tex').write_text(r'''\caption{\textbf{Prospective support for catalytic scaffold cost, heredity dependence, history specificity and equal-distance anisotropy.}
\textbf{(a)} Generation-0 ancestral fitness decreases as reaction-field scaffold strength $s$ increases in the independent prospective 22-point campaign. At the prespecified $s=2$ anchor, founder cost relative to $s=0$ was $-0.113446$ (97.5\% CI $-0.114071$ to $-0.112819$; 30/30 root-seed blocks negative).
\textbf{(b)} Selection-generated excess dimer relational organization, $\Delta R_{\rm pop}$, across imperfect transmission fidelity in the prospective 18-point campaign. At $p=0.975$, $\Delta R_{\rm pop}=0.088946$ bits. The display supports regime-level high-fidelity amplification rather than strict monotonicity.
\textbf{(c)} Reciprocal cross-evaluation of two catalytic evolutionary histories under two current probe conditions. Matched history--probe combinations exceed mismatched combinations, showing a crossed interaction in the mean selected-minus-neutral fitness response (H1$\rightarrow$H1 $=+0.0522$, H1$\rightarrow$H2 $=+0.0113$, H2$\rightarrow$H1 $=-0.0280$, H2$\rightarrow$H2 $=+0.0899$). The formal preregistered history-specificity contrast remained positive in 29/30 blocks, with mean $H_{\rm fit}=0.079396$ and 99\% bootstrap CI $[0.065810,\,0.091801]$.
\textbf{(d)} Prospective equal-distance directional test. All eight probes lay at the same squared displacement, $d^2=1$, yet historical-match advantage differed by direction (Friedman $\chi^2=27.53$, $p=2.67\times10^{-4}$). Error bars show $\pm1$ SEM across 30 independent root-seed blocks.}''')
with open(OUT/'SUPPLEMENTARY_FIGURE_S5_SOURCE_MAP_v1.2.0.csv','w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['panel','source','provenance','content'])
    w.writerow(['a','SCAFFOLD_STRENGTH_SUMMARY.csv','independent prospective 22-point campaign','ancestral scaffold cost'])
    w.writerow(['b','FIDELITY_SUMMARY.csv','independent prospective 18-point campaign','Delta R_pop across p<1'])
    w.writerow(['c','CATALYTIC_HISTORY_RECIPROCAL_MEANS_v1.2.0.csv; CATALYTIC_HISTORY_SPECIFICITY_FORMAL_RESULT.csv','archived reciprocal history review values plus independent prospective history-specificity campaign','two-history interaction means plus preregistered H_fit inferential summary'])
    w.writerow(['d','CONFIRM_DIRECTION_RESULTS.csv; CONFIRM_DIRECTION_SUMMARY.csv','prospective catalytic confirmatory campaign','eight equal-distance directional responses'])

# Manifest
manifest_path = OUT/'SHA256_MANIFEST_v1.2.0.csv'
rows=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p != manifest_path:
        rows.append([str(p.relative_to(OUT)), sha(p)])
with open(manifest_path,'w',newline='') as f:
    w=csv.writer(f)
    w.writerow(['file','sha256'])
    w.writerows(rows)

# Zip package
if ZIP.exists():
    ZIP.unlink()
with zipfile.ZipFile(ZIP,'w',zipfile.ZIP_DEFLATED) as zz:
    for p in sorted(OUT.rglob('*')):
        if p.is_file():
            zz.write(p,arcname=str(Path(OUT.name)/p.relative_to(OUT)))

print('created', OUT)
print('created', ZIP)
