from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
ROOT=Path('/mnt/data/CATALYTIC_COMPLEX_FIDELITY_CONFIRMATORY_REPLICATION_v1.0.0')
s=pd.read_csv(ROOT/'results/FIDELITY_SUMMARY.csv')
for endpoint,title,ylabel,fname in [
 ('Delta_R_pop','Reliable heredity amplifies relational organization',r'$\Delta R_{pop}$ (bits)','FIGURE_4D_FIDELITY_RPOP'),
 ('Delta_V_rel','Reliable heredity amplifies adaptive relational value',r'$\Delta V_{rel}$ (fitness units)','FIGURE_4E_FIDELITY_VREL')]:
    q=s[s.endpoint==endpoint].sort_values('transmission_fidelity')
    fig,ax=plt.subplots(figsize=(6.2,4.6))
    y=q['mean'].to_numpy(); lo=q['ci95_low'].to_numpy(); hi=q['ci95_high'].to_numpy(); x=q['transmission_fidelity'].to_numpy()
    ax.errorbar(x,y,yerr=[y-lo,hi-y],marker='o',capsize=3)
    ax.axhline(0,ls='--',lw=1,color='0.6')
    ax.set_xlabel('transmission fidelity $p$'); ax.set_ylabel(ylabel); ax.set_title(title,weight='bold')
    ax.spines[['top','right']].set_visible(False); fig.tight_layout()
    fig.savefig(ROOT/'results'/f'{fname}.png',dpi=300,bbox_inches='tight'); fig.savefig(ROOT/'results'/f'{fname}.pdf',bbox_inches='tight'); plt.close(fig)
