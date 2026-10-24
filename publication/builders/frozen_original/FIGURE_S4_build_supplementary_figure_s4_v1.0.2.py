from pathlib import Path
import json, hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PKG = Path(__file__).resolve().parent
SRC = PKG / 'sources'

t3 = pd.read_csv(SRC / 'T3_PEAK_RESULTS.csv')
p5 = pd.read_csv(SRC / 'T5_PROBE_LEVEL_RESULTS.csv')
s3 = json.load(open(SRC / 'T3_RESULT_SUMMARY.json'))
s5 = json.load(open(SRC / 'T5_RESULT_SUMMARY.json'))

BLUE='#1f77b4'; ORANGE='#ff7f0e'; DARK='#303030'
plt.rcParams.update({
    'font.family':'DejaVu Sans',
    'font.size':10.5,
    'axes.labelsize':12,
    'axes.titlesize':14.0,
    'axes.titleweight':'bold',
    'xtick.labelsize':10,
    'ytick.labelsize':10,
    'legend.fontsize':9.2,
    'axes.linewidth':1.0,
    'pdf.fonttype':42,
    'ps.fonttype':42,
})

def style(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out', length=5, width=1)

def title(ax,label,text):
    ax.text(-0.13,1.055,f'({label})',transform=ax.transAxes,fontsize=15.5,
            fontweight='bold',va='bottom',clip_on=False)
    ax.text(0,1.055,text,transform=ax.transAxes,fontsize=12.3,
            fontweight='bold',va='bottom',clip_on=False,linespacing=.96)

# Exact frozen S4 canvas geometry: 12.8 x 4.8 inches => 4480 x 1680 at 350 dpi.
fig = plt.figure(figsize=(12.8,4.8))
gs = fig.add_gridspec(1,2,left=.075,right=.975,top=.875,bottom=.19,wspace=.30)
A = fig.add_subplot(gs[0,0])
B = fig.add_subplot(gs[0,1])

# Panel (a): source-faithful rebuild of the frozen acquisition-expression panel.
style(A)
title(A,'a','Training history predicts maximal expression')
qt=t3.q_train.to_numpy(); pred=t3.q_peak_pred.to_numpy(); obs=t3.q_peak_obs.to_numpy()
order=np.argsort(qt); qt=qt[order]; pred=pred[order]; obs=obs[order]
step=.125
A.plot(qt,pred,color=BLUE,lw=1.7,label='prespecified prediction')
A.fill_between(qt,pred-step,pred+step,color=BLUE,alpha=.15,label='one grid interval')
A.scatter(qt,obs,s=48,color=ORANGE,zorder=5,label='observed peak')
A.set_xlabel(r'training scaffold strength $\beta/\Theta$')
A.set_ylabel('probe strength at maximal expression')
A.set_xlim(qt.min()-.18,qt.max()+.20)
A.set_ylim(min((pred-step).min(),obs.min())-.08,max((pred+step).max(),obs.max())+.08)
A.legend(frameon=False,loc='upper left')
A.text(.96,.08,
       f"5/5 peaks within one grid step\nno-refit surface $R^2$ = {s3['full_curve_no_refit']['R2']:.3f}",
       transform=A.transAxes,ha='right',fontsize=9.1)

# Panel (b): same frozen data and statistics; only reader-facing aliases are replaced by angles.
style(B)
title(B,'b','Prespecified directional contrast succeeds')
weak = p5[p5.probe_id=='P09'].sort_values('block_index').DeltaH.to_numpy()
strong = p5[p5.probe_id=='P13'].sort_values('block_index').DeltaH.to_numpy()
mn=min(weak.min(),strong.min())-.5; mx=max(weak.max(),strong.max())+.5
B.plot([mn,mx],[mn,mx],':',color=DARK,lw=1.2)
B.scatter(weak,strong,s=34,facecolor='white',edgecolor=BLUE,lw=1.3)
B.set_xlim(mn,mx); B.set_ylim(mn,mx)
B.set_xlabel(r'$202.5^{\circ}$ response (predicted weak direction)', fontsize=10.7)
B.set_ylabel(r'$292.5^{\circ}$ response (predicted strong direction)', fontsize=10.7, labelpad=7)
B.text(.55,.10,
       f"292.5° > 202.5°: {s5['top_gt_bottom_blocks']}/30 blocks\n"
       f"sign $p$ = {s5['extremal_sign_p']:.2e}\n"
       f"anisotropy $p$ = {s5['anisotropy_permutation_p']:.2e}",
       transform=B.transAxes,fontsize=9.1)

base = PKG / 'SUPPLEMENTARY_FIGURE_S4_FINAL_v1.0.2'
fig.savefig(str(base)+'.pdf',facecolor='white')
fig.savefig(str(base)+'.png',dpi=350,facecolor='white')
fig.savefig(str(base)+'.svg',facecolor='white')
fig.savefig(PKG/'rendered'/'page-1.png',dpi=180,facecolor='white')
plt.close(fig)
