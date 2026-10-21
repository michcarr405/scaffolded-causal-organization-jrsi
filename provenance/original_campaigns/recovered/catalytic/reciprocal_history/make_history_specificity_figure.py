import pandas as pd, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
root=Path('/mnt/data/CATALYTIC_COMPLEX_HISTORY_SPECIFICITY_CONFIRMATORY_v1.0.0')
df=pd.read_csv(root/'results/BLOCK_HISTORY_SPECIFICITY_RESULTS.csv')
mat=np.array([[df.R1_H1.mean(),df.R1_H2.mean()],[df.R2_H1.mean(),df.R2_H2.mean()]])
res=pd.read_csv(root/'results/FORMAL_RESULT.csv').iloc[0]
fig,axs=plt.subplots(1,2,figsize=(8.2,3.4),dpi=220,gridspec_kw={'width_ratios':[1,1.35]})
# heatmap
ax=axs[0]
lim=np.max(np.abs(mat))*1.12
im=ax.imshow(mat,cmap='RdBu_r',vmin=-lim,vmax=lim,aspect='equal')
ax.set_xticks([0,1],['current H1','current H2']); ax.set_yticks([0,1],['history H1','history H2'])
ax.set_title('Selected-minus-neutral\nfitness response',fontweight='bold')
for i in range(2):
 for j in range(2):
  ax.text(j,i,f'{mat[i,j]:+.3f}',ha='center',va='center',fontsize=10,fontweight='bold')
cb=fig.colorbar(im,ax=ax,fraction=.046,pad=.04); cb.set_label('fitness response')
# blocks
ax=axs[1]
x=np.arange(1,len(df)+1); y=df.H_fit.values
ax.axhline(0,color='0.6',ls='--',lw=1)
ax.scatter(x,y,s=20,zorder=3)
mean=float(res['mean']); lo=float(res['ci99_low']); hi=float(res['ci99_high'])
ax.axhline(mean,color='black',lw=1.4,label=f'mean = {mean:.3f}')
ax.fill_between([0.5,30.5],[lo,lo],[hi,hi],alpha=.13,color='black',label='99% bootstrap CI')
ax.set_xlim(.5,30.5); ax.set_xlabel('root-seed block'); ax.set_ylabel(r'$H_{fit}$ (fitness units)')
ax.set_title('Reciprocal matching-history contrast',fontweight='bold')
ax.text(.03,.96,f"29/30 positive\nsign p = {float(res['sign_p_one_sided']):.2e}",transform=ax.transAxes,ha='left',va='top',fontsize=9)
ax.spines[['top','right']].set_visible(False)
fig.tight_layout()
fig.savefig(root/'CATALYTIC_HISTORY_SPECIFICITY_CONFIRMATION_v1.0.0.pdf')
fig.savefig(root/'CATALYTIC_HISTORY_SPECIFICITY_CONFIRMATION_v1.0.0.png',dpi=300)
