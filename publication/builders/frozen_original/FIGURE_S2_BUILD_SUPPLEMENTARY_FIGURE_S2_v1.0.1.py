from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.ticker import FormatStrFormatter, MaxNLocator

ROOT=Path('/mnt/data/SCO_SUPPLEMENTARY_FIGURE_S2_RESULT_FREEZE_JRSI_v1.0.1')
src=ROOT/'sources'
BLUE='#0072B2'; ORANGE='#E69F00'; GRAY='#777777'; BLACK='#222222'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.5,'axes.titlesize':12,'axes.labelsize':10.5,'xtick.labelsize':9,'ytick.labelsize':9,'legend.fontsize':8.8,'pdf.fonttype':42,'ps.fonttype':42,'axes.linewidth':0.9,'figure.facecolor':'white','savefig.facecolor':'white'})

DI=pd.read_csv(src/'S6_INTACT_G250_SELECTED_ENRICHMENT.csv')
DP=pd.read_csv(src/'S6_PRIMARY_POST_ERASURE_ENRICHMENT.csv')
DE=pd.read_csv(src/'S6_EXACT_MARGIN_POST_ERASURE_ENRICHMENT.csv')
order=pd.read_csv(src/'TOP24_MOTIF_ORDER.csv')
pairs=pd.read_csv(src/'PAIRED_BLOCK_ENDPOINTS_v1.0.0.csv')
labels=DI.motif_label.astype(str).tolist()
prefs=(order.preferred_segment_selected_g250.to_numpy(int)-1).tolist()
seps=[j-.5 for j in range(1,len(prefs)) if prefs[j]!=prefs[j-1]]
EI=DI[['S1','S2','S3','S4']].to_numpy(); EP=DP[['S1','S2','S3','S4']].to_numpy(); EE=DE[['S1','S2','S3','S4']].to_numpy()
cmap=LinearSegmentedColormap.from_list('orange_white_blue',[ORANGE,'#FFFFFF',BLUE])
normE=TwoSlopeNorm(vmin=-6,vcenter=0,vmax=2); normR=TwoSlopeNorm(vmin=-.012,vcenter=0,vmax=.012)

def heat_style(ax,show_y=False):
    ax.set_xticks(range(4),['S1','S2','S3','S4']); ax.set_xlabel('segment $S$'); ax.set_yticks(range(24))
    if show_y: ax.set_yticklabels(labels,fontsize=7.5); ax.set_ylabel('top-24 motif identities $M$')
    else: ax.set_yticklabels([]); ax.tick_params(axis='y',length=0)
    for y in seps: ax.axhline(y,color=BLACK,lw=.7)
    for xx in np.arange(-.5,4,1): ax.axvline(xx,color='white',lw=.3,alpha=.65)

fig=plt.figure(figsize=(10.4,8.3)); gs=fig.add_gridspec(2,2,left=.09,right=.96,top=.94,bottom=.08,wspace=.30,hspace=.35)
ax=fig.add_subplot(gs[0,0]); im=ax.imshow(EI,aspect='auto',cmap=cmap,norm=normE,interpolation='nearest'); heat_style(ax,True); ax.set_title('Intact evolved selected',pad=9,fontweight='bold'); ax.text(-.17,1.035,'(a)',transform=ax.transAxes,fontweight='bold',fontsize=12,clip_on=False); pos=ax.get_position(); cax=fig.add_axes([pos.x1+.008,pos.y0,.012,pos.height]); cb=fig.colorbar(im,cax=cax); cb.set_ticks([-6,-4,-2,0,2]); cb.ax.set_title(r'$E_{intact}$'+'\n(bits)',fontsize=7.5,pad=2)
ax=fig.add_subplot(gs[0,1]); im=ax.imshow(EP,aspect='auto',cmap=cmap,norm=normR,interpolation='nearest'); heat_style(ax,False); ax.set_title('Primary factorized erasure',pad=9,fontweight='bold'); ax.text(-.14,1.035,'(b)',transform=ax.transAxes,fontweight='bold',fontsize=12,clip_on=False); ax.text(.5,.51,'post-erasure\n$E(S,M)=0$',transform=ax.transAxes,ha='center',va='center',fontsize=9,color=GRAY); pos=ax.get_position(); cax=fig.add_axes([pos.x1+.008,pos.y0,.012,pos.height]); cb=fig.colorbar(im,cax=cax); cb.set_ticks([-.01,0,.01]); cb.ax.set_title(r'$E_{after}$'+'\n(bits)',fontsize=7.5,pad=2)
ax=fig.add_subplot(gs[1,0]); im=ax.imshow(EE,aspect='auto',cmap=cmap,norm=normR,interpolation='nearest'); heat_style(ax,True); ax.set_title('Exact-margin erasure',pad=9,fontweight='bold'); ax.text(.98,.985,'expanded residual scale',transform=ax.transAxes,ha='right',va='top',fontsize=8.2,color=GRAY,bbox=dict(facecolor='white',edgecolor='none',alpha=.82,pad=1.2)); ax.text(-.17,1.035,'(c)',transform=ax.transAxes,fontweight='bold',fontsize=12,clip_on=False); pos=ax.get_position(); cax=fig.add_axes([pos.x1+.008,pos.y0,.012,pos.height]); cb=fig.colorbar(im,cax=cax); cb.set_ticks([-.01,0,.01]); cb.ax.set_title(r'$E_{after}$'+'\n(bits)',fontsize=7.5,pad=2)
ax=fig.add_subplot(gs[1,1]); x=pairs.D_delta_C_down_primary.to_numpy(); y=pairs.A_delta_C_down_unitshuffle.to_numpy(); mx=max(x.max(),y.max())*1.04; ax.scatter(x,y,s=24,facecolors='none',edgecolors=BLUE,linewidths=1.0,alpha=.9); ax.plot([0,mx],[0,mx],':',color=BLACK,lw=1.1,label='identity'); ax.set_xlim(0,mx); ax.set_ylim(0,mx); ax.set_aspect('equal',adjustable='box'); ax.set_xlabel(r'primary $\Delta C_{\rm down}$ (bits)'); ax.set_ylabel(r'exact-margin $\Delta C_{\rm down}$ (bits)'); ax.set_title('Independent erasures agree blockwise',pad=9,fontweight='bold',loc='left',x=0.10); ax.text(-.19,1.035,'(d)',transform=ax.transAxes,fontweight='bold',fontsize=12,clip_on=False); ax.xaxis.set_major_locator(MaxNLocator(4)); ax.yaxis.set_major_locator(MaxNLocator(4)); ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f')); ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f')); ax.legend(frameon=False,loc='lower right'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
for ext in ('pdf','png','svg'):
    kw={'dpi':400} if ext=='png' else {}
    fig.savefig(ROOT/f'SUPPLEMENTARY_FIGURE_S2_FINAL_v1.0.1.{ext}',bbox_inches='tight',**kw)
plt.close(fig)
print('rebuilt S2 v1.0.1')
