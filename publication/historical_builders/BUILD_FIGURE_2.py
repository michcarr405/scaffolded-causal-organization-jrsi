from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'sources'
OUT = ROOT

r22 = pd.read_csv(SRC/'RATIO_SUMMARY_22pt_confirmatory_v1.0.0.csv')
ms = pd.read_csv(SRC/'MAPPING_SUMMARY_v1.0.0.csv')
cross_raw = pd.read_csv(SRC/'CROSS_EVAL_SELECTED_MINUS_NEUTRAL_MATRIX_v1.0.0.csv')
cross = cross_raw.set_index('training_scaffold')[['SCF0','SCF1','SCF2','SCF3']]

assert len(r22) == 22 and set(r22.n_blocks) == {30}
for fam in ['D_primary','A_unitshuffle']:
    sub = ms[ms.family == fam]
    assert list(sub.scaffold_id) == ['SCF0','SCF1','SCF2','SCF3']
    assert (sub.n == 30).all() and (sub.positive_blocks == 30).all()

mpl.rcParams.update({
    'font.family':'DejaVu Sans',
    'font.size':9.5,
    'axes.titlesize':11.5,
    'axes.labelsize':10.0,
    'xtick.labelsize':8.8,
    'ytick.labelsize':8.8,
    'legend.fontsize':8.4,
    'pdf.fonttype':42,
    'ps.fonttype':42,
    'svg.fonttype':'none',
    'axes.linewidth':0.9,
    'figure.facecolor':'white',
    'savefig.facecolor':'white'
})

BLUE='#0072B2'; ORANGE='#E69F00'; GRAY='#666666'
zero_kw = dict(color='#9A9A9A', lw=0.9, ls='--', zorder=0)
scfs = ['SCF0','SCF1','SCF2','SCF3']

fig = plt.figure(figsize=(12.6,8.8))
gs = fig.add_gridspec(2,2,left=0.075,right=0.965,top=0.95,bottom=0.09,wspace=0.28,hspace=0.40)

# (a) ancestral cost
ax = fig.add_subplot(gs[0,0])
x = r22.beta_over_theta.to_numpy()
ax.errorbar(x, r22.F0_mean,
            yerr=[r22.F0_mean-r22.F0_ci95_lo, r22.F0_ci95_hi-r22.F0_mean],
            fmt='o-', color='#526B84', mfc='white', mec='#526B84', ms=4.2,
            capsize=1.8, lw=1.45, elinewidth=1.0)
ax.set_title('Stronger scaffold lowers ancestral performance', loc='left', pad=8, fontweight='bold')
ax.set_xlabel(r'physical scaffold strength $\beta/\Theta$')
ax.set_ylabel('ancestral reproductive score (generation 0)')
ax.set_xlim(-0.15,8.15); ax.set_xticks(range(0,9))
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.12,1.07,'(a)', transform=ax.transAxes, fontsize=15, fontweight='bold', va='top')

# (b) recovery
ax = fig.add_subplot(gs[0,1])
ax.errorbar(x, r22.G_selected_mean,
            yerr=[r22.G_selected_mean-r22.G_selected_ci95_lo, r22.G_selected_ci95_hi-r22.G_selected_mean],
            fmt='o-', color=BLUE, ms=4.2, capsize=1.8, lw=1.45, elinewidth=1.0,
            label='selected - ancestor')
ax.errorbar(x, r22.G_neutral_mean,
            yerr=[r22.G_neutral_mean-r22.G_neutral_ci95_lo, r22.G_neutral_ci95_hi-r22.G_neutral_mean],
            fmt='s--', color=ORANGE, mfc='white', mec=ORANGE, ms=4.0, capsize=1.8,
            lw=1.2, elinewidth=1.0, label='neutral - ancestor')
ax.axhline(0, **zero_kw)
ax.set_title('Selection drives compensatory recovery', loc='left', pad=8, fontweight='bold')
ax.set_xlabel(r'physical scaffold strength $\beta/\Theta$')
ax.set_ylabel('change from ancestral reproductive score')
ax.set_xlim(-0.15,8.15); ax.set_xticks(range(0,9))
ax.legend(frameon=False, loc='upper left')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.12,1.07,'(b)', transform=ax.transAxes, fontsize=15, fontweight='bold', va='top')

# (c) causal erasure
ax = fig.add_subplot(gs[1,0])
xs=np.arange(4)
for off,fam,color,fmt,label in [
    (-0.07,'D_primary',BLUE,'o','primary erasure'),
    (0.07,'A_unitshuffle',ORANGE,'D','exact-margin erasure')
]:
    sub=ms[ms.family==fam].set_index('scaffold_id').loc[scfs]
    y=sub['mean'].to_numpy(); lo=sub['ci_low'].to_numpy(); hi=sub['ci_high'].to_numpy()
    ax.errorbar(xs+off,y,yerr=[y-lo,hi-y],fmt=fmt,color=color,
                mfc=('white' if fam=='A_unitshuffle' else color),mec=color,
                ms=6,capsize=3,lw=1.15,elinewidth=1.15,label=label)
ax.axhline(0, **zero_kw)
ax.set_xticks(xs,scfs)
ax.set_ylabel(r'selected-specific $\Delta C_{\rm down}$ (bits)')
ax.set_title('Relation erasure changes lower-level chemistry', loc='left', pad=8, fontweight='bold')
# Final approved layout: legend in lower-right open region.
ax.legend(frameon=False, loc='lower right', bbox_to_anchor=(0.98, 0.47), borderaxespad=0.0)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
ax.text(-0.12,1.07,'(c)', transform=ax.transAxes, fontsize=15, fontweight='bold', va='top')

# (d) history specificity
subgs = gs[1,1].subgridspec(1,3,width_ratios=[1.0,0.06,0.30],wspace=0.25)
ax = fig.add_subplot(subgs[0,0]); cax=fig.add_subplot(subgs[0,1]); hax=fig.add_subplot(subgs[0,2])
mat = cross.to_numpy()
norm = TwoSlopeNorm(vmin=-3.0,vcenter=0.0,vmax=12.0)
im=ax.imshow(mat,cmap='RdBu_r',norm=norm,aspect='equal')
for i in range(4):
    for j in range(4):
        v=mat[i,j]
        txt='-0.0' if (v<0 and abs(v)<0.05) else f'{v:.1f}'
        color='white' if abs(v)>2.4 or v>8 else 'black'
        ax.text(j,i,txt,ha='center',va='center',fontsize=9.2,
                fontweight=('bold' if i==j else 'normal'),color=color)
for i in range(4):
    ax.add_patch(Rectangle((i-0.48,i-0.48),0.96,0.96,fill=False,ec='#222222',lw=1.8))
ax.set_xticks(range(4),scfs); ax.set_yticks(range(4),scfs)
ax.set_xlabel('current probe scaffold'); ax.set_ylabel('evolutionary scaffold')
ax.set_title('Common-probe responses retain evolutionary history',loc='left',pad=8,fontweight='bold')
ax.text(-0.19,1.07,'(d)', transform=ax.transAxes, fontsize=15, fontweight='bold', va='top')
cb=fig.colorbar(im,cax=cax); cb.ax.tick_params(labelsize=8); cax.text(0.5,-0.07,r'$\Delta F$',transform=cax.transAxes,ha='center',va='top',fontsize=9)
hvals=cross_raw.historical_advantage_delta_H.to_numpy()
hax.set_facecolor('#F4F4F4'); hax.set_xlim(0,1); hax.set_ylim(0,1); hax.set_xticks([]); hax.set_yticks([])
for sp in hax.spines.values(): sp.set_visible(False)
hax.text(0.5,0.93,r'$\Delta H$',ha='center',va='top',fontsize=11.5,fontstyle='italic')
for y,v in zip([0.74,0.56,0.38,0.20],hvals):
    hax.text(0.5,y,f'{v:.2f}',ha='center',va='center',fontsize=10.0,fontweight='bold')
hax.plot([0.15,0.85],[0.11,0.11],color='#999999',lw=0.8)
hax.text(0.5,0.06,'30/30 each\npooled 11.91',ha='center',va='center',fontsize=7.3,color=GRAY,linespacing=1.1)

stem=OUT/'FIGURE_2_FINAL_v1.0.0'
fig.savefig(str(stem)+'.pdf',bbox_inches='tight')
fig.savefig(str(stem)+'.png',dpi=400,bbox_inches='tight')
plt.close(fig)
