#!/usr/bin/env python3
"""Rebuild the review-only Fig. 5/S6 revision from archived data.

No evolution, new random erasures, bootstrap inference, or hypothesis tests run.
Mapping uncertainties are sample SD / sqrt(30), computed across root blocks.
Prospective CIs are copied from the frozen, separately generated campaign.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.ticker import FormatStrFormatter

BLUE = '#0072B2'
ORANGE = '#E69F00'
GREEN = '#009E73'
GRAY = '#888888'
BLACK = '#222222'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def clean_ax(ax) -> None:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(direction='out', length=4, width=.85)


def label(ax, letter: str, x: float = -.14, y: float = 1.07) -> None:
    ax.text(x, y, f'({letter})', transform=ax.transAxes,
            fontsize=14, fontweight='bold', va='top')


def summarize(df: pd.DataFrame, key: str, value: str) -> pd.DataFrame:
    out = df.groupby(key, sort=True)[value].agg(['mean', 'std', 'count']).reset_index()
    out['sem'] = out['std'] / np.sqrt(out['count'])
    check(bool(out['count'].eq(30).all()), f'{key}: expected 30 blocks per coordinate')
    return out[[key, 'mean', 'sem', 'std', 'count']]


def save(fig, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    for ext in ('pdf', 'svg', 'png'):
        options = {'dpi': 400} if ext == 'png' else {}
        fig.savefig(Path(str(path) + '.' + ext), bbox_inches='tight', **options)
    plt.close(fig)


def load_and_validate(root: Path) -> dict:
    mp = root / 'sources/mapping'
    original = root / 'sources/figure5_reference'
    manifest = pd.read_csv(root / 'sources/INPUT_SOURCE_MANIFEST.csv')
    for row in manifest.itertuples():
        check(sha(root / row.bundle_path) == row.sha256, 'Source hash mismatch: ' + row.bundle_path)
    spec = json.loads((root / 'DISPLAY_SPECIFICATION.json').read_text())
    cfg = json.loads((mp / 'CONFIG_v1.0.0.json').read_text())
    check(spec['mapping_fidelity'] == cfg['base_p'] == .95, 'Mapping fidelity mismatch')
    check(spec['mapping_generation'] == 50, 'Unexpected generation selection')
    a = pd.read_csv(mp / 'anisotropy_by_time.csv')
    e = pd.read_csv(mp / 'expression_by_time.csv')
    ac = pd.read_csv(mp / 'anisotropy_contrast_by_time.csv')
    ec = pd.read_csv(mp / 'expression_separation_contrast_by_time.csv')
    dense = pd.read_csv(original / 'DENSE_TIME_SURFACE_SUMMARY.csv')
    dense_mapping = pd.read_csv(mp / 'dense_time_surface_summary.csv')
    check(len(a) == 30 * 8 * 12, 'Directional source count mismatch')
    check(len(e) == 30 * 8 * 10, 'Expression source count mismatch')
    check(not a.duplicated(['block', 't', 'phi']).any(), 'Duplicate directional rows')
    check(not e.duplicated(['block', 't', 'alpha']).any(), 'Duplicate expression rows')
    for df, coord, expected in ((a, 'phi', cfg['anisotropy_phis']), (e, 'alpha', cfg['expression_alphas'])):
        check(np.isfinite(df.select_dtypes(include='number').values).all(), 'Non-finite source data')
        check(np.allclose(sorted(df[coord].unique()), expected, rtol=0, atol=1e-14), 'Probe grid mismatch')
        check(sorted(df.t.unique()) == cfg['probe_generations'], 'Checkpoint grid mismatch')
        check(df.groupby(['block', 't']).size().eq(len(expected)).all(), 'Incomplete grid within block')
        check(df.groupby(['t', coord]).block.nunique().eq(30).all(), 'Incomplete root-block set')
        check(np.allclose(df.DeltaV_rel, df.Vrel_S - df.Vrel_N, rtol=0, atol=5e-15), 'Relational-value identity failed')
    check(np.allclose(a.radius, cfg['anisotropy_radius']), 'Unequal direction radii')
    # Match the retained time contrasts to differences of the archived full curves.
    ev = e.pivot(index=['block', 't'], columns='alpha', values='DeltaV_rel')
    av = a.pivot(index=['block', 't'], columns='phi', values='DeltaV_rel')
    ev_diff = ev[.4] - ev[1.0]
    pi_col = next(x for x in av.columns if np.isclose(x, np.pi, atol=1e-14))
    av_diff = av[pi_col] - av[0.0]
    ec2 = ec.set_index(['block', 't']).expression_C4.reindex(ev_diff.index)
    ac2 = ac.set_index(['block', 't']).anisotropy_C5.reindex(av_diff.index)
    ediff = float(np.max(np.abs(ec2 - ev_diff)))
    adiff = float(np.max(np.abs(ac2 - av_diff)))
    check(ediff < 1e-14 and adiff < 1e-14, 'Archived contrast mismatch')
    # Panel 5b is unchanged and is consistent with the mapping source.
    d1 = dense.sort_values(['p', 't']).reset_index(drop=True)
    d2 = dense_mapping.sort_values(['p', 't']).reset_index(drop=True)
    check(d1.shape == d2.shape, 'Dense summary shape mismatch')
    check(np.allclose(d1.values, d2.values, rtol=0, atol=1e-14), 'Dense summaries differ')
    prospective = pd.read_csv(root / 'sources/prospective/LATTICE_PROSPECTIVE_CONTRASTS_v1.0.0.csv')
    anchors = pd.read_csv(original / 'CROSS_REALIZATION_EVIDENCE_ANCHORS_v1.0.0.csv', keep_default_na=False)
    check(len(anchors) == 12, 'Expected 12 cross-realization cells')
    # Frozen prospective records, not inferred from the new mapping curves.
    for cid, expected in {'C1': [.00854079, .00734351, .00976737],
                          'C4': [.10597441, .10290756, .10892076],
                          'C5': [.15742683, .15369067, .16105461]}.items():
        row = prospective.loc[prospective.contrast.eq(cid)].iloc[0]
        check(np.allclose([row['mean'], row.ci99_low, row.ci99_high], expected, rtol=0, atol=1e-12), 'Prospective anchor mismatch')
    t = spec['mapping_generation']
    s_a = summarize(a[a.t.eq(t)], 'phi', 'DeltaV_rel')
    s_a.insert(1, 'phi_degrees', np.rad2deg(s_a.phi))
    s_e = summarize(e[e.t.eq(t)], 'alpha', 'DeltaV_rel')
    s_ac = summarize(ac, 't', 'anisotropy_C5')
    s_ec = summarize(ec, 't', 'expression_C4')
    derived = root / 'derived'; derived.mkdir(exist_ok=True)
    s_a.to_csv(derived / 'FIGURE_5A_DIRECTIONAL_PROFILE_T50.csv', index=False)
    s_e.to_csv(derived / 'FIGURE_S6A_EXPRESSION_PROFILE_T50.csv', index=False)
    s_ec.to_csv(derived / 'FIGURE_S6C_EXPRESSION_CONTRAST_TRAJECTORY.csv', index=False)
    s_ac.to_csv(derived / 'FIGURE_S6D_ANISOTROPY_CONTRAST_TRAJECTORY.csv', index=False)
    prospective[prospective.contrast.isin(['C1', 'C4', 'C5'])].to_csv(derived / 'FIGURE_S6B_PROSPECTIVE_SUMMARIES.csv', index=False)
    qc = {
        'source_hashes_verified': len(manifest),
        'directional_rows': len(a), 'expression_rows': len(e),
        'independent_root_blocks_per_probe': 30,
        'display_generation': t, 'display_fidelity': .95,
        'display_direction_count': len(s_a), 'display_expression_count': len(s_e),
        'display_coordinates_are_complete_archived_grids': True,
        'no_added_360_degree_datapoint': True,
        'all_direction_radii': sorted(a.radius.unique().tolist()),
        'uncertainty_mapping': 'sample SD / sqrt(n), n=30 root blocks',
        'uncertainty_prospective': 'archived 99% bootstrap intervals, not recalculated',
        'max_abs_expression_contrast_reconstruction_error': ediff,
        'max_abs_directional_contrast_reconstruction_error': adiff,
        'figure5b_unchanged_source_summary_verified': True,
        'figure5c_unchanged_anchor_table_sha256': sha(original / 'CROSS_REALIZATION_EVIDENCE_ANCHORS_v1.0.0.csv'),
        'new_evolution_runs': 0, 'new_hypothesis_tests': 0,
        'figure5a_mean_range': [float(s_a['mean'].min()), float(s_a['mean'].max())],
        'figure_s6a_generation50_mean_by_alpha': {str(row.alpha): float(row['mean']) for _, row in s_e.iterrows()},
        'status': 'PASS'
    }
    (root / 'qc/NUMERICAL_QC.json').write_text(json.dumps(qc, indent=2) + '\n')
    return dict(direction=s_a, expression=s_e, ac=s_ac, ec=s_ec,
                dense=dense, anchors=anchors, prospective=prospective)


def build_fig5(root: Path, data: dict, original_a: bool = False) -> None:
    dense = data['dense']; heat = dense[dense.p < 1].copy()
    pvals = np.sort(heat.p.unique()); tvals = np.sort(heat.t.unique())
    pivot = heat.pivot(index='p', columns='t', values='DeltaV_rel').loc[pvals, tvals]
    a50 = heat[heat.t.between(41, 50)].groupby('p').DeltaV_rel.mean().reindex(pvals)
    a50.rename('A50').reset_index().to_csv(root / 'derived/FIGURE_5B_A50.csv', index=False)
    fig = plt.figure(figsize=(12.8, 8.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.15, .92], width_ratios=[.82, 1.18],
                         left=.075, right=.975, top=.94, bottom=.08, wspace=.31, hspace=.38)
    ax = fig.add_subplot(gs[0, 0]); label(ax, 'a')
    if original_a:
        # Baseline control for testing faithful reconstruction of unchanged panels.
        row = data['prospective'].set_index('contrast').loc['C1']
        m, lo, hi = row['mean'], row.ci99_low, row.ci99_high
        ax.set_title('Prospective lattice history specificity', loc='left', pad=8)
        ax.axvline(0, color=GRAY, ls='--', lw=.9)
        ax.errorbar([m], [0], xerr=[[m-lo], [hi-m]], fmt='o', color=GREEN,
                    mfc=GREEN, ms=7, capsize=4, lw=1.6)
        ax.set_yticks([]); ax.set_xlabel('matching-history fitness advantage')
        ax.text(.98, .15, '30/30 blocks > 0\n99% bootstrap CI', transform=ax.transAxes,
                ha='right', fontsize=9, color='#555555')
    else:
        d = data['direction']
        ax.set_title('Post-confirmatory directional response\nat equal displacement', loc='left', pad=8)
        ax.errorbar(d.phi_degrees, d['mean'], yerr=d['sem'], fmt='o-',
                    color=ORANGE, mfc=ORANGE, mec=ORANGE, ms=4.8,
                    capsize=2.6, lw=1.6, elinewidth=.95)
        ax.axhline(0, color=GRAY, ls='--', lw=.8, zorder=0)
        ax.set_xlim(-8, 338); ax.set_ylim(-.005, .28)
        ax.set_xticks([0, 90, 180, 270, 330])
        ax.set_yticks([0, .05, .10, .15, .20, .25])
        ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        ax.set_xlabel('probe direction (degrees)')
        ax.set_ylabel('relational causal value\n' + r'$\Delta V_{\rm rel}$ (fitness units)')
        ax.text(.03, .06, 'Equal radius ' + r'$r=0.6$' + '\n' + r'$p=0.95$; generation 50',
                transform=ax.transAxes, fontsize=8.8, va='bottom', color='#555555')
    clean_ax(ax)
    # Panel b: original source values, plotting geometry, labels and appearance.
    sub = gs[0, 1].subgridspec(1, 3, width_ratios=[5.0, 1.35, .32], wspace=.20)
    ax = fig.add_subplot(sub[0, 0]); marg = fig.add_subplot(sub[0, 1], sharey=ax)
    cax = fig.add_subplot(sub[0, 2]); label(ax, 'b', x=-.16, y=1.07)
    ax.set_title('Post-confirmatory heredity mapping\nacross fidelity and time', loc='left', pad=8)
    im = ax.imshow(pivot.values, origin='lower', aspect='auto', cmap='viridis',
                   interpolation='nearest', extent=[0, 50, pvals.min(), pvals.max()])
    ax.set_xlabel('generation'); ax.set_ylabel('transmission fidelity $p$')
    ax.set_xticks([0, 10, 20, 30, 40, 50]); ax.set_yticks([0, .2, .4, .6, .8, .975])
    ax.set_yticklabels(['0', '0.2', '0.4', '0.6', '0.8', '0.975'])
    marg.plot(a50.values, a50.index.values, 'o-', color=BLACK, ms=3.3, lw=1.3)
    marg.set_xlabel('$A_{50}(p)$', labelpad=3); marg.set_xlim(0, .18)
    marg.set_xticks([0, .09, .17]); marg.set_xticklabels(['0', '0.09', '0.17'])
    marg.tick_params(axis='y', left=False, labelleft=False); clean_ax(marg)
    cb = fig.colorbar(im, cax=cax, format='%.2f')
    cb.ax.set_title(r'$\Delta V_{\rm rel}$', fontsize=9, pad=5)
    cb.set_ticks([0, .05, .10, .15]); cb.ax.yaxis.set_ticks_position('left')
    cb.ax.tick_params(labelsize=8, pad=2)
    # Panel c: preserve all 12 original prospective evidence entries without refitting.
    ax = fig.add_subplot(gs[1, :]); ax.set_axis_off(); label(ax, 'c', x=-.055, y=1.06)
    ax.set_title('Cross-realization prospective evidence anchors', loc='left', pad=8)
    rows = ['History specificity', 'Heredity dependence', 'Acquisition-expression', 'Equal-distance anisotropy']
    cols = ['Model B', 'Catalytic', 'Lattice']
    header, face_label, cell = '#DEDEDE', '#EFEFEF', '#E4F0E5'
    x0, y0, wlabel, wcol, rh = .08, .06, .34, .175, .185
    ax.add_patch(Rectangle((x0, y0+4*rh), wlabel, rh, facecolor=header, edgecolor='white', transform=ax.transAxes))
    for j, col in enumerate(cols):
        x = x0 + wlabel + j*wcol
        ax.add_patch(Rectangle((x, y0+4*rh), wcol, rh, facecolor=header, edgecolor='white', transform=ax.transAxes))
        ax.text(x+wcol/2, y0+4*rh+rh/2, col, ha='center', va='center', fontweight='bold', fontsize=10, transform=ax.transAxes)
    for i, sig in enumerate(rows):
        y = y0+(3-i)*rh
        ax.add_patch(Rectangle((x0, y), wlabel, rh, facecolor=face_label, edgecolor='white', transform=ax.transAxes))
        ax.text(x0+.012, y+rh/2, sig, ha='left', va='center', fontweight='bold', fontsize=9.7, transform=ax.transAxes)
        for j, col in enumerate(cols):
            rec = data['anchors'][(data['anchors'].signature == sig) & (data['anchors'].realization == col)].iloc[0]
            x = x0 + wlabel + j*wcol
            ax.add_patch(Rectangle((x, y), wcol, rh, facecolor=cell, edgecolor='white', transform=ax.transAxes))
            txt = f'{rec.anchor}\n{rec.metric}' + (f'\n{rec.support}' if rec.support else '')
            ax.text(x+wcol/2, y+rh/2, txt, ha='center', va='center', fontsize=8.2, linespacing=1.15, transform=ax.transAxes)
    ax.text(x0+wlabel+1.5*wcol, y0-.005, 'Representative frozen anchors; metrics and units differ among realizations.',
            ha='center', va='top', fontsize=8.5, color='#555555', transform=ax.transAxes)
    # Store canvas-space panel limits for image checks independent of tight cropping.
    fig.canvas.draw()
    if original_a:
        save(fig, root / 'qc/FIGURE_5_BASELINE_REBUILD')
    else:
        save(fig, root / 'figures/FIGURE_5_REVIEW_DRAFT_v1.1.0')


def build_s6(root: Path, data: dict) -> None:
    fig = plt.figure(figsize=(12.8, 9.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.25, 1.0], left=.085, right=.975,
                         top=.91, bottom=.075, wspace=.32, hspace=.43)
    ax = fig.add_subplot(gs[0, 0]); label(ax, 'a')
    ax.set_title('Post-confirmatory acquisition-expression\nacross probe strengths', loc='left', pad=9)
    d = data['expression']
    ax.errorbar(d.alpha, d['mean'], yerr=d['sem'], fmt='o-', color=BLUE,
                mfc=BLUE, mec=BLUE, ms=4.8, capsize=2.6, lw=1.6, elinewidth=.95,
                label=r'Mean $\pm$ 1 SEM')
    ax.axvline(1, color=GRAY, ls='--', lw=.9, zorder=0, label='Training strength')
    ax.axhline(0, color=GRAY, ls='--', lw=.8, zorder=0)
    ax.set_xlim(-.04, 1.84); ax.set_ylim(-.005, .34)
    ax.set_xticks([0, .4, .8, 1.0, 1.4, 1.8]); ax.set_yticks([0, .05, .1, .15, .2, .25, .3])
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax.set_xlabel(r'probe strength $\alpha$  ($B_P=\alpha B_H$)')
    ax.set_ylabel('relational causal value\n' + r'$\Delta V_{\rm rel}$ (fitness units)')
    ax.legend(loc='upper right', frameon=False, fontsize=8.7)
    ax.text(.96, .77, r'$p=0.95$; generation 50', transform=ax.transAxes,
            fontsize=8.8, ha='right', color='#555555')
    clean_ax(ax)
    # Compact prospective evidence panel. Three independently labelled scales
    # prevent presentation as interchangeable or standardized effect sizes.
    parent = fig.add_subplot(gs[0, 1]); parent.set_axis_off(); label(parent, 'b')
    parent.set_title('Original prospective confirmation\nSeparate tests; separate horizontal scales', loc='left', pad=9)
    parent.text(0, .985, '200 generations; 99% bootstrap confidence intervals', transform=parent.transAxes,
                fontsize=8.8, va='top', color='#555555')
    configs = [
        ('C1', 'History specificity', 'matching-history fitness advantage', GREEN,
         (-.00035, .011), [0, .005, .010], '%.3f', .72),
        ('C4', 'Acquisition-expression', r'$\Delta V_{\rm rel}(0.4B_H)-\Delta V_{\rm rel}(B_H)$', BLUE,
         (-.004, .12), [0, .04, .08, .12], '%.2f', .39),
        ('C5', 'Equal-distance anisotropy', r'$\Delta V_{\rm rel}(\phi=\pi)-\Delta V_{\rm rel}(\phi=0)$', ORANGE,
         (-.005, .18), [0, .06, .12, .18], '%.2f', .06),
    ]
    for cid, title, xlabel, color, lims, ticks, fmt, bottom in configs:
        a = parent.inset_axes([.02, bottom, .96, .125])
        row = data['prospective'].set_index('contrast').loc[cid]
        m, lo, hi = float(row['mean']), float(row.ci99_low), float(row.ci99_high)
        a.axvline(0, color=GRAY, ls='--', lw=.8, zorder=0)
        a.errorbar([m], [0], xerr=[[m-lo], [hi-m]], fmt='o', color=color,
                   ms=5.5, capsize=3, lw=1.4)
        a.set_ylim(-.4, .4); a.set_yticks([]); a.set_xlim(*lims); a.set_xticks(ticks)
        a.xaxis.set_major_formatter(FormatStrFormatter(fmt))
        a.set_title(title, loc='left', fontsize=9.4, pad=5)
        a.text(1, 1.13, '30/30 positive', transform=a.transAxes, ha='right', va='bottom',
               fontsize=8.5, color='#555555')
        a.set_xlabel(xlabel, fontsize=8.7, labelpad=2)
        clean_ax(a); a.spines['left'].set_visible(False)
        a.tick_params(axis='x', labelsize=8.4, length=3, pad=2)
    ax = fig.add_subplot(gs[1, 0]); label(ax, 'c')
    ax.set_title('Post-confirmatory acquisition-expression\ndevelopment', loc='left', pad=9)
    d = data['ec']
    ax.errorbar(d.t, d['mean'], yerr=d['sem'], fmt='o-', color=BLUE, ms=4.8,
                capsize=2.5, lw=1.6, elinewidth=.9)
    ax.axhline(0, color=GRAY, ls='--', lw=.8, zorder=0)
    ax.set_xlabel('generation'); ax.set_ylabel('acquisition-expression contrast')
    ax.set_xticks([0, 10, 20, 30, 40, 50]); ax.set_xlim(-1.5, 51.5)
    clean_ax(ax)
    ax = fig.add_subplot(gs[1, 1]); label(ax, 'd')
    ax.set_title('Post-confirmatory equal-distance\nanisotropy development', loc='left', pad=9)
    d = data['ac']
    ax.errorbar(d.t, d['mean'], yerr=d['sem'], fmt='o-', color=ORANGE, ms=4.8,
                capsize=2.5, lw=1.6, elinewidth=.9)
    ax.axhline(0, color=GRAY, ls='--', lw=.8, zorder=0)
    ax.set_xlabel('generation'); ax.set_ylabel('anisotropy contrast')
    ax.set_xticks([0, 10, 20, 30, 40, 50]); ax.set_xlim(-1.5, 51.5)
    clean_ax(ax)
    save(fig, root / 'figures/SUPPLEMENTARY_FIGURE_S6_REVIEW_DRAFT_v1.2.0')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--baseline', action='store_true', help='Also rebuild old Figure 5 as a visual regression control.')
    args = parser.parse_args()
    root = args.root.resolve()
    plt.rcParams.update({
        'font.family': 'DejaVu Sans', 'font.size': 9.5, 'axes.titlesize': 12.0,
        'axes.titleweight': 'bold', 'axes.labelsize': 10.5, 'xtick.labelsize': 9.0,
        'ytick.labelsize': 9.0, 'legend.fontsize': 8.6, 'axes.linewidth': .9,
        'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none',
        'figure.facecolor': 'white', 'savefig.facecolor': 'white', 'svg.hashsalt': 'SCO_FIG5_S6_REVIEW_v1'
    })
    for folder in ('qc', 'derived', 'figures'):
        (root / folder).mkdir(exist_ok=True)
    data = load_and_validate(root)
    build_fig5(root, data)
    build_s6(root, data)
    if args.baseline:
        build_fig5(root, data, original_a=True)
    print('PASS: archived sources validated; both review figures rebuilt.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError) as exc:
        print(f'Build failed: {exc}', file=sys.stderr)
        sys.exit(1)
