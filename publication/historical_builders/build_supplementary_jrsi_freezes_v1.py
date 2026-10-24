from pathlib import Path
import shutil, hashlib, csv, json, zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.ticker import FormatStrFormatter, MaxNLocator

ROOT=Path('/mnt/data')
OLD=ROOT/'_old_supp_extract/MODEL_B_DCC_MANUSCRIPT_FIGURES_FREEZE_v3.0.0'
FIG4=ROOT/'SCO_FIGURE_4_RESULT_FREEZE_JRSI_v1.0.0/sources'
S6SRC=ROOT/'SCO_FIGURE_4_5_S5_S6_JRSI_RESTRUCTURE_DRAFT_v1.0.0/sources'
WORK=ROOT/'_supp_work'

BLUE='#0072B2'; ORANGE='#E69F00'; GRAY='#777777'; BLACK='#222222'
plt.rcParams.update({
    'font.family':'DejaVu Sans', 'font.size':9.5, 'axes.titlesize':12,
    'axes.labelsize':10.5, 'xtick.labelsize':9, 'ytick.labelsize':9,
    'legend.fontsize':8.8, 'pdf.fonttype':42, 'ps.fonttype':42,
    'axes.linewidth':0.9, 'figure.facecolor':'white', 'savefig.facecolor':'white'
})

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def clean_dir(p):
    if p.exists(): shutil.rmtree(p)
    (p/'sources').mkdir(parents=True)

def write_manifest(out, version='v1.0.0'):
    fn=out/f'SHA256_MANIFEST_{version}.csv'
    rows=[]
    for p in sorted(out.rglob('*')):
        if p.is_file() and p != fn:
            rows.append([str(p.relative_to(out)),sha(p)])
    with open(fn,'w',newline='') as f:
        w=csv.writer(f); w.writerow(['file','sha256']); w.writerows(rows)

def zip_dir(out):
    zp=ROOT/f'{out.name}.zip'
    if zp.exists(): zp.unlink()
    with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(out.rglob('*')):
            if p.is_file(): z.write(p, arcname=str(Path(out.name)/p.relative_to(out)))
    return zp

def save_all(fig, base):
    fig.savefig(str(base)+'.pdf', bbox_inches='tight')
    fig.savefig(str(base)+'.png', dpi=400, bbox_inches='tight')
    fig.savefig(str(base)+'.svg', bbox_inches='tight')

# ---------- S1 ----------
out=ROOT/'SCO_SUPPLEMENTARY_FIGURE_S1_RESULT_FREEZE_JRSI_v1.0.0'; clean_dir(out)
src=OLD/'sources/Supplementary_Figure_S1'
D0=pd.read_csv(src/'S5_G0_SHARED_ANCESTOR_ENRICHMENT.csv'); DN=pd.read_csv(src/'S5_G250_NEUTRAL_ENRICHMENT.csv'); DS=pd.read_csv(src/'S5_G250_SELECTED_ENRICHMENT.csv')
labels=D0.motif_label.astype(str).tolist(); E0=D0[['S1','S2','S3','S4']].to_numpy(); EN=DN[['S1','S2','S3','S4']].to_numpy(); ES=DS[['S1','S2','S3','S4']].to_numpy()
order=pd.read_csv(src/'TOP24_MOTIF_ORDER.csv'); prefs=(order.preferred_segment_selected_g250.to_numpy(int)-1).tolist(); seps=[j-.5 for j in range(1,len(prefs)) if prefs[j]!=prefs[j-1]]
cmap=LinearSegmentedColormap.from_list('orange_white_blue',[ORANGE,'#FFFFFF',BLUE]); normE=TwoSlopeNorm(vmin=-6,vcenter=0,vmax=2)
def heat_style(ax,show_y=False):
    ax.set_xticks(range(4),['S1','S2','S3','S4']); ax.set_xlabel('segment $S$'); ax.set_yticks(range(24))
    if show_y: ax.set_yticklabels(labels,fontsize=7.5); ax.set_ylabel('top-24 motif identities $M$')
    else: ax.set_yticklabels([]); ax.tick_params(axis='y',length=0)
    for y in seps: ax.axhline(y,color=BLACK,lw=.7)
    for xx in np.arange(-.5,4,1): ax.axvline(xx,color='white',lw=.3,alpha=.65)
fig=plt.figure(figsize=(10.2,4.55)); outer=fig.add_gridspec(1,3,left=.105,right=.945,top=.84,bottom=.14,wspace=.25)
axs=[fig.add_subplot(outer[0,i]) for i in range(3)]; ims=[]
for i,(ax,E,plab,title) in enumerate(zip(axs,[E0,EN,ES],['(a)','(b)','(c)'],['Generation 0\n(shared ancestor)','Generation 250\nneutral','Generation 250\nselected'])):
    im=ax.imshow(E,aspect='auto',cmap=cmap,norm=normE,interpolation='nearest'); ims.append(im); heat_style(ax,i==0); ax.set_title(title,pad=10); ax.text(-.18,1.035,plab,transform=ax.transAxes,fontweight='bold',fontsize=11.5,clip_on=False)
pos=axs[2].get_position(); cax=fig.add_axes([pos.x1+.012,pos.y0,.014,pos.height]); cb=fig.colorbar(ims[-1],cax=cax); cb.set_ticks([-6,-4,-2,0,2]); cb.set_label(r'$E(S,M)$ (bits)',labelpad=5)
save_all(fig,out/'SUPPLEMENTARY_FIGURE_S1_FINAL_v1.0.0'); plt.close(fig)
for p in src.iterdir():
    if p.is_file(): shutil.copy2(p,out/'sources'/p.name)
(out/'SUPPLEMENTARY_FIGURE_S1_CAPTION_FINAL_v1.0.0.tex').write_text(r'''\caption{\textbf{Selection generates motif--segment relational organization in Model B.}
Heatmaps show empirical pointwise motif--segment enrichment, $E(S,M)=\log_2[P(S,M)/(P(S)P(M))]$, from the 30 independent SCF0 confirmatory blocks at $\beta=4$, $\Theta=1.2$ and $p=0.975$. \textbf{(a)} Generation-0 shared ancestor. \textbf{(b)} Generation-250 neutral populations. \textbf{(c)} Generation-250 selected populations. The same 24 motif identities, row order, segment order and colour scale are used throughout. Horizontal lines separate motif groups according to their preferred segment in the evolved selected population; they are visual group separators rather than physical boundaries or statistical thresholds.}''')
with open(out/'SUPPLEMENTARY_FIGURE_S1_SOURCE_MAP_v1.0.0.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['panel','source','content']);
    w.writerow(['a','S5_G0_SHARED_ANCESTOR_ENRICHMENT.csv','generation-0 shared-ancestor enrichment']); w.writerow(['b','S5_G250_NEUTRAL_ENRICHMENT.csv','generation-250 neutral enrichment']); w.writerow(['c','S5_G250_SELECTED_ENRICHMENT.csv','generation-250 selected enrichment'])
(out/'README.md').write_text('S1 JRSI result freeze. Programmatic source-faithful rebuild from the canonical Model B heatmap source tables. No scientific values were changed.\n')
(out/'FREEZE_NOTE_v1.0.0.md').write_text('Current JRSI S1. Supersedes older numbering contexts only; scientific content is identical to the canonical emergence heatmap freeze.\n')
shutil.copy2(Path(__file__),out/'build_supplementary_jrsi_freezes_v1.py'); write_manifest(out); zip_dir(out)

# ---------- S2 ----------
out=ROOT/'SCO_SUPPLEMENTARY_FIGURE_S2_RESULT_FREEZE_JRSI_v1.0.0'; clean_dir(out)
src2=OLD/'sources/Supplementary_Figure_S2'
DI=pd.read_csv(src2/'S6_INTACT_G250_SELECTED_ENRICHMENT.csv'); DP=pd.read_csv(src2/'S6_PRIMARY_POST_ERASURE_ENRICHMENT.csv'); DE=pd.read_csv(src2/'S6_EXACT_MARGIN_POST_ERASURE_ENRICHMENT.csv')
EI=DI[['S1','S2','S3','S4']].to_numpy(); EP=DP[['S1','S2','S3','S4']].to_numpy(); EE=DE[['S1','S2','S3','S4']].to_numpy(); normR=TwoSlopeNorm(vmin=-.012,vcenter=0,vmax=.012)
pairs=pd.read_csv(WORK/'PAIRED_BLOCK_ENDPOINTS_v1.0.0.csv')
r=float(np.corrcoef(pairs.D_delta_C_down_primary,pairs.A_delta_C_down_unitshuffle)[0,1])
fig=plt.figure(figsize=(10.4,8.3)); gs=fig.add_gridspec(2,2,left=.09,right=.96,top=.94,bottom=.08,wspace=.30,hspace=.35)
# a intact
ax=fig.add_subplot(gs[0,0]); im=ax.imshow(EI,aspect='auto',cmap=cmap,norm=normE,interpolation='nearest'); heat_style(ax,True); ax.set_title('Intact evolved selected',pad=9,fontweight='bold'); ax.text(-.17,1.035,'(a)',transform=ax.transAxes,fontweight='bold',fontsize=12,clip_on=False); pos=ax.get_position(); cax=fig.add_axes([pos.x1+.008,pos.y0,.012,pos.height]); cb=fig.colorbar(im,cax=cax); cb.set_ticks([-6,-4,-2,0,2]); cb.ax.set_title(r'$E_{intact}$'+'\n(bits)',fontsize=7.5,pad=2)
# b primary
ax=fig.add_subplot(gs[0,1]); im=ax.imshow(EP,aspect='auto',cmap=cmap,norm=normR,interpolation='nearest'); heat_style(ax,False); ax.set_title('Primary factorized erasure',pad=9,fontweight='bold'); ax.text(-.14,1.035,'(b)',transform=ax.transAxes,fontweight='bold',fontsize=12,clip_on=False); ax.text(.5,.51,'post-erasure\n$E(S,M)=0$',transform=ax.transAxes,ha='center',va='center',fontsize=9,color=GRAY); pos=ax.get_position(); cax=fig.add_axes([pos.x1+.008,pos.y0,.012,pos.height]); cb=fig.colorbar(im,cax=cax); cb.set_ticks([-.01,0,.01]); cb.ax.set_title(r'$E_{after}$'+'\n(bits)',fontsize=7.5,pad=2)
# c exact-margin
ax=fig.add_subplot(gs[1,0]); im=ax.imshow(EE,aspect='auto',cmap=cmap,norm=normR,interpolation='nearest'); heat_style(ax,True); ax.set_title('Exact-margin erasure',pad=9,fontweight='bold'); ax.text(-.17,1.035,'(c)',transform=ax.transAxes,fontweight='bold',fontsize=12,clip_on=False); pos=ax.get_position(); cax=fig.add_axes([pos.x1+.008,pos.y0,.012,pos.height]); cb=fig.colorbar(im,cax=cax); cb.set_ticks([-.01,0,.01]); cb.ax.set_title(r'$E_{after}$'+'\n(bits)',fontsize=7.5,pad=2)
# d agreement
ax=fig.add_subplot(gs[1,1]); x=pairs.D_delta_C_down_primary.to_numpy(); y=pairs.A_delta_C_down_unitshuffle.to_numpy(); mx=max(x.max(),y.max())*1.04; ax.scatter(x,y,s=24,facecolors='none',edgecolors=BLUE,linewidths=1.0,alpha=.9); ax.plot([0,mx],[0,mx],':',color=BLACK,lw=1.1,label='identity'); ax.set_xlim(0,mx); ax.set_ylim(0,mx); ax.set_aspect('equal',adjustable='box'); ax.set_xlabel(r'primary $\Delta C_{\rm down}$ (bits)'); ax.set_ylabel(r'exact-margin $\Delta C_{\rm down}$ (bits)'); ax.set_title('Independent erasures agree blockwise',pad=9,fontweight='bold',loc='left',x=0.10); ax.text(-.19,1.035,'(d)',transform=ax.transAxes,fontweight='bold',fontsize=12,clip_on=False); ax.xaxis.set_major_locator(MaxNLocator(4)); ax.yaxis.set_major_locator(MaxNLocator(4)); ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f')); ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f')); ax.legend(frameon=False,loc='lower right'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
save_all(fig,out/'SUPPLEMENTARY_FIGURE_S2_FINAL_v1.0.0'); plt.close(fig)
for p in src2.iterdir():
    if p.is_file(): shutil.copy2(p,out/'sources'/p.name)
shutil.copy2(WORK/'PAIRED_BLOCK_ENDPOINTS_v1.0.0.csv',out/'sources/PAIRED_BLOCK_ENDPOINTS_v1.0.0.csv')
(out/'SUPPLEMENTARY_FIGURE_S2_CAPTION_FINAL_v1.0.0.tex').write_text(rf'''\caption{{\textbf{{Relational erasures remove evolved motif--segment organization and agree across independently evolved blocks.}}
The same top-24 motif identities and row order as Supplementary Fig.~S1 are used. \textbf{{(a)}} Intact generation-250 selected motif--segment enrichment. \textbf{{(b)}} Post-erasure enrichment after the primary factorized counterfactual, which is exactly zero by construction. \textbf{{(c)}} Post-erasure enrichment after the independently constructed exact-margin intervention, shown on a narrow residual scale. Horizontal lines separate motif groups according to their preferred segment in the evolved selected population. \textbf{{(d)}} Blockwise comparison of selected-specific $\Delta C_{{\rm down}}$ under the primary and exact-margin erasures across all four scaffold identities; the dotted line denotes identity. The blockwise Pearson correlation was $r={r:.6f}$ across 120 paired endpoints.}}''')
with open(out/'SUPPLEMENTARY_FIGURE_S2_SOURCE_MAP_v1.0.0.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['panel','source','content']); w.writerow(['a','S6_INTACT_G250_SELECTED_ENRICHMENT.csv','intact selected enrichment']); w.writerow(['b','S6_PRIMARY_POST_ERASURE_ENRICHMENT.csv','primary factorized erasure']); w.writerow(['c','S6_EXACT_MARGIN_POST_ERASURE_ENRICHMENT.csv','exact-margin erasure residuals']); w.writerow(['d','PAIRED_BLOCK_ENDPOINTS_v1.0.0.csv','blockwise agreement of selected-specific erasure effects'])
(out/'README.md').write_text('S2 JRSI result freeze. Panels a-c rebuild the canonical Model B erasure heatmaps; panel d relocates the previously main-text blockwise erasure-agreement evidence into the supplement. No simulations or inferential analyses were rerun.\n')
(out/'FREEZE_NOTE_v1.0.0.md').write_text('Current JRSI S2 combines canonical relational-erasure heatmaps with the frozen blockwise primary-versus-exact-margin agreement diagnostic.\n')
shutil.copy2(Path(__file__),out/'build_supplementary_jrsi_freezes_v1.py'); write_manifest(out); zip_dir(out)

# ---------- S5 ----------
out=ROOT/'SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.0.0'; clean_dir(out)
strength=pd.read_csv(FIG4/'SCAFFOLD_STRENGTH_SUMMARY.csv'); fidelity=pd.read_csv(FIG4/'FIDELITY_SUMMARY.csv')
fig,axs=plt.subplots(1,2,figsize=(12.8,4.5)); fig.subplots_adjust(left=.075,right=.985,top=.87,bottom=.17,wspace=.28)
ax=axs[0]; x=strength.scaffold_strength.to_numpy(); y=strength.fitness_ancestor_mean.to_numpy(); lo=strength.fitness_ancestor_ci95_lo.to_numpy(); hi=strength.fitness_ancestor_ci95_hi.to_numpy(); ax.errorbar(x,y,yerr=np.vstack([y-lo,hi-y]),fmt='o-',color='#526B84',mfc='white',mec='#526B84',ms=4.7,capsize=2.0,lw=1.5,elinewidth=1.0); ax.set_title('Stronger reaction-field scaffold lowers ancestral fitness',loc='left',fontweight='bold'); ax.set_xlabel(r'reaction-field scaffold strength $s$'); ax.set_ylabel('ancestral fitness (generation 0)'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.text(-.12,1.06,'(a)',transform=ax.transAxes,fontweight='bold',fontsize=14)
ax=axs[1]; sub=fidelity[(fidelity.endpoint=='Delta_R_pop') & (fidelity.transmission_fidelity<1.0)].copy(); x=sub.transmission_fidelity.to_numpy(); y=sub['mean'].to_numpy(); lo=sub.ci95_low.to_numpy(); hi=sub.ci95_high.to_numpy(); ax.errorbar(x,y,yerr=np.vstack([y-lo,hi-y]),fmt='o-',color=BLUE,mfc=BLUE,mec=BLUE,ms=4.7,capsize=2.2,lw=1.5,elinewidth=1.0); ax.axhline(0,color='#999999',ls='--',lw=1.0); ax.set_title('Reliable heredity amplifies catalytic relational organization',loc='left',fontweight='bold'); ax.set_xlabel(r'transmission fidelity $p$'); ax.set_ylabel(r'$\Delta R_{\rm pop}$ (bits)'); ax.set_xlim(-.02,.995); ax.set_xticks([0,.2,.4,.6,.8,.975]); ax.set_xticklabels(['0','0.2','0.4','0.6','0.8','0.975']); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.text(-.12,1.06,'(b)',transform=ax.transAxes,fontweight='bold',fontsize=14)
save_all(fig,out/'SUPPLEMENTARY_FIGURE_S5_FINAL_v1.0.0'); plt.close(fig)
for name in ['SCAFFOLD_STRENGTH_SUMMARY.csv','FIDELITY_SUMMARY.csv']:
    shutil.copy2(FIG4/name,out/'sources'/name)
(out/'SUPPLEMENTARY_FIGURE_S5_CAPTION_FINAL_v1.0.0.tex').write_text(r'''\caption{\textbf{Supporting catalytic scaffold and heredity results.}
\textbf{(a)} Generation-0 ancestral fitness decreases as reaction-field scaffold strength $s$ increases in the independent prospective 22-point campaign. At the prespecified $s=2$ anchor, founder cost relative to $s=0$ was $-0.113446$ (97.5\% CI $-0.114071$ to $-0.112819$; 30/30 blocks negative). \textbf{(b)} Selection-generated excess dimer relational organization, $\Delta R_{\rm pop}$, is weak at low transmission fidelity and strongly amplified in the high-fidelity regime in the independent prospective 18-point campaign. The display is restricted to $p<1$; at $p=0.975$, $\Delta R_{\rm pop}=0.088946$ bits.}''')
with open(out/'SUPPLEMENTARY_FIGURE_S5_SOURCE_MAP_v1.0.0.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['panel','source','content']); w.writerow(['a','SCAFFOLD_STRENGTH_SUMMARY.csv','ancestral scaffold cost']); w.writerow(['b','FIDELITY_SUMMARY.csv','Delta R_pop across imperfect transmission fidelity'])
(out/'README.md').write_text('S5 JRSI result freeze. Rebuilt directly from the exact source tables packaged with the current frozen JRSI Figure 4; source hashes are identical to the earlier S5 draft inputs.\n')
(out/'FREEZE_NOTE_v1.0.0.md').write_text('Current JRSI S5. No simulation or inferential rerun; source-faithful presentation of catalytic supporting results.\n')
shutil.copy2(Path(__file__),out/'build_supplementary_jrsi_freezes_v1.py'); write_manifest(out); zip_dir(out)

# ---------- S6 ----------
out=ROOT/'SCO_SUPPLEMENTARY_FIGURE_S6_RESULT_FREEZE_JRSI_v1.0.0'; clean_dir(out)
expr=pd.read_csv(S6SRC/'EXPRESSION_SEPARATION_BY_TIME.csv'); aniso=pd.read_csv(S6SRC/'ANISOTROPY_BY_TIME.csv')
def summarize(df,col):
    g=df.groupby('t')[col].agg(['mean','sem']).reset_index(); return g
se=summarize(expr,'expression_C4'); sa=summarize(aniso,'anisotropy_C5')
fig,axs=plt.subplots(1,2,figsize=(12.8,4.5)); fig.subplots_adjust(left=.075,right=.985,top=.87,bottom=.17,wspace=.28)
ax=axs[0]; ax.errorbar(se.t,se['mean'],yerr=se['sem'],fmt='o-',color=BLUE,mfc=BLUE,mec=BLUE,ms=5,capsize=2.6,lw=1.8,elinewidth=1.0); ax.axhline(0,color='#999999',ls='--',lw=1.0); ax.set_title('Acquisition-expression separation develops over time',loc='left',fontweight='bold'); ax.set_xlabel('generation'); ax.set_ylabel('acquisition-expression contrast'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.text(-.12,1.06,'(a)',transform=ax.transAxes,fontweight='bold',fontsize=14)
ax=axs[1]; ax.errorbar(sa.t,sa['mean'],yerr=sa['sem'],fmt='o-',color=ORANGE,mfc=ORANGE,mec=ORANGE,ms=5,capsize=2.6,lw=1.8,elinewidth=1.0); ax.axhline(0,color='#999999',ls='--',lw=1.0); ax.set_title('Equal-distance anisotropy emerges and stabilizes',loc='left',fontweight='bold'); ax.set_xlabel('generation'); ax.set_ylabel('anisotropy contrast'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.text(-.12,1.06,'(b)',transform=ax.transAxes,fontweight='bold',fontsize=14)
save_all(fig,out/'SUPPLEMENTARY_FIGURE_S6_FINAL_v1.0.0'); plt.close(fig)
for name in ['EXPRESSION_SEPARATION_BY_TIME.csv','ANISOTROPY_BY_TIME.csv','LATTICE_MAPPING_RESULT_FREEZE.md','LATTICE_PRIOR_PROSPECTIVE_RESULT_FREEZE.md']:
    shutil.copy2(S6SRC/name,out/'sources'/name)
(out/'SUPPLEMENTARY_FIGURE_S6_CAPTION_FINAL_v1.0.0.tex').write_text(r'''\caption{\textbf{Post-confirmatory temporal development of two architecture-level signatures in the abstract lattice control.}
\textbf{(a)} Acquisition--expression separation at $p=0.95$ rises toward a stable plateau; the earlier prospective lattice campaign had already confirmed the existence of this signature. \textbf{(b)} Equal-distance anisotropy likewise emerges and stabilizes at $p=0.95$; the earlier prospective campaign prospectively confirmed the corresponding directional contrast. Points show means across 30 independent root-seed blocks and error bars show $\pm 1$ SEM. These trajectories provide post-confirmatory mechanistic mapping and do not replace the prior prospective existence tests.}''')
with open(out/'SUPPLEMENTARY_FIGURE_S6_SOURCE_MAP_v1.0.0.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['panel','source','content']); w.writerow(['a','EXPRESSION_SEPARATION_BY_TIME.csv','acquisition-expression separation over time at p=0.95']); w.writerow(['b','ANISOTROPY_BY_TIME.csv','equal-distance anisotropy over time at p=0.95'])
(out/'README.md').write_text('S6 JRSI result freeze. Programmatic source-faithful rebuild from frozen lattice post-confirmatory block-level trajectories. Error bars are descriptive +/-1 SEM across the 30 root-seed blocks.\n')
(out/'FREEZE_NOTE_v1.0.0.md').write_text('Current JRSI S6. Post-confirmatory temporal mapping only; it does not replace the earlier prospective existence tests.\n')
shutil.copy2(Path(__file__),out/'build_supplementary_jrsi_freezes_v1.py'); write_manifest(out); zip_dir(out)

# ---------- JRSI supplementary manifest ----------
man=ROOT/'JRSI_SUPPLEMENTARY_FIGURE_MANIFEST_v1.0.0'
if man.exists(): shutil.rmtree(man)
man.mkdir()
rows=[
['S1','Selection generates motif-segment relational organization','SCO_SUPPLEMENTARY_FIGURE_S1_RESULT_FREEZE_JRSI_v1.0.0','FROZEN','Model B emergence heatmaps'],
['S2','Relational erasures remove evolved motif-segment organization','SCO_SUPPLEMENTARY_FIGURE_S2_RESULT_FREEZE_JRSI_v1.0.0','FROZEN','Model B erasure heatmaps plus blockwise primary/exact-margin agreement'],
['S3','Independent scaffold-strength replication','SCO_SUPPLEMENTARY_FIGURE_S3_RESULT_FREEZE_JRSI_v1.0.0','FROZEN','7-point versus 22-point replication/support'],
['S4','Acquisition-expression and directional support','SCO_SUPPLEMENTARY_FIGURE_S4_RESULT_FREEZE_JRSI_v1.0.0','FROZEN','expression optimum and strong-versus-weak directional contrast'],
['S5','Supporting catalytic scaffold and heredity results','SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.0.0','FROZEN','ancestral catalytic scaffold cost and Delta R_pop heredity dependence'],
['S6','Post-confirmatory lattice temporal dynamics','SCO_SUPPLEMENTARY_FIGURE_S6_RESULT_FREEZE_JRSI_v1.0.0','FROZEN','acquisition-expression and anisotropy trajectories']]
with open(man/'JRSI_SUPPLEMENTARY_FIGURE_MANIFEST_v1.0.0.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['figure','title','freeze_package','status','role']); w.writerows(rows)
md=['# JRSI Supplementary Figure Manifest v1.0.0','','This is the active supplementary-figure numbering for the rebuilt JRSI manuscript. The earlier extended S1-S21 planning map is superseded for current manuscript figure numbering; archived analyses remain available in their original freezes but are not assigned active figure numbers here.','','| Figure | Current role | Status | Freeze package |','|---|---|---|---|']
for fig,title,pkg,status,role in rows: md.append(f'| {fig} | {role} | {status} | `{pkg}` |')
md += ['','## Numbering doctrine','- S1-S2: Model B relational organization and intervention diagnostics.','- S3-S4: Model B replication and acquisition/directional support.','- S5: catalytic supporting evidence.','- S6: lattice post-confirmatory temporal mapping.','- Main-text figure references should use Supplementary Fig. S#, never Extended Data.','- The old S1-S21 planning numbering is not to be used in the current JRSI manuscript.']
(man/'JRSI_SUPPLEMENTARY_FIGURE_MANIFEST_v1.0.0.md').write_text('\n'.join(md)+'\n')
(man/'README.md').write_text('Active JRSI supplementary figure manifest after manuscript restructuring. All six active supplementary figures are frozen.\n')
write_manifest(man)
zip_dir(man)

# combined convenience bundle containing manifest + six freeze zips
bundle=ROOT/'JRSI_SUPPLEMENTARY_FIGURES_S1_TO_S6_FREEZE_BUNDLE_v1.0.0.zip'
if bundle.exists(): bundle.unlink()
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(man.rglob('*')):
        if p.is_file(): z.write(p,arcname=str(Path(man.name)/p.relative_to(man)))
    for pkg in [
        'SCO_SUPPLEMENTARY_FIGURE_S1_RESULT_FREEZE_JRSI_v1.0.0.zip',
        'SCO_SUPPLEMENTARY_FIGURE_S2_RESULT_FREEZE_JRSI_v1.0.0.zip',
        'SCO_SUPPLEMENTARY_FIGURE_S3_RESULT_FREEZE_JRSI_v1.0.0.zip',
        'SCO_SUPPLEMENTARY_FIGURE_S4_RESULT_FREEZE_JRSI_v1.0.0.zip',
        'SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.0.0.zip',
        'SCO_SUPPLEMENTARY_FIGURE_S6_RESULT_FREEZE_JRSI_v1.0.0.zip']:
        pp=ROOT/pkg
        if pp.exists(): z.write(pp,arcname=pp.name)

print('created:')
for p in [
ROOT/'SCO_SUPPLEMENTARY_FIGURE_S1_RESULT_FREEZE_JRSI_v1.0.0.zip',
ROOT/'SCO_SUPPLEMENTARY_FIGURE_S2_RESULT_FREEZE_JRSI_v1.0.0.zip',
ROOT/'SCO_SUPPLEMENTARY_FIGURE_S5_RESULT_FREEZE_JRSI_v1.0.0.zip',
ROOT/'SCO_SUPPLEMENTARY_FIGURE_S6_RESULT_FREEZE_JRSI_v1.0.0.zip',
ROOT/'JRSI_SUPPLEMENTARY_FIGURE_MANIFEST_v1.0.0.zip',bundle]: print(p)
