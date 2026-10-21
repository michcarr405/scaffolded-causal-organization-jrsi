from pathlib import Path
import json, hashlib, zipfile
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
ROOT=Path('/mnt/data/reduced_theory_prospective_T3T4')
# T3 figure
s=pd.read_csv(ROOT/'T3'/'T3_retrieval_summary.csv')
sp=s[s.primary_grid==True]
fig,ax=plt.subplots(figsize=(8,5.5))
for qt,g in sp.groupby('q_train'):
    g=g.sort_values('q_probe')
    ax.plot(g.q_probe,g.DeltaC_mean,marker='o',markersize=3,label=f'train {qt:g}')
ax.set_xlabel('Probe scaffold strength beta/theta')
ax.set_ylabel('Selected - neutral Delta C_down (bits)')
ax.set_title('T3: frozen-population retrieval curves')
ax.legend(frameon=False,ncol=2)
fig.tight_layout(); fig.savefig(ROOT/'T3'/'T3_retrieval_curves.png',dpi=220); plt.close(fig)
# T3 observed vs predicted peaks
p=pd.read_csv(ROOT/'T3'/'T3_peak_results.csv')
fig,ax=plt.subplots(figsize=(6.5,5))
ax.plot(p.q_train,p.q_peak_pred,marker='o',label='Frozen v0.2 prediction')
ax.plot(p.q_train,p.q_peak_obs,marker='s',label='Observed grid peak')
ax.set_xlabel('Training scaffold strength beta/theta')
ax.set_ylabel('Probe strength at maximum expression')
ax.set_title('T3: prospective retrieval-peak law')
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(ROOT/'T3'/'T3_peak_prediction.png',dpi=220); plt.close(fig)
# T4 figure
u=pd.read_csv(ROOT/'T4'/'T4_distance_summary.csv')
fig,ax=plt.subplots(figsize=(7,5.2))
ax.errorbar(u.distance,u.R_obs_mean,yerr=[u.R_obs_mean-u.bootstrap95_lo,u.bootstrap95_hi-u.R_obs_mean],marker='o',capsize=3,label='Observed')
ax.plot(u.distance,u.R_pred,marker='s',label='Frozen v0.2 finite-distance law')
ax.plot(u.distance,u.R_local,linestyle='--',label='Local d/64 law')
ax.set_xlabel('Squared scaffold distance')
ax.set_ylabel('Historical-match response normalized at d=64')
ax.set_title('T4: prospective scaffold-distance test')
ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(ROOT/'T4'/'T4_distance_test.png',dpi=220); plt.close(fig)
# Result freeze
r3=json.loads((ROOT/'T3'/'T3_RESULT_SUMMARY.json').read_text())
r4=json.loads((ROOT/'T4'/'T4_RESULT_SUMMARY.json').read_text())
raw4=pd.read_csv(ROOT/'T4'/'T4_block_distance_results.csv')
means4=raw4.groupby('distance').DeltaH.mean()
text=f'''# Reduced Theory Prospective Tests T3-T4 - Result Freeze v1.0.0

Status: FROZEN RESULTS.

## T3 - finite-amplitude retrieval-peak law

The T3 plan and execution specification were frozen and hashed before outcome generation. Five previously unused training strengths were evolved with 30 entirely new selected-neutral root-seed pairs per strength (150 pairs; 300 evolutionary runs). Generation-250 populations were frozen before assay.

Primary result: **PASS**. The observed block-mean retrieval peak fell within one 0.125 probe-grid interval of the frozen v0.2 prediction for **{r3['primary_peak_success_count']}/5** training strengths (required >=4/5).

Predicted versus observed peaks:
'''
for x in r3['peak_results']:
    text += f"- training {x['q_train']:.2f}: predicted {x['q_peak_pred']:.4f}, observed {x['q_peak_obs']:.3f}, error {x['signed_error']:+.4f}.\n"
text += f'''
Signed peak error showed no monotonic trend by the predeclared operational test (Spearman rho={r3['signed_error_spearman']['rho']:.3f}, two-sided p={r3['signed_error_spearman']['two_sided_p']:.3f}).

The full frozen finite-amplitude curve, with **no parameter refitting**, achieved pooled R2={r3['full_curve_no_refit']['R2']:.4f} and RMSE={r3['full_curve_no_refit']['RMSE']:.6g} bits across 125 primary grid points.

Interpretation: the post-T1 v0.2 prediction that the probe strength maximizing expression shifts systematically with the magnitude of organization acquired during evolution received strong prospective support.

## T4 - finite-distance historical-match law

The T4 design was frozen before evolutionary outcomes. Thirty entirely new selected-neutral root-seed pairs evolved under the canonical historical scaffold. Frozen endpoint populations were probed under 28 continuous equal-strength scaffold variants: four orientations at each total squared distance 16, 32, 48, 64, 80, 112, and 144. The construction preserved per-segment scaffold norm exactly and reproduced the historical categorical kernel to numerical precision.

Primary zero-parameter v0.2 result: **NOT SUPPORTED**. The frozen saturating scalar-distance law gave class-mean R2={r4['zero_parameter_finite_distance']['class_mean_R2']:.4f}, RMSE={r4['zero_parameter_finite_distance']['class_mean_RMSE']:.4f}; the local d/64 law was worse (R2={r4['local_distance_law']['class_mean_R2']:.4f}, RMSE={r4['local_distance_law']['class_mean_RMSE']:.4f}) but neither described the new continuous-scaffold data adequately.

Observed normalized mean response:
'''
for d,v in r4['mean_normalized_response'].items():
    text += f'- d={d}: {v:.4f}.\n'
text += '\nObserved raw DeltaH means were:\n'
for d,v in means4.items(): text += f'- d={d:g}: {v:.4f}.\n'
text += '''
The response rose from near zero at d=16, reached its maximum near d=80, and then declined at d=112 and d=144. Orientation-level effects were substantial at small and intermediate distances. Thus raw Euclidean scaffold distance is not a sufficient state variable for historical mismatch outside the restricted categorical-permutation family used in T2.

## Combined inference

T3 strengthens the acquisition-storage-retrieval part of Reduced Theory v0.2: training history quantitatively predicts the physical context in which frozen inherited organization is maximally expressed.

T4 falsifies the proposed one-dimensional finite-distance extension. The earlier T2 monotonic distance result is real within the categorical permutation family, but it does not generalize to arbitrary equal-strength directions in scaffold-logit space. The next theory should therefore be anisotropic/state-dependent rather than a scalar function of Euclidean scaffold distance. A natural local form is DeltaH approximately delta_b^T G(x*, chemistry) delta_b, where G is an effective metric induced by the chemical kernel and evolved organization.

No v0.2 parameters were refit for these prospective scores.
'''
(ROOT/'RESULT_FREEZE_T3_T4_v1.0.0.md').write_text(text)
# manifest
files=[p for p in ROOT.rglob('*') if p.is_file() and 'states' not in p.parts and p.name!='SHA256_MANIFEST_T3_T4.csv']
rows=[]
for pth in sorted(files):
    rows.append({'path':str(pth.relative_to(ROOT)),'sha256':hashlib.sha256(pth.read_bytes()).hexdigest(),'bytes':pth.stat().st_size})
pd.DataFrame(rows).to_csv(ROOT/'SHA256_MANIFEST_T3_T4.csv',index=False)
# zip excluding heavy states and logs optional include scripts/results/plans/figures
zip_path=Path('/mnt/data/REDUCED_THEORY_PROSPECTIVE_TESTS_T3_T4_v1.0.0.zip')
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for pth in sorted(ROOT.rglob('*')):
        if not pth.is_file() or 'states' in pth.parts: continue
        z.write(pth,arcname=str(Path('reduced_theory_prospective_T3T4')/pth.relative_to(ROOT)))
print(zip_path)
