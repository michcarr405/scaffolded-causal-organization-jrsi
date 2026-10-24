from pathlib import Path
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
SRC = ROOT/'sources'
OUT = ROOT
r22 = pd.read_csv(SRC/'RATIO_SUMMARY_22pt_confirmatory_v1.0.0.csv')
r7 = pd.read_csv(SRC/'RATIO_SUMMARY_7pt_primary_v1.0.0.csv')
assert len(r22)==22 and len(r7)==7
assert set(r22.n_blocks)=={30} and set(r7.n_blocks)=={30}

mpl.rcParams.update({
    'font.family':'DejaVu Sans',
    'axes.titlesize':13,
    'axes.titleweight':'bold',
    'axes.labelsize':11,
    'xtick.labelsize':10,
    'ytick.labelsize':10,
    'legend.fontsize':10,
    'figure.facecolor':'white',
    'savefig.facecolor':'white'
})

colors={'a':'#708090','b':'#1f77b4','c':'#19a979','seven':'#e67e22'}

def err(mean, lo, hi, df):
    return [(df[mean]-df[lo]).to_numpy(), (df[hi]-df[mean]).to_numpy()]

fig, axes = plt.subplots(1,3,figsize=(16,5),constrained_layout=True)

ax=axes[0]
ax.errorbar(r22.beta_over_theta,r22.F0_mean,yerr=err('F0_mean','F0_ci95_lo','F0_ci95_hi',r22),fmt='o-',color=colors['a'],mfc='white',mec=colors['a'],mew=1.2,markersize=4.8,lw=1.4,elinewidth=1.0,capsize=2.5,label='22-point campaign')
ax.errorbar(r7.beta_over_theta,r7.F0_mean,yerr=err('F0_mean','F0_ci95_lo','F0_ci95_hi',r7),fmt='s',color=colors['seven'],mfc='white',mec=colors['seven'],mew=1.3,markersize=6.0,lw=0,elinewidth=1.0,capsize=2.5,label='7-point campaign')
ax.set_title('(a)   Ancestral scaffold cost',loc='left',pad=8); ax.set_xlabel(r'$\beta/\Theta$'); ax.set_ylabel('ancestral reproductive score'); ax.set_xlim(-0.15,8.15); ax.set_ylim(-1,max(r22.F0_mean.max(),r7.F0_mean.max())+3); ax.legend(frameon=False,loc='upper right')

ax=axes[1]
ax.errorbar(r22.beta_over_theta,r22.G_selected_mean,yerr=err('G_selected_mean','G_selected_ci95_lo','G_selected_ci95_hi',r22),fmt='o-',color=colors['b'],mfc=colors['b'],mec=colors['b'],mew=1.0,markersize=4.8,lw=1.4,elinewidth=1.0,capsize=2.5,label='22-point campaign')
ax.errorbar(r7.beta_over_theta,r7.G_selected_mean,yerr=err('G_selected_mean','G_selected_ci95_lo','G_selected_ci95_hi',r7),fmt='s',color=colors['seven'],mfc='white',mec=colors['seven'],mew=1.3,markersize=6.0,lw=0,elinewidth=1.0,capsize=2.5,label='7-point campaign')
ax.axhline(0,color='0.7',ls='--',lw=1); ax.set_title('(b)   Selected recovery from ancestor',loc='left',pad=8); ax.set_xlabel(r'$\beta/\Theta$'); ax.set_ylabel('selected - ancestral score'); ax.set_xlim(-0.15,8.15); ax.set_ylim(-0.6,max(r22.G_selected_mean.max(),r7.G_selected_mean.max())+1.5); ax.legend(frameon=False,loc='upper right')

ax=axes[2]
ax.errorbar(r22.beta_over_theta,r22.DeltaF_mean,yerr=err('DeltaF_mean','DeltaF_ci95_lo','DeltaF_ci95_hi',r22),fmt='o-',color=colors['c'],mfc=colors['c'],mec=colors['c'],mew=1.0,markersize=4.8,lw=1.4,elinewidth=1.0,capsize=2.5,label='22-point campaign')
ax.errorbar(r7.beta_over_theta,r7.DeltaF_mean,yerr=err('DeltaF_mean','DeltaF_ci95_lo','DeltaF_ci95_hi',r7),fmt='s',color=colors['seven'],mfc='white',mec=colors['seven'],mew=1.3,markersize=6.0,lw=0,elinewidth=1.0,capsize=2.5,label='7-point campaign')
ax.axhline(0,color='0.7',ls='--',lw=1); ax.set_title('(c)   Selected - neutral endpoint difference',loc='left',pad=8); ax.set_xlabel(r'$\beta/\Theta$'); ax.set_ylabel(r'$\Delta F$ (score units)'); ax.set_xlim(-0.15,8.15); ax.set_ylim(-0.6,max(r22.DeltaF_mean.max(),r7.DeltaF_mean.max())+1.5); ax.legend(frameon=False,loc='upper right')

for ax in axes:
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False); ax.tick_params(direction='out',length=4,width=0.8)

stem=OUT/'SUPPLEMENTARY_FIGURE_S3_FINAL_v1.0.0'
fig.savefig(str(stem)+'.pdf',bbox_inches='tight')
fig.savefig(str(stem)+'.png',dpi=200,bbox_inches='tight')
plt.close(fig)
