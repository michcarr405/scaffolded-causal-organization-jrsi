import pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path
B=Path('/mnt/data/reaction_net_pilot/discovery_v02')
# timecourse fitness
T=pd.read_csv(B/'A_timecourse.csv')
for metric,title,ylabel,out in [
 ('fitness_mean','Fitness recovery under the reaction-field scaffold','Mean fitness','fig_A_fitness_timecourse.png'),
 ('C_pop','Relational causal effect on reaction-state distribution','Population JSD (bits)','fig_B_causal_timecourse.png')]:
 fig,ax=plt.subplots(figsize=(6.4,4.2))
 for mode,g in T.groupby('mode'):
  s=g.groupby('generation')[metric].agg(['mean','sem']).reset_index()
  ax.errorbar(s.generation,s['mean'],yerr=s['sem'],marker='o',label=mode)
 ax.set_xlabel('Generation');ax.set_ylabel(ylabel);ax.set_title(title);ax.legend(frameon=False);fig.tight_layout();fig.savefig(B/out,dpi=180);plt.close(fig)
# fidelity delta
F=pd.read_csv(B/'B_fidelity_summary.csv')
fig,ax=plt.subplots(figsize=(6.4,4.2));ax.plot(F.p,F.Delta_C_pop,marker='o');ax.axhline(0,ls='--',lw=.8);ax.set_xlabel('Transmission fidelity p');ax.set_ylabel('Selected - neutral relational JSD (bits)');ax.set_title('Inherited causal organization concentrates at high fidelity');fig.tight_layout();fig.savefig(B/'fig_C_fidelity.png',dpi=180);plt.close(fig)
# retrieval curves
C=pd.read_csv(B/'C_retrieval_mean.csv')
fig,ax=plt.subplots(figsize=(6.4,4.2))
for ts,g in C.groupby('train_strength'):
 ax.plot(g.probe_strength,g.DeltaC,marker='o',ms=3,label=f'train {ts:g}')
ax.axhline(0,ls='--',lw=.8);ax.set_xlabel('Probe scaffold strength');ax.set_ylabel('Selected - neutral relational JSD (bits)');ax.set_title('Frozen populations: causal expression depends on probe strength');ax.legend(frameon=False);fig.tight_layout();fig.savefig(B/'fig_D_retrieval.png',dpi=180);plt.close(fig)
# anisotropy
D=pd.read_csv(B/'D_anisotropy.csv');dm=D.groupby('phi_deg').DeltaH.agg(['mean','sem']).reset_index()
fig,ax=plt.subplots(figsize=(6.4,4.2));ax.errorbar(dm.phi_deg,dm['mean'],yerr=dm['sem'],marker='o');ax.set_xlabel('Equal-distance scaffold direction (degrees)');ax.set_ylabel('Historical-match advantage ΔH');ax.set_title('Equal-magnitude scaffold changes have directional effects');fig.tight_layout();fig.savefig(B/'fig_E_anisotropy.png',dpi=180);plt.close(fig)
# matrix ensemble
E=pd.read_csv(B/'E_matrix_ensemble_summary.csv')
fig,ax=plt.subplots(figsize=(6.4,4.2));x=np.arange(len(E));ax.axhline(0,ls='--',lw=.8);ax.plot(x,E.DeltaV,marker='o');ax.set_xticks(x);ax.set_xticklabels(E.A_seed.astype(str),rotation=45);ax.set_xlabel('Independent catalytic matrix seed');ax.set_ylabel('Selected - neutral relation-specific fitness effect');ax.set_title('Adaptive value of relational organization across microscopic matrices');fig.tight_layout();fig.savefig(B/'fig_F_matrix_ensemble.png',dpi=180);plt.close(fig)
