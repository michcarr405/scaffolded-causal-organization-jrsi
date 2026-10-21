from pathlib import Path
import pandas as pd, matplotlib.pyplot as plt
ROOT=Path('/mnt/data/CATALYTIC_COMPLEX_SCAFFOLD_STRENGTH_CONFIRMATORY_v1.0.0')
s=pd.read_csv(ROOT/'results/STRENGTH_SUMMARY.csv')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':12,'axes.labelsize':10,'xtick.labelsize':9,'ytick.labelsize':9})
# B
fig,ax=plt.subplots(figsize=(5.2,4.45)); x=s.scaffold_strength
ax.errorbar(x,s.fitness_ancestor_mean,yerr=[s.fitness_ancestor_mean-s.fitness_ancestor_ci95_lo,s.fitness_ancestor_ci95_hi-s.fitness_ancestor_mean],fmt='o-',lw=1.4,ms=3.8,capsize=1.6)
ax.set_title('Stronger reaction-field scaffold lowers ancestral fitness',loc='left',fontweight='bold'); ax.set_xlabel(r'reaction-field scaffold strength $s$'); ax.set_ylabel('ancestral fitness (generation 0)'); ax.spines[['top','right']].set_visible(False); fig.tight_layout(); fig.savefig(ROOT/'results/FIGURE_4B_CONFIRMATORY.pdf'); fig.savefig(ROOT/'results/FIGURE_4B_CONFIRMATORY.png',dpi=300); plt.close(fig)
# C
fig,ax=plt.subplots(figsize=(5.2,4.45)); blue='#0072B2'; orange='#E69F00'; ax.axhline(0,color='.6',lw=.9,ls='--')
ax.errorbar(x,s.selected_minus_ancestor_mean,yerr=[s.selected_minus_ancestor_mean-s.selected_minus_ancestor_ci95_lo,s.selected_minus_ancestor_ci95_hi-s.selected_minus_ancestor_mean],fmt='o-',color=blue,ms=4,capsize=1.7,lw=1.4,label='selected - ancestor')
ax.errorbar(x,s.neutral_minus_ancestor_mean,yerr=[s.neutral_minus_ancestor_mean-s.neutral_minus_ancestor_ci95_lo,s.neutral_minus_ancestor_ci95_hi-s.neutral_minus_ancestor_mean],fmt='s--',color=orange,mfc='white',ms=4,capsize=1.7,lw=1.2,label='neutral - ancestor')
ax.set_title('Selection drives fitness recovery\nabove the ancestral baseline',loc='left',fontweight='bold'); ax.set_xlabel(r'reaction-field scaffold strength $s$'); ax.set_ylabel('fitness change from ancestral baseline'); ax.legend(frameon=False,loc='upper left'); ax.spines[['top','right']].set_visible(False); fig.tight_layout(); fig.savefig(ROOT/'results/FIGURE_4C_CONFIRMATORY.pdf'); fig.savefig(ROOT/'results/FIGURE_4C_CONFIRMATORY.png',dpi=300); plt.close(fig)
