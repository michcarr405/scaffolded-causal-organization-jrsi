import pandas as pd, numpy as np, matplotlib.pyplot as plt
from pathlib import Path
B=Path('/mnt/data/reaction_net_confirmatory')
df=pd.read_csv(B/'CONFIRM_BLOCK_RESULTS.csv'); dd=pd.read_csv(B/'CONFIRM_DIRECTION_RESULTS.csv')
# paired endpoints
for col,title,ylabel,out in [
 ('Delta_fitness','Selection-dependent fitness recovery','Selected - neutral fitness','fig_confirm_fitness.png'),
 ('Delta_V_rel','Adaptive effect of inherited dimer relations','Selected - neutral relational fitness effect','fig_confirm_relational_value.png'),
 ('Delta_R_pop','Selection-generated dimer organization','Selected - neutral relational organization (JSD)','fig_confirm_relational_org.png')]:
 fig,ax=plt.subplots(figsize=(6.2,4.1));x=np.arange(1,len(df)+1);ax.scatter(x,df[col]);ax.axhline(0,ls='--',lw=.8);ax.set_xlabel('Independent root-seed block');ax.set_ylabel(ylabel);ax.set_title(title);fig.tight_layout();fig.savefig(B/out,dpi=180);plt.close(fig)
# masking paired
fig,ax=plt.subplots(figsize=(6.2,4.1));ax.scatter(df.Delta_C_pop,df.DeltaC_probe05);lo=min(df.Delta_C_pop.min(),df.DeltaC_probe05.min());hi=max(df.Delta_C_pop.max(),df.DeltaC_probe05.max());ax.plot([lo,hi],[lo,hi],ls='--',lw=.8);ax.set_xlabel('ΔC at training scaffold strength 2.0');ax.set_ylabel('ΔC at weaker probe strength 0.5');ax.set_title('Same frozen populations reveal more causal effect under weaker probing');fig.tight_layout();fig.savefig(B/'fig_confirm_masking.png',dpi=180);plt.close(fig)
# anisotropy profile
s=dd.groupby('phi_deg').DeltaH.agg(['mean','sem']).reset_index();fig,ax=plt.subplots(figsize=(6.2,4.1));ax.errorbar(s.phi_deg,s['mean'],yerr=s['sem'],marker='o');ax.set_xlabel('Equal-distance scaffold direction (degrees)');ax.set_ylabel('Historical-match advantage ΔH');ax.set_title('Directional historical specificity at fixed scaffold distance');fig.tight_layout();fig.savefig(B/'fig_confirm_anisotropy.png',dpi=180);plt.close(fig)
