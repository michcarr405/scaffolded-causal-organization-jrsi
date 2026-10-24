#!/usr/bin/env python3
"""Rebuild Figure 5 v1.1.1 from frozen source-faithful Figure 5 tables.

Reader-facing synchronization changes only:
  * panel (a): r -> r_L for the lattice directional probe radius;
  * panel (c): manuscript-consistent norm-squared notation for catalytic
    equal-distance probes and removal of the internal lattice C5 alias.
No simulation, resampling, inference, or source values are changed.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter

ROOT = Path(__file__).resolve().parent
BLUE = '#0072B2'; ORANGE = '#E69F00'; GRAY = '#888888'; BLACK = '#222222'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_ax(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out', length=4, width=.85)


def label(ax, letter, x=-.14, y=1.07):
    ax.text(x, y, f'({letter})', transform=ax.transAxes,
            fontsize=14, fontweight='bold', va='top')


def save(fig, stem: Path):
    for ext in ('pdf', 'svg', 'png'):
        opts = {'dpi': 400} if ext == 'png' else {}
        fig.savefig(Path(str(stem) + '.' + ext), bbox_inches='tight', **opts)
    plt.close(fig)


def load_sources():
    direction = pd.read_csv(ROOT / 'FIGURE_5A_DIRECTIONAL_PROFILE_T50.csv')
    dense = pd.read_csv(ROOT / 'sources/DENSE_TIME_SURFACE_SUMMARY.csv')
    anchors = pd.read_csv(ROOT / 'sources/CROSS_REALIZATION_EVIDENCE_ANCHORS_v1.0.0.csv', keep_default_na=False)
    assert len(direction) == 12
    assert (direction['count'] == 30).all()
    assert np.allclose(direction['phi_degrees'].to_numpy(), np.arange(0, 360, 30), atol=1e-9)
    assert set(dense.columns) >= {'p','t','DeltaV_rel'}
    assert len(anchors) == 12
    return direction, dense, anchors


def main():
    direction, dense, anchors = load_sources()
    heat = dense[dense.p < 1].copy()
    pvals = np.sort(heat.p.unique())
    tvals = np.sort(heat.t.unique())
    pivot = heat.pivot(index='p', columns='t', values='DeltaV_rel').loc[pvals, tvals]
    a50 = heat[heat.t.between(41, 50)].groupby('p').DeltaV_rel.mean().reindex(pvals)

    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 9.5,
        'axes.titlesize': 12.0, 'axes.titleweight': 'bold',
        'axes.labelsize': 10.5, 'xtick.labelsize': 9.0, 'ytick.labelsize': 9.0,
        'legend.fontsize': 8.6, 'axes.linewidth': .9,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'figure.facecolor': 'white', 'savefig.facecolor': 'white',
        'svg.hashsalt': 'SCO_FIG5_v1.1.1'
    })

    fig = plt.figure(figsize=(12.8, 8.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, .92], width_ratios=[.82, 1.18],
                         left=.075, right=.975, top=.94, bottom=.08, wspace=.31, hspace=.38)

    # (a) directional mapping
    ax = fig.add_subplot(gs[0,0]); label(ax, 'a')
    ax.set_title('Post-confirmatory directional response\nat equal displacement', loc='left', pad=8)
    ax.errorbar(direction.phi_degrees, direction['mean'], yerr=direction['sem'], fmt='o-',
                color=ORANGE, mfc=ORANGE, mec=ORANGE, ms=4.8,
                capsize=2.6, lw=1.6, elinewidth=.95)
    ax.axhline(0, color=GRAY, ls='--', lw=.8, zorder=0)
    ax.set_xlim(-8,338); ax.set_ylim(-.005,.28)
    ax.set_xticks([0,90,180,270,330]); ax.set_yticks([0,.05,.10,.15,.20,.25])
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.set_xlabel('probe direction (degrees)')
    ax.set_ylabel('relational causal value\n' + r'$\Delta V_{\rm rel}$ (fitness units)')
    ax.text(.03,.06,'Equal radius ' + r'$r_L=0.6$' + '\n' + r'$p=0.95$; generation 50',
            transform=ax.transAxes, fontsize=8.8, va='bottom', color='#555555')
    clean_ax(ax)

    # (b) fidelity-time surface and A50 marginal
    sub = gs[0,1].subgridspec(1,3,width_ratios=[5.0,1.35,.32],wspace=.20)
    ax = fig.add_subplot(sub[0,0]); marg = fig.add_subplot(sub[0,1], sharey=ax); cax=fig.add_subplot(sub[0,2])
    label(ax,'b',x=-.16,y=1.07)
    ax.set_title('Post-confirmatory heredity mapping\nacross fidelity and time', loc='left', pad=8)
    im=ax.imshow(pivot.values,origin='lower',aspect='auto',cmap='viridis',interpolation='nearest',
                 extent=[0,50,pvals.min(),pvals.max()])
    ax.set_xlabel('generation'); ax.set_ylabel('transmission fidelity $p$')
    ax.set_xticks([0,10,20,30,40,50]); ax.set_yticks([0,.2,.4,.6,.8,.975])
    ax.set_yticklabels(['0','0.2','0.4','0.6','0.8','0.975'])
    marg.plot(a50.values,a50.index.values,'o-',color=BLACK,ms=3.3,lw=1.3)
    marg.set_xlabel('$A_{50}(p)$',labelpad=3); marg.set_xlim(0,.18)
    marg.set_xticks([0,.09,.17]); marg.set_xticklabels(['0','0.09','0.17'])
    marg.tick_params(axis='y',left=False,labelleft=False); clean_ax(marg)
    cb=fig.colorbar(im,cax=cax,format='%.2f'); cb.ax.set_title(r'$\Delta V_{\rm rel}$',fontsize=9,pad=5)
    cb.set_ticks([0,.05,.10,.15]); cb.ax.yaxis.set_ticks_position('left'); cb.ax.tick_params(labelsize=8,pad=2)

    # (c) cross-realization evidence anchors
    ax=fig.add_subplot(gs[1,:]); ax.set_axis_off(); label(ax,'c',x=-.055,y=1.06)
    ax.set_title('Cross-realization prospective evidence anchors',loc='left',pad=8)
    rows=['History specificity','Heredity dependence','Acquisition-expression','Equal-distance anisotropy']
    cols=['Model B','Catalytic','Lattice']
    header,face_label,cell='#DEDEDE','#EFEFEF','#E4F0E5'
    x0,y0,wlabel,wcol,rh=.08,.06,.34,.175,.185
    ax.add_patch(Rectangle((x0,y0+4*rh),wlabel,rh,facecolor=header,edgecolor='white',transform=ax.transAxes))
    for j,col in enumerate(cols):
        x=x0+wlabel+j*wcol
        ax.add_patch(Rectangle((x,y0+4*rh),wcol,rh,facecolor=header,edgecolor='white',transform=ax.transAxes))
        ax.text(x+wcol/2,y0+4*rh+rh/2,col,ha='center',va='center',fontweight='bold',fontsize=10,transform=ax.transAxes)
    for i,sig in enumerate(rows):
        y=y0+(3-i)*rh
        ax.add_patch(Rectangle((x0,y),wlabel,rh,facecolor=face_label,edgecolor='white',transform=ax.transAxes))
        ax.text(x0+.012,y+rh/2,sig,ha='left',va='center',fontweight='bold',fontsize=9.7,transform=ax.transAxes)
        for j,col in enumerate(cols):
            rec=anchors[(anchors.signature==sig)&(anchors.realization==col)].iloc[0]
            x=x0+wlabel+j*wcol
            ax.add_patch(Rectangle((x,y),wcol,rh,facecolor=cell,edgecolor='white',transform=ax.transAxes))
            support=rec.support
            if sig=='Equal-distance anisotropy' and col=='Catalytic':
                support=r'equal $\|B_P-B_H\|^2=1$'
            elif sig=='Equal-distance anisotropy' and col=='Lattice':
                support='30/30'
            txt=f'{rec.anchor}\n{rec.metric}' + (f'\n{support}' if support else '')
            ax.text(x+wcol/2,y+rh/2,txt,ha='center',va='center',fontsize=8.2,linespacing=1.15,transform=ax.transAxes)
    ax.text(x0+wlabel+1.5*wcol,y0-.005,'Representative frozen anchors; metrics and units differ among realizations.',
            ha='center',va='top',fontsize=8.5,color='#555555',transform=ax.transAxes)

    stem=ROOT/'FIGURE_5_FINAL_v1.1.1'
    save(fig,stem)

    qc={
        'status':'PASS',
        'source_direction_sha256':sha(ROOT/'FIGURE_5A_DIRECTIONAL_PROFILE_T50.csv'),
        'source_dense_sha256':sha(ROOT/'sources/DENSE_TIME_SURFACE_SUMMARY.csv'),
        'source_anchor_sha256':sha(ROOT/'sources/CROSS_REALIZATION_EVIDENCE_ANCHORS_v1.0.0.csv'),
        'direction_count':int(len(direction)),
        'root_blocks_per_direction':30,
        'display_only_changes':['r -> r_L in panel a','catalytic norm-squared notation in panel c','remove internal C5 alias in panel c'],
        'new_simulation_runs':0,
        'new_inference':0
    }
    (ROOT/'NUMERICAL_QC_v1.1.1.json').write_text(json.dumps(qc,indent=2)+'\n')
    print('PASS: Figure 5 v1.1.1 rebuilt from frozen source tables.')

if __name__=='__main__':
    main()
