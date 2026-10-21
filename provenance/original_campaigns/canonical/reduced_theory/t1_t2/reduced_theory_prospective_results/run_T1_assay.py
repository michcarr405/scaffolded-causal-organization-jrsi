from pathlib import Path
import re, json, math
import numpy as np
import pandas as pd
import sys

ROOT=Path('/mnt/data/prospective_test_work/strength/MODEL_B_DCC_SCAFFOLD_STRENGTH_CONFIRMATORY_RUN_v1.0.0')
sys.path.insert(0,str(ROOT/'scripts'))
from strength_pipeline import c_down_primary, params_for, NATIVE, THETA

OUT=Path('/mnt/data/reduced_theory_prospective_T1')
qgrid=np.round(np.arange(0.0,5.0001,0.25),2)
primary={1.5,2.5,3.0,3.5,4.0}
q0=2.5
c=-0.24648168999601677
gamma=0.5700229862715289

def suscept(q):
    z=c+gamma*np.asarray(q,float)
    s=1/(1+np.exp(-z))
    return s*(1-s)

def pred_ratio(q):
    return suscept(q)/suscept(q0)

rows=[]
files=sorted((ROOT/'raw'/'states').glob('*_g250.npz'))
pat=re.compile(r'^(STR_B\d+)_([A-Z0-9]+)_(SELECTED|NEUTRAL)_g250\.npz$')
for idx,f in enumerate(files):
    m=pat.match(f.name)
    if not m:
        continue
    block, rid, mode=m.groups()
    z=np.load(f)
    pop=z['g250']
    qtrain=float(z['beta_over_theta'])
    beta_train=float(z['beta'])
    params=params_for(beta_train)
    affinity=params['motif_affinity_matrix']
    for q in qgrid:
        beta=float(q*THETA)
        cd=c_down_primary(pop,affinity,NATIVE,beta,THETA)['jsd_bits']
        rows.append(dict(block_id=block,ratio_id=rid,mode=mode.lower(),q_train=qtrain,beta_train=beta_train,q_probe=float(q),beta_probe=beta,C_down=float(cd)))
    if (idx+1)%100==0:
        print('processed',idx+1,'/',len(files), flush=True)

df=pd.DataFrame(rows)
df.to_csv(OUT/'T1_raw_assays.csv',index=False)

wide=df.pivot_table(index=['block_id','ratio_id','q_train','q_probe'],columns='mode',values='C_down').reset_index()
wide['DeltaC']=wide['selected']-wide['neutral']
wide.to_csv(OUT/'T1_block_DeltaC.csv',index=False)

summary=(wide.groupby(['ratio_id','q_train','q_probe'])
         .agg(n_blocks=('DeltaC','size'),DeltaC_mean=('DeltaC','mean'),DeltaC_sd=('DeltaC','std'),C_selected_mean=('selected','mean'),C_neutral_mean=('neutral','mean'))
         .reset_index())
# normalize by condition-level mean at q0
bases=summary.loc[np.isclose(summary.q_probe,q0),['ratio_id','DeltaC_mean']].rename(columns={'DeltaC_mean':'DeltaC_q0'})
summary=summary.merge(bases,on='ratio_id',how='left')
summary['retrieval_ratio']=summary['DeltaC_mean']/summary['DeltaC_q0']
summary['pred_ratio']=pred_ratio(summary['q_probe'].values)
summary['residual']=summary['retrieval_ratio']-summary['pred_ratio']
summary.to_csv(OUT/'T1_summary.csv',index=False)

# blockwise ratios secondary
baseb=wide.loc[np.isclose(wide.q_probe,q0),['block_id','ratio_id','DeltaC']].rename(columns={'DeltaC':'DeltaC_q0_block'})
wb=wide.merge(baseb,on=['block_id','ratio_id'],how='left')
wb['retrieval_ratio_block']=wb['DeltaC']/wb['DeltaC_q0_block']
wb.to_csv(OUT/'T1_block_ratios.csv',index=False)

# fixed prediction primary stats
prim=summary[summary.q_train.isin(primary)].copy()
def r2(y,yh):
    y=np.asarray(y,float); yh=np.asarray(yh,float)
    ss=np.sum((y-yh)**2); den=np.sum((y-y.mean())**2)
    return float(1-ss/den)
def rmse(y,yh):
    return float(np.sqrt(np.mean((np.asarray(y)-np.asarray(yh))**2)))

stats=[]
stats.append(dict(scope='pooled_primary',q_train=np.nan,n=len(prim),R2=r2(prim.retrieval_ratio,prim.pred_ratio),RMSE=rmse(prim.retrieval_ratio,prim.pred_ratio)))
for qt,g in prim.groupby('q_train'):
    stats.append(dict(scope='per_training',q_train=float(qt),n=len(g),R2=r2(g.retrieval_ratio,g.pred_ratio),RMSE=rmse(g.retrieval_ratio,g.pred_ratio)))
statsdf=pd.DataFrame(stats)
statsdf.to_csv(OUT/'T1_prediction_stats.csv',index=False)

mean_curve=(prim.groupby('q_probe').agg(retrieval_ratio_mean=('retrieval_ratio','mean'),retrieval_ratio_sd_across_training=('retrieval_ratio','std'),pred_ratio=('pred_ratio','first')).reset_index())
mean_curve['residual']=mean_curve.retrieval_ratio_mean-mean_curve.pred_ratio
mean_curve.to_csv(OUT/'T1_mean_retrieval_curve.csv',index=False)
peak_row=mean_curve.loc[mean_curve.retrieval_ratio_mean.idxmax()]

# free susceptibility refit and linear/quadratic diagnostics to mean curve
from scipy.optimize import curve_fit
x=mean_curve.q_probe.values; y=mean_curve.retrieval_ratio_mean.values

def mod(q,c2,g2):
    z=c2+g2*np.asarray(q,float); s=1/(1+np.exp(-z)); F=s*(1-s)
    z0=c2+g2*q0; s0=1/(1+np.exp(-z0)); F0=s0*(1-s0)
    return F/F0
popt,_=curve_fit(mod,x,y,p0=[c,gamma],bounds=([-20,-20],[20,20]),maxfev=100000)
free=mod(x,*popt)
lin=np.polyval(np.polyfit(x,y,1),x)
quad=np.polyval(np.polyfit(x,y,2),x)
secondary={
    'free_susceptibility': {'c':float(popt[0]),'gamma':float(popt[1]),'R2':r2(y,free),'RMSE':rmse(y,free),'peak_continuous':float(-popt[0]/popt[1]) if popt[1]!=0 else None},
    'linear': {'R2':r2(y,lin),'RMSE':rmse(y,lin)},
    'quadratic': {'R2':r2(y,quad),'RMSE':rmse(y,quad)},
}

res={
  'plan_sha256': (OUT/'PLAN_SHA256.txt').read_text().split()[0],
  'n_states': int(df[['block_id','ratio_id','mode']].drop_duplicates().shape[0]),
  'n_assays': int(len(df)),
  'primary_training_strengths': sorted(primary),
  'probe_grid': qgrid.tolist(),
  'fixed_prediction': {'c':c,'gamma':gamma,'q0':q0,'continuous_peak':float(-c/gamma),'grid_peak':float(qgrid[np.argmax(pred_ratio(qgrid))])},
  'primary_pooled': statsdf.iloc[0].to_dict(),
  'empirical_mean_curve_peak_q': float(peak_row.q_probe),
  'empirical_mean_curve_peak_ratio': float(peak_row.retrieval_ratio_mean),
  'mean_between_training_sd': float(mean_curve.retrieval_ratio_sd_across_training.mean()),
  'max_between_training_sd': float(mean_curve.retrieval_ratio_sd_across_training.max()),
  'secondary_refit': secondary,
}
(OUT/'T1_RESULT_SUMMARY.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print(json.dumps(res,indent=2,sort_keys=True))
