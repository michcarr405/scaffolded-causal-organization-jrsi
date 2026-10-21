from pathlib import Path
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
OUT=Path('/mnt/data/reduced_theory_v03_T5')
d=pd.read_csv(OUT/'T5_direction_summary.csv').sort_values('phi_deg')
# Angular/profile line figure
fig,ax=plt.subplots(figsize=(7.2,4.6))
ax.plot(d.phi_deg,d.DeltaH_mean,'o-',label='Observed T5 mean')
ax.plot(d.phi_deg,d.pred_obs_affine,'s--',label='Frozen prediction')
ax.set_xlabel('Probe direction (degrees)')
ax.set_ylabel('Historical-match loss, selected - neutral')
ax.set_title('Equal-distance scaffold changes have direction-specific effects')
ax.set_xticks(d.phi_deg)
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(OUT/'T5_angular_profile.png',dpi=220); plt.close(fig)
# predicted-observed scatter
fig,ax=plt.subplots(figsize=(5.3,5.0))
ax.scatter(d.pred_obs_affine,d.DeltaH_mean,s=45)
lo=min(d.pred_obs_affine.min(),d.DeltaH_mean.min()); hi=max(d.pred_obs_affine.max(),d.DeltaH_mean.max())
ax.plot([lo,hi],[lo,hi],'--',linewidth=1)
for _,r in d.iterrows(): ax.annotate(r.probe_id,(r.pred_obs_affine,r.DeltaH_mean),xytext=(4,3),textcoords='offset points',fontsize=8)
ax.set_xlabel('Frozen predicted DeltaH')
ax.set_ylabel('Observed T5 mean DeltaH')
ax.set_title('Prospective anisotropic-response prediction')
fig.tight_layout(); fig.savefig(OUT/'T5_predicted_vs_observed.png',dpi=220); plt.close(fig)
