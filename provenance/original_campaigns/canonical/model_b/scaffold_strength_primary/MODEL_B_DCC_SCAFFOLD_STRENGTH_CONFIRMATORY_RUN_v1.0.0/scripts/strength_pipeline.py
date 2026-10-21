from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
from typing import Iterable
import numpy as np
from numba import njit

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SRC=ROOT/'source'
sys.path.insert(0,str(SRC))
from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.core import compute_fitnesses_and_observations
from modelb_semantic_repo.original_model.simulation import init_population, reproduce_with_partitioning
from modelb_semantic_repo.rng import make_generator

N_MOTIFS=4**5; N_STATES=4; N_SEGMENTS=4
CHECKPOINTS=(0,25,50,75,100,125,150,175,200,225,250)
N_GENS=250; P_INHERIT=0.975; THETA=1.2; MU=0.001
N_SPEC_DRAWS=16; FIXED_PROBE_BETA=3.0
NATIVE=(2,0,3,1); REVERSED=(1,3,0,2)


def state_hash(pop: np.ndarray)->str:
    a=np.ascontiguousarray(pop); h=hashlib.sha256(); h.update(str(a.dtype).encode()); h.update(b'|'); h.update(('x'.join(map(str,a.shape))).encode()); h.update(b'|'); h.update(a.tobytes()); return h.hexdigest()

def motif_tensor(pop):
    p=np.asarray(pop,dtype=np.int64); w=np.lib.stride_tricks.sliding_window_view(p,5,axis=-1); powers=np.array([256,64,16,4,1],dtype=np.int64); return np.tensordot(w,powers,axes=([-1],[0])).astype(np.int64,copy=False)

def position_segment_labels(chain_len=56):
    return np.repeat(np.arange(4,dtype=np.int64),chain_len//4)

def motif_segment_counts(pop):
    m=motif_tensor(pop); seg=position_segment_labels(m.shape[-1]); flatm=m.reshape(-1); flats=np.broadcast_to(seg,m.shape).reshape(-1); idx=flats*N_MOTIFS+flatm; return np.bincount(idx,minlength=4*N_MOTIFS).reshape(4,N_MOTIFS).astype(np.int64)

def make_kernel(affinity,mapping:Iterable[int],beta:float,temperature:float=THETA):
    logits=np.broadcast_to(np.asarray(affinity,float)[None,:,:],(4,N_MOTIFS,4)).copy()
    for s,f in enumerate(tuple(mapping)): logits[s,:,int(f)]+=float(beta)
    x=logits/float(temperature); x-=x.max(axis=2,keepdims=True); ex=np.exp(x); return ex/ex.sum(axis=2,keepdims=True)

def jsd_bits(p,q):
    p=np.asarray(p,float).reshape(-1); q=np.asarray(q,float).reshape(-1); p=p/p.sum(); q=q/q.sum(); m=.5*(p+q); mp=p>0; mq=q>0
    return float(.5*np.sum(p[mp]*np.log2(p[mp]/m[mp]))+.5*np.sum(q[mq]*np.log2(q[mq]/m[mq])))

def c_down_primary(pop,affinity,mapping,beta,temperature=THETA):
    counts=motif_segment_counts(pop); total=counts.sum(); psm=counts.astype(float)/total; ps=psm.sum(axis=1,keepdims=True); pm=psm.sum(axis=0,keepdims=True); erased=ps@pm; ker=make_kernel(affinity,mapping,beta,temperature)
    intact_sz=np.einsum('sm,smz->sz',psm,ker); erased_sz=np.einsum('sm,smz->sz',erased,ker)
    return {'jsd_bits':jsd_bits(intact_sz,erased_sz),'motif_marginal_error':float(np.max(np.abs(erased.sum(axis=0)-pm.reshape(-1)))),'segment_marginal_error':float(np.max(np.abs(erased.sum(axis=1)-ps.reshape(-1))))}

@njit
def probe_two_mapping_fitnesses(motifs3,cdf_native,cdf_rev,productive,anti,reward,penalty,uniforms):
    n_draws=uniforms.shape[0]; n_cells,n_seqs,chain_len=motifs3.shape; seg_len=chain_len//4; out=np.empty((2,n_draws),dtype=np.float64)
    for mp in range(2):
        cdf=cdf_native if mp==0 else cdf_rev
        for d in range(n_draws):
            total_fit=0.0; obs_idx=0
            for ci in range(n_cells):
                prod_sum=0.0; anti_sum=0.0
                for si in range(n_seqs):
                    prev=-1
                    for pos in range(chain_len):
                        seg=pos//seg_len
                        if seg>=4: seg=3
                        motif=motifs3[ci,si,pos]; u=uniforms[d,obs_idx]; obs_idx+=1
                        if u<=cdf[seg,motif,0]: chosen=0
                        elif u<=cdf[seg,motif,1]: chosen=1
                        elif u<=cdf[seg,motif,2]: chosen=2
                        else: chosen=3
                        if pos>0:
                            if productive[prev,chosen]: prod_sum+=1.0
                            if anti[prev,chosen]: anti_sum+=1.0
                        prev=chosen
                fit=1.0+reward*(prod_sum/n_seqs)-penalty*(anti_sum/n_seqs)
                if fit<0.1: fit=0.1
                total_fit+=fit
            out[mp,d]=total_fit/n_cells
    return out

def specificity(pop,params,beta,seed,ratio_id,assay,uniforms=None,n_draws=N_SPEC_DRAWS):
    motifs=motif_tensor(pop); nw=motifs.size
    if uniforms is None:
        rng=make_generator(int(seed),'strength-specificity-crn',str(ratio_id),str(assay)); uniforms=rng.random((int(n_draws),nw))
    kn=make_kernel(params['motif_affinity_matrix'],NATIVE,beta,params['temperature']); kr=make_kernel(params['motif_affinity_matrix'],REVERSED,beta,params['temperature'])
    cn=np.cumsum(kn,axis=2); cr=np.cumsum(kr,axis=2); cn[:,:,-1]=1.0; cr[:,:,-1]=1.0
    vals=probe_two_mapping_fitnesses(motifs,cn,cr,params['productive_pairs'],params['anti_pairs'],float(params['reward_strength']),float(params['penalty_strength']),np.asarray(uniforms,float))
    means=vals.mean(axis=1)
    return {'native_mean':float(means[0]),'reversed_mean':float(means[1]),'R':float(means[0]-means[1]),'draw_values':vals}

def params_for(beta):
    p=default_parameters(); p['segment_favored_met']=np.asarray(NATIVE,dtype=np.int64); p['bias_strength']=float(beta); p['temperature']=THETA; p['mutation_rate']=MU; p['n_gens']=N_GENS; return p

def observe_with_uniforms(pop,params,uniforms):
    return compute_fitnesses_and_observations(pop,params['motif_affinity_matrix'],params['segment_favored_met'],params['bias_strength'],params['productive_pairs'],params['anti_pairs'],params['reward_strength'],params['penalty_strength'],params['temperature'],uniforms)

def _write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def _write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def run_ratio_pair(block_id,ratio_id,beta,ratio,seed,selected_run_id,neutral_run_id,outdir:Path,validation_version='v1.0.0'):
    params=params_for(beta); affinity=params['motif_affinity_matrix']; nw=params['n_cells']*params['n_seqs']*(params['seq_len']-4)
    init_rng=make_generator(int(seed),'strength-initialization'); pop0=init_population(params['n_cells'],params['n_seqs'],params['seq_len'],init_rng)
    pop_s=pop0.copy(); pop_n=pop0.copy()
    # Frozen CRN g0 observation is shared across all ratios and modes within block.
    u0=make_generator(int(seed),'strength-g0-observation').random(nw)
    fs0,_,_=observe_with_uniforms(pop_s,params,u0); fn0,_,_=observe_with_uniforms(pop_n,params,u0)
    # Technical split of the frozen propagation namespace, documented preproduction.
    obs_s=make_generator(int(seed),'strength-propagation',str(ratio_id),'observation'); obs_n=make_generator(int(seed),'strength-propagation',str(ratio_id),'observation')
    rep_s=make_generator(int(seed),'strength-propagation',str(ratio_id),'reproduction'); rep_n=make_generator(int(seed),'strength-propagation',str(ratio_id),'reproduction')
    metrics={'selected':[],'neutral':[]}
    def add(mode,run_id,g,fit,pop):
        cd=c_down_primary(pop,affinity,NATIVE,beta,THETA)
        metrics[mode].append({'run_id':run_id,'block_id':block_id,'ratio_id':ratio_id,'beta_over_theta':float(ratio),'beta':float(beta),'mode':mode,'base_seed_uint32':int(seed),'generation':int(g),'mean_fitness':float(fit.mean()),'C_down_train':float(cd['jsd_bits']),'population_hash':state_hash(pop),'validation_version':validation_version})
    add('selected',selected_run_id,0,fs0,pop_s); add('neutral',neutral_run_id,0,fn0,pop_n)
    fs=fs0; fn=fn0
    for g in range(1,N_GENS+1):
        pop_s=reproduce_with_partitioning(pop_s,fs,MU,P_INHERIT,rep_s)
        pop_n=reproduce_with_partitioning(pop_n,np.ones_like(fn),MU,P_INHERIT,rep_n)
        if g==N_GENS:
            ue=make_generator(int(seed),'strength-endpoint-observation',str(ratio_id)).random(nw)
            fs,_,_=observe_with_uniforms(pop_s,params,ue); fn,_,_=observe_with_uniforms(pop_n,params,ue)
        else:
            us=obs_s.random(nw); un=obs_n.random(nw)
            fs,_,_=observe_with_uniforms(pop_s,params,us); fn,_,_=observe_with_uniforms(pop_n,params,un)
        if g in CHECKPOINTS:
            add('selected',selected_run_id,g,fs,pop_s); add('neutral',neutral_run_id,g,fn,pop_n)
    # endpoint deterministic Cdown at training and standardized probe
    cds_t=c_down_primary(pop_s,affinity,NATIVE,beta,THETA)['jsd_bits']; cdn_t=c_down_primary(pop_n,affinity,NATIVE,beta,THETA)['jsd_bits']
    cds_p=c_down_primary(pop_s,affinity,NATIVE,FIXED_PROBE_BETA,THETA)['jsd_bits']; cdn_p=c_down_primary(pop_n,affinity,NATIVE,FIXED_PROBE_BETA,THETA)['jsd_bits']
    # CRN specificity: same draws across selected/neutral and native/reversed within assay.
    us_t=make_generator(int(seed),'strength-specificity-crn',str(ratio_id),'train').random((N_SPEC_DRAWS,nw))
    us_p=make_generator(int(seed),'strength-specificity-crn',str(ratio_id),'probe3').random((N_SPEC_DRAWS,nw))
    rs_t=specificity(pop_s,params,beta,seed,ratio_id,'train',us_t); rn_t=specificity(pop_n,params,beta,seed,ratio_id,'train',us_t)
    rs_p=specificity(pop_s,params,FIXED_PROBE_BETA,seed,ratio_id,'probe3',us_p); rn_p=specificity(pop_n,params,FIXED_PROBE_BETA,seed,ratio_id,'probe3',us_p)
    anc_hash=state_hash(pop0)
    end={
      'selected':{'run_id':selected_run_id,'block_id':block_id,'ratio_id':ratio_id,'beta_over_theta':float(ratio),'beta':float(beta),'mode':'selected','base_seed_uint32':int(seed),'F0':float(fs0.mean()),'F250':float(fs.mean()),'G':float(fs.mean()-fs0.mean()),'C_down_train_g250':float(cds_t),'C_down_probe_beta3_g250':float(cds_p),'R_train_g250':float(rs_t['R']),'R_probe_beta3_g250':float(rs_p['R']),'native_train':rs_t['native_mean'],'reversed_train':rs_t['reversed_mean'],'native_probe3':rs_p['native_mean'],'reversed_probe3':rs_p['reversed_mean'],'ancestor_hash':anc_hash,'final_hash':state_hash(pop_s),'validation_version':validation_version},
      'neutral':{'run_id':neutral_run_id,'block_id':block_id,'ratio_id':ratio_id,'beta_over_theta':float(ratio),'beta':float(beta),'mode':'neutral','base_seed_uint32':int(seed),'F0':float(fn0.mean()),'F250':float(fn.mean()),'G':float(fn.mean()-fn0.mean()),'C_down_train_g250':float(cdn_t),'C_down_probe_beta3_g250':float(cdn_p),'R_train_g250':float(rn_t['R']),'R_probe_beta3_g250':float(rn_p['R']),'native_train':rn_t['native_mean'],'reversed_train':rn_t['reversed_mean'],'native_probe3':rn_p['native_mean'],'reversed_probe3':rn_p['reversed_mean'],'ancestor_hash':anc_hash,'final_hash':state_hash(pop_n),'validation_version':validation_version}
    }
    for mode,run_id,pop in [('selected',selected_run_id,pop_s),('neutral',neutral_run_id,pop_n)]:
        np.savez_compressed(outdir/'raw'/'states'/f'{run_id}_g250.npz',g0=pop0,g250=pop,base_seed_uint32=np.asarray(seed,dtype=np.uint32),ratio_id=np.asarray(ratio_id),beta=np.asarray(beta),beta_over_theta=np.asarray(ratio))
        _write_csv(outdir/'raw'/'metrics'/f'{run_id}_metrics.csv',metrics[mode]); _write_json(outdir/'raw'/'endpoints'/f'{run_id}_endpoint.json',end[mode])
    pair={'block_id':block_id,'ratio_id':ratio_id,'beta_over_theta':float(ratio),'beta':float(beta),'base_seed_uint32':int(seed),'selected_run_id':selected_run_id,'neutral_run_id':neutral_run_id,'F0':float(fs0.mean()),'F250_selected':float(fs.mean()),'F250_neutral':float(fn.mean()),'G_selected':float(fs.mean()-fs0.mean()),'G_neutral':float(fn.mean()-fn0.mean()),'DeltaF':float(fs.mean()-fn.mean()),'C_train_selected':float(cds_t),'C_train_neutral':float(cdn_t),'DeltaC_train':float(cds_t-cdn_t),'C_probe3_selected':float(cds_p),'C_probe3_neutral':float(cdn_p),'DeltaC_probe3':float(cds_p-cdn_p),'R_train_selected':float(rs_t['R']),'R_train_neutral':float(rn_t['R']),'DeltaR_train':float(rs_t['R']-rn_t['R']),'R_probe3_selected':float(rs_p['R']),'R_probe3_neutral':float(rn_p['R']),'DeltaR_probe3':float(rs_p['R']-rn_p['R']),'ancestor_hash':anc_hash,'selected_final_hash':state_hash(pop_s),'neutral_final_hash':state_hash(pop_n),'validation_version':validation_version,'status':'COMPLETE'}
    _write_json(outdir/'raw'/'endpoints'/f'{block_id}_{ratio_id}_PAIR.json',pair); return pair
