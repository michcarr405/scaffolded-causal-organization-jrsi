from pathlib import Path
import numpy as np, pandas as pd, json, math, hashlib, sys
SRCROOT=Path('/mnt/data/prospective_test_work/identity/MODEL_B_DCC_CONFIRMATORY_RUN_v1.0.0')
sys.path.insert(0,str(SRCROOT/'scripts'))
from dcc_pipeline import make_params, make_kernel, BETA, THETA
OUT=Path('/mnt/data/reduced_theory_prospective_T3T4/T4')
H=(2,0,3,1)
TARGETS=[16.,32.,48.,64.,80.,112.,144.]
PHIS=[0.,0.5*math.pi,math.pi,1.5*math.pi]
RSEG=BETA*math.sqrt(3.0)/2.0
RTOT2=4*RSEG**2
rows=[]
# historical centered field
hist=np.zeros((4,4),float)
for s,f in enumerate(H):
    hist[s,:]=-BETA/4.0; hist[s,f]=3*BETA/4.0
row={'scaffold_id':'D000_HIST','distance_target':0.0,'phi_index':-1,'phi':np.nan,'theta':0.0}
for s in range(4):
    for z in range(4): row[f'b{s}_{z}']=hist[s,z]
rows.append(row)
for d in TARGETS:
    theta=math.acos(1.0-d/(2.0*RTOT2))
    for pi,phi in enumerate(PHIS):
        mat=np.zeros((4,4),float)
        for s,f in enumerate(H):
            others=[x for x in range(4) if x!=f]
            a,b,c=others
            v=hist[s].copy()
            w1=np.zeros(4); w1[a]=1/math.sqrt(2); w1[b]=-1/math.sqrt(2)
            w2=np.zeros(4); w2[a]=1/math.sqrt(6); w2[b]=1/math.sqrt(6); w2[c]=-2/math.sqrt(6)
            u=RSEG*(math.cos(phi)*w1+math.sin(phi)*w2)
            mat[s]=math.cos(theta)*v+math.sin(theta)*u
        row={'scaffold_id':f'D{int(d):03d}_P{pi}','distance_target':d,'phi_index':pi,'phi':phi,'theta':theta}
        for s in range(4):
            for z in range(4): row[f'b{s}_{z}']=mat[s,z]
        rows.append(row)
df=pd.DataFrame(rows)
# validate geometry
bcols=[f'b{s}_{z}' for s in range(4) for z in range(4)]
B=df[bcols].to_numpy(float).reshape(-1,4,4)
dists=np.sum((B-hist[None,:,:])**2,axis=(1,2))
seg_means=np.max(np.abs(B.mean(axis=2)))
seg_norm2=np.sum(B**2,axis=2)
max_norm_err=np.max(np.abs(seg_norm2-RSEG**2))
max_dist_err=np.max(np.abs(dists-df.distance_target.to_numpy(float)))
# historical kernel equivalence to original categorical implementation
params=make_params(H); aff=params['motif_affinity_matrix']
orig=make_kernel(aff,H,BETA,THETA)
logits=aff[None,:,:]+hist[:,None,:]
x=logits/THETA; x=x-x.max(axis=2,keepdims=True); ex=np.exp(x); cent=ex/ex.sum(axis=2,keepdims=True)
kerr=float(np.max(np.abs(orig-cent)))
assert seg_means < 1e-12 and max_norm_err < 1e-10 and max_dist_err < 1e-9 and kerr < 1e-12
# exact counts / target law
LAM=326.128666514
def R(d): return (1-math.exp(-d/LAM))/(1-math.exp(-64.0/LAM))
pred=pd.DataFrame({'distance':TARGETS,'R_pred':[R(d) for d in TARGETS],'local_d_over_64':[d/64 for d in TARGETS]})
df.to_csv(OUT/'T4_PROBE_SCAFFOLDS_FROZEN.csv',index=False)
pred.to_csv(OUT/'T4_FROZEN_PREDICTIONS.csv',index=False)
val={'historical_mapping':H,'beta':BETA,'theta':THETA,'target_distances':TARGETS,'orientations_per_distance':4,'n_probe_scaffolds_including_history':len(df),'per_segment_norm2':RSEG**2,'total_norm2':RTOT2,'max_segment_mean_abs':float(seg_means),'max_segment_norm2_error':float(max_norm_err),'max_distance_error':float(max_dist_err),'historical_kernel_max_abs_error':kerr,'status':'PASS'}
(OUT/'T4_DESIGN_VALIDATION.json').write_text(json.dumps(val,indent=2,sort_keys=True)+'\n')
print(json.dumps(val,indent=2,sort_keys=True))
