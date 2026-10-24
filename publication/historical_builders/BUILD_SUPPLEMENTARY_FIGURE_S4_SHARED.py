from pathlib import Path
import shutil, json, hashlib, csv
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse, FancyArrowPatch

ROOT = Path('/mnt/data')
SRC = ROOT/'_fig3inspect'/'SCO_FIGURE_3_RESULT_FREEZE_v1.2.1'/'sources'
OUT = ROOT/'SCO_FIGURE_3_S4_JRSI_RESTRUCTURE_DRAFT_v1.0.0'
if OUT.exists():
    shutil.rmtree(OUT)
(OUT/'sources').mkdir(parents=True)
(OUT/'render_qc').mkdir(parents=True)

fid = pd.read_csv(SRC/'MODEL_B_FIDELITY_SUMMARY.csv')
t3 = pd.read_csv(SRC/'T3_PEAK_RESULTS.csv')
t4 = pd.read_csv(SRC/'T4_DISTANCE_SUMMARY.csv')
t5 = pd.read_csv(SRC/'T5_DIRECTION_SUMMARY.csv')
p5 = pd.read_csv(SRC/'T5_PROBE_LEVEL_RESULTS.csv')
s3 = json.load(open(SRC/'T3_RESULT_SUMMARY.json'))
s4 = json.load(open(SRC/'T4_RESULT_SUMMARY.json'))
s5 = json.load(open(SRC/'T5_RESULT_SUMMARY.json'))

# Reader-facing main-text display domain: imperfect heredity only.
f = fid[fid.p_inherit < 1].copy()

BLUE='#1f77b4'; ORANGE='#ff7f0e'; GREEN='#2ca02c'; GRAY='#9a9a9a'; DARK='#303030'; PURPLE='#9467bd'; RED='#d62728'
plt.rcParams.update({
    'font.family':'DejaVu Sans',
    'font.size':10.5,
    'axes.labelsize':11.5,
    'axes.titlesize':12.5,
    'axes.titleweight':'bold',
    'xtick.labelsize':9.8,
    'ytick.labelsize':9.8,
    'legend.fontsize':9.0,
    'axes.linewidth':1.0,
    'pdf.fonttype':42,
    'ps.fonttype':42,
    'svg.fonttype':'none',
    'figure.facecolor':'white',
    'savefig.facecolor':'white'
})

def style(ax, zero=False):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out', length=4.5, width=1)
    if zero:
        ax.axhline(0, color=GRAY, ls='--', lw=0.9, zorder=0)

def ptitle(ax, label, text):
    ax.text(-0.13, 1.055, f'({label})', transform=ax.transAxes,
            fontsize=15.5, fontweight='bold', va='bottom', clip_on=False)
    ax.text(0, 1.055, text, transform=ax.transAxes,
            fontsize=12.5, fontweight='bold', va='bottom', clip_on=False)

# ---------------- Figure 3: four-panel JRSI main figure ----------------
fig = plt.figure(figsize=(14.5, 10.0))
gs = fig.add_gridspec(2, 2, left=.075, right=.975, top=.945, bottom=.075,
                      wspace=.28, hspace=.40)
A = fig.add_subplot(gs[0,0])
B = fig.add_subplot(gs[0,1])
C = fig.add_subplot(gs[1,0])
D = fig.add_subplot(gs[1,1])

# 3a - scientifically unchanged from frozen v1.2.1 panel A.
style(A, zero=True)
ptitle(A, 'a', 'Reliable heredity amplifies inherited causal organization')
x = f.p_inherit.to_numpy(); y = f.DeltaC_down_mean.to_numpy()
lo = f.DeltaC_down_ci95_lo.to_numpy(); hi = f.DeltaC_down_ci95_hi.to_numpy()
A.fill_between(x, lo, hi, color=BLUE, alpha=.12, lw=0)
A.plot(x, y, 'o-', color=BLUE, ms=4.4, lw=1.8)
A.set_xlabel(r'transmission fidelity $p$')
A.set_ylabel(r'$\Delta C_{\rm down}$ (bits $\times 10^{-3}$)')
A.set_xlim(-.03, .995)
A.set_xticks([0,.2,.4,.6,.8,.975])
A.set_xticklabels(['0.0','0.2','0.4','0.6','0.8','0.975'])
A.yaxis.set_major_formatter(lambda v,pos: f'{v*1e3:g}')
A.set_ylim(-0.00012, max(hi)*1.055)
A.text(.06, .105,
       'prospective 18-fidelity campaign; 30 root blocks\nall six prespecified contrasts passed',
       transform=A.transAxes, fontsize=9.0)
ia = A.inset_axes([.14,.53,.44,.39])
rx = f.DeltaR_mean.to_numpy()
ia.plot(x, rx, 'o-', color=BLUE, ms=3.0, lw=1.25)
ia.axhline(0, color=GRAY, ls='--', lw=.8)
ia.set_title(r'history specificity $\Delta R$', fontsize=9.4, pad=3)
ia.set_xlabel(r'$p$', fontsize=8.3, labelpad=0)
ia.set_ylabel('fitness', fontsize=8.3, labelpad=1)
ia.tick_params(labelsize=7.6, length=3)
ia.spines['top'].set_visible(False); ia.spines['right'].set_visible(False)
ia.set_xlim(-.03,.995)
ia.set_xticks([0,.2,.4,.6,.8,.975])
ia.set_xticklabels(['0','0.2','0.4','0.6','0.8','.975'])

# 3b - old frozen panel C.
style(B)
ptitle(B, 'b', 'Scalar environmental distance fails prospectively')
d = t4.distance.to_numpy(); o = t4.R_obs_mean.to_numpy()
ol = t4.bootstrap95_lo.to_numpy(); oh = t4.bootstrap95_hi.to_numpy()
B.plot(d, t4.R_pred, '--', color=BLUE, lw=1.7, label='prespecified scalar law')
B.plot(d, t4.R_local, ':', color=ORANGE, lw=1.8, label=r'local $d/64$ law')
B.errorbar(d, o, yerr=np.vstack([o-ol, oh-o]), fmt='o-', color=GREEN,
           ms=4.5, capsize=2.5, lw=1.5, label='observed')
B.axhline(1, color='0.85', lw=1.0, zorder=0)
B.set_xlabel(r'squared scaffold distance $d$')
B.set_ylabel('normalized historical response')
B.legend(frameon=False, loc='upper left')
B.text(.97,.07,
       f"scalar law $R^2$ = {s4['zero_parameter_finite_distance']['class_mean_R2']:.3f}\n"
       f"local law $R^2$ = {s4['local_distance_law']['class_mean_R2']:.3f}",
       transform=B.transAxes, ha='right', fontsize=9.0)

# 3c - old frozen panel D; schematic only, source-faithful theory revision.
C.set_axis_off()
ptitle(C, 'c', 'Directional response replaces a distance-only law')
C.set_xlim(0,1); C.set_ylim(0,1)
C.set_aspect('equal', adjustable='box')
lc=(0.22,0.57)
for r in [0.07,0.125,0.18,0.235]:
    C.add_patch(Circle(lc, r, fill=False, ec='.50', lw=1.1, clip_on=False))
C.plot([lc[0],lc[0]+0.18],[lc[1],lc[1]+0.10], color=BLUE, lw=2.0,
       solid_capstyle='round', clip_on=False)
C.text(0.22,0.885,'distance only',ha='center',fontsize=10.5)
C.text(0.22,0.17,r'$\mathcal{R}=f(\|\delta\|)$',ha='center',fontsize=12)
C.add_patch(FancyArrowPatch((0.43,0.76),(0.58,0.76),arrowstyle='-|>',
                            mutation_scale=14,lw=1.4,color=DARK,clip_on=False))
C.text(0.505,0.80,'revise',ha='center',fontsize=8.5)
rc=(0.79,0.56)
for w,h in [(0.34,0.12),(0.27,0.095),(0.20,0.07),(0.13,0.045)]:
    C.add_patch(Ellipse(rc,w,h,angle=18,fill=False,ec='.50',lw=1.0,clip_on=False))
for col,deg,L in [(RED,145,0.18),(GREEN,60,0.16),(ORANGE,15,0.19),(PURPLE,210,0.17)]:
    th=np.deg2rad(deg)
    C.plot([rc[0],rc[0]+L*np.cos(th)],[rc[1],rc[1]+L*np.sin(th)],
           color=col,lw=1.6,solid_capstyle='round',clip_on=False)
C.text(0.79,0.885,'direction matters',ha='center',fontsize=10.5)
C.text(0.79,0.17,
       r'$\mathcal{R}(B_H+\delta)\approx R_0+g_T^T\delta+\frac{1}{2}\delta^T H_T\delta$',
       ha='center', fontsize=10.8)
C.text(0.02,0.035,
       'Prospective failure of the scalar-distance law motivated the revised\nlocal geometry, which permits anisotropic response.',
       fontsize=8.9, va='bottom')

# 3d - old frozen panel E.
style(D)
ptitle(D, 'd', 'Equal-distance directional profile is predicted')
phi = t5.phi_deg.to_numpy(); pred = t5.pred_obs_affine.to_numpy(); obs = t5.DeltaH_mean.to_numpy()
D.plot(phi, pred, 'o--', color=BLUE, ms=4.0, lw=1.6, label='prespecified prediction')
D.plot(phi, obs, 'o-', color=ORANGE, ms=4.0, lw=1.5, label='observed')
D.set_xlabel(r'probe direction (degrees; all at $d=64$)')
D.set_ylabel(r'historical response $\Delta H$')
D.set_xlim(0,360); D.set_xticks([0,90,180,270,360])
D.legend(frameon=False, loc='lower right')
D.text(.15,.93,
       f"profile $r$ = {s5['profile_r']:.3f}\npermutation $p$ = {s5['profile_exact_permutation_p']:.2e}",
       transform=D.transAxes, va='top', fontsize=9.1)

fig3_pdf = OUT/'FIGURE_3_JRSI_RESTRUCTURE_DRAFT_v1.0.0.pdf'
fig3_png = OUT/'FIGURE_3_JRSI_RESTRUCTURE_DRAFT_v1.0.0.png'
fig3_svg = OUT/'FIGURE_3_JRSI_RESTRUCTURE_DRAFT_v1.0.0.svg'
fig.savefig(fig3_pdf, facecolor='white')
fig.savefig(fig3_png, dpi=350, facecolor='white')
fig.savefig(fig3_svg, facecolor='white')
plt.close(fig)

# ---------------- Supplementary Figure S4: relocated old B and F ----------------
fig = plt.figure(figsize=(12.8, 4.8))
gs = fig.add_gridspec(1,2,left=.075,right=.975,top=.88,bottom=.18,wspace=.30)
A = fig.add_subplot(gs[0,0]); B = fig.add_subplot(gs[0,1])

style(A)
ptitle(A, 'a', 'Training history predicts maximal expression')
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
       transform=A.transAxes,ha='right',fontsize=9.0)

style(B)
ptitle(B, 'b', 'Prespecified directional contrast succeeds')
a=p5[p5.probe_id=='P09'].sort_values('block_index').DeltaH.to_numpy()
b=p5[p5.probe_id=='P13'].sort_values('block_index').DeltaH.to_numpy()
mn=min(a.min(),b.min())-.5; mx=max(a.max(),b.max())+.5
B.plot([mn,mx],[mn,mx],':',color=DARK,lw=1.2)
B.scatter(a,b,s=34,facecolor='white',edgecolor=BLUE,lw=1.3)
B.set_xlim(mn,mx); B.set_ylim(mn,mx)
B.set_xlabel('P09 response (predicted weak direction)')
B.set_ylabel('P13 response (predicted strong direction)')
B.text(.55,.10,
       f"P13 > P09: {s5['top_gt_bottom_blocks']}/30 blocks\n"
       f"sign $p$ = {s5['extremal_sign_p']:.2e}\n"
       f"anisotropy $p$ = {s5['anisotropy_permutation_p']:.2e}",
       transform=B.transAxes,fontsize=9.0)

s4_pdf = OUT/'SUPPLEMENTARY_FIGURE_S4_JRSI_DRAFT_v1.0.0.pdf'
s4_png = OUT/'SUPPLEMENTARY_FIGURE_S4_JRSI_DRAFT_v1.0.0.png'
s4_svg = OUT/'SUPPLEMENTARY_FIGURE_S4_JRSI_DRAFT_v1.0.0.svg'
fig.savefig(s4_pdf,facecolor='white')
fig.savefig(s4_png,dpi=350,facecolor='white')
fig.savefig(s4_svg,facecolor='white')
plt.close(fig)

# Captions
(OUT/'FIGURE_3_CAPTION_DRAFT_v1.0.0.tex').write_text(r'''\caption{\textbf{Reliable heredity, prospective falsification and directional revision of environmental response.}
\textbf{(a)} Reliable heredity amplifies selected-specific causal organization in Model B. The main-text curve shows the imperfect-transmission domain, $p<1$, ending at $p=0.975$; the inset shows the corresponding history-specific response. The underlying prospectively frozen 18-fidelity inferential campaign is unchanged. At $p=0.975$, $\Delta C_{\rm down}=0.0036617$ bits and the history-specific response was $\Delta R=13.7549$ score units. The panel preserves the scientific content of the previously frozen Figure~3a while adopting the four-panel JRSI layout.
\textbf{(b)} The prospectively specified scalar environmental-distance law failed. Observed normalized historical responses departed strongly from both the frozen finite-distance prediction ($R^2=-0.576$, RMSE $=0.470$) and the local $d/64$ law ($R^2=-1.311$, RMSE $=0.570$), motivating revision of the response geometry.
\textbf{(c)} The revised local theory allows the response to depend on direction through gradient and curvature terms, $\mathcal{R}(B_H+\delta)\approx R_0+g_T^T\delta+\frac{1}{2}\delta^T H_T\delta$, rather than only on scalar distance from the historical condition.
\textbf{(d)} A new prospective equal-distance test evaluated eight probe directions at identical squared scaffold distance $d=64$. The predicted directional profile closely matched the observed profile ($r=0.9879$, exact permutation $p=2.48\times10^{-4}$). The directional theory was calibrated from the preceding response geometry and is therefore treated as a prospective out-of-sample test of the revised calibrated model rather than a parameter-free prediction.}''')

(OUT/'SUPPLEMENTARY_FIGURE_S4_CAPTION_DRAFT_v1.0.0.tex').write_text(r'''\caption{\textbf{Acquisition--expression separation and prespecified directional contrast in Model B.}
\textbf{(a)} Five historical scaffold strengths were used to evolve selected--neutral inherited differences, which were then evaluated across a common probe grid. All five observed block-mean expression peaks fell within one $0.125$ probe-grid interval of the prespecified prediction. Across the full 125-point response surface, the no-refit prediction gave $R^2=0.9663$ and RMSE $=4.88\times10^{-4}$ bits. The acquisition condition therefore need not coincide with the condition of maximal later expression.
\textbf{(b)} In the prospective equal-distance directional test, the prespecified strong direction P13 exceeded the prespecified weak direction P09 in 30/30 independent root-seed blocks (one-sided exact sign $p=9.31\times10^{-10}$). The complete eight-direction response profile was also anisotropic under direction-label permutation ($p=2.00\times10^{-5}$).}''')

# Source maps
with open(OUT/'FIGURE_3_SOURCE_MAP_DRAFT_v1.0.0.csv','w',newline='') as fcsv:
    w=csv.writer(fcsv); w.writerow(['panel','reader_facing_role','primary_source','provenance'])
    w.writerow(['a','Heredity dependence and history specificity','MODEL_B_FIDELITY_SUMMARY.csv','prospective 18-fidelity campaign; main display restricted to p<1'])
    w.writerow(['b','Prospective failure of scalar distance law','T4_DISTANCE_SUMMARY.csv; T4_RESULT_SUMMARY.json','prospective falsification'])
    w.writerow(['c','Directional response theory revision','general-theory local response equation; schematic','theory revision after prospective scalar-law failure'])
    w.writerow(['d','Prospective equal-distance directional profile','T5_DIRECTION_SUMMARY.csv; T5_RESULT_SUMMARY.json','prospective out-of-sample test of revised calibrated geometry'])
with open(OUT/'SUPPLEMENTARY_FIGURE_S4_SOURCE_MAP_DRAFT_v1.0.0.csv','w',newline='') as fcsv:
    w=csv.writer(fcsv); w.writerow(['panel','reader_facing_role','primary_source','provenance'])
    w.writerow(['a','Training history predicts maximal expression','T3_PEAK_RESULTS.csv; T3_RESULT_SUMMARY.json','prospective acquisition-expression prediction'])
    w.writerow(['b','Prespecified strong-versus-weak directional contrast','T5_PROBE_LEVEL_RESULTS.csv; T5_RESULT_SUMMARY.json','prospective directional contrast after theory revision'])

# Copy only required frozen source files.
needed = [
    'MODEL_B_FIDELITY_SUMMARY.csv','MODEL_B_FIDELITY_CONFIRMATORY_RESULTS.md','PERFECT_TRANSMISSION_PRESENTATION_POLICY.md',
    'T3_PEAK_RESULTS.csv','T3_RESULT_SUMMARY.json',
    'T4_DISTANCE_SUMMARY.csv','T4_RESULT_SUMMARY.json',
    'T5_DIRECTION_SUMMARY.csv','T5_PROBE_LEVEL_RESULTS.csv','T5_RESULT_SUMMARY.json'
]
for name in needed:
    shutil.copy2(SRC/name, OUT/'sources'/name)

# Build/source-faithfulness note.
(OUT/'README.md').write_text('''# SCO Figure 3 + Supplementary Figure S4 JRSI restructure draft v1.0.0\n\nProgrammatic, source-faithful restructure from the frozen Figure 3 v1.2.1 evidence.\n\nMain Figure 3 panel mapping:\n- 3a = frozen old panel A, scientifically unchanged (layout resized only)\n- 3b = frozen old panel C\n- 3c = frozen old panel D\n- 3d = frozen old panel E\n\nSupplementary Figure S4 panel mapping:\n- S4a = frozen old panel B\n- S4b = frozen old panel F\n\nNo simulation, re-estimation, or inferential change was performed.\n''')
(OUT/'RESTRUCTURE_NOTE_v1.0.0.md').write_text('''This is a presentation-only JRSI restructure of frozen Figure 3 v1.2.1. Panel A is not replaced scientifically. The acquisition-expression panel and the prespecified strong-versus-weak contrast are relocated to Supplementary Figure S4. The old Supplementary Fig. S21 / Table S8 reference is intentionally removed from the new caption pending final supplementary numbering; no underlying perfect-transmission or p<1 sensitivity result is altered.\n''')

# Self-contained build script.
shutil.copy2(Path(__file__), OUT/'build_jrsi_fig3_s4_restructure_v1_0_0.py')

# Manifest after all content generated.
rows=[]
for p in sorted(OUT.rglob('*')):
    if p.is_file() and p.name != 'SHA256_MANIFEST_DRAFT_v1.0.0.csv':
        rows.append([str(p.relative_to(OUT)), hashlib.sha256(p.read_bytes()).hexdigest()])
with open(OUT/'SHA256_MANIFEST_DRAFT_v1.0.0.csv','w',newline='') as fcsv:
    w=csv.writer(fcsv); w.writerow(['file','sha256']); w.writerows(rows)

print(OUT)
