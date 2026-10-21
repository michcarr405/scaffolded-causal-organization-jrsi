from __future__ import annotations
import csv, hashlib, json, sys
from pathlib import Path
import numpy as np
from numba import njit
HERE=Path(__file__).resolve().parent; ROOT=HERE.parent; SRC=ROOT/'source'; sys.path.insert(0,str(SRC))
from modelb_semantic_repo.original_model.config import default_parameters
from modelb_semantic_repo.original_model.core import compute_fitnesses_and_observations
from modelb_semantic_repo.original_model.simulation import init_population, reproduce_with_partitioning
from modelb_semantic_repo.rng import make_generator

N_MOTIFS=4**5; THETA=1.2; BETA=3.0; MU=0.001; N_GENS=250; N_SPEC_DRAWS=16
NATIVE=(2,0,3,1); REVERSED=(1,3,0,2)

def state_hash(pop):
    a=np.ascontiguousarray(pop); h=hashlib.sha256(); h.update(str(a.dtype).encode()); h.update(b'|'); h.update(('x'.join(map(str,a.shape))).encode()); h.update(b'|'); h.update(a.tobytes()); return h.hexdigest()

def motif_tensor(pop):
    p=np.asarray(pop,dtype=np.int64); w=np.lib.stride_tricks.sliding_window_view(p,5,axis=-1); powers=np.array([256,64,16,4,1],dtype=np.int64)
    return np.tensordot(w,powers,axes=([-1],[0])).astype(np.int64,copy=False)

def position_segment_labels(chain_len=56): return np.repeat(np.arange(4,dtype=np.int64),chain_len//4)

def motif_segment_counts(pop):
    m=motif_tensor(pop); seg=position_segment_labels(m.shape[-1]); flatm=m.reshape(-1); flats=np.broadcast_to(seg,m.shape).reshape(-1); idx=flats*N_MOTIFS+flatm
    return np.bincount(idx,minlength=4*N_MOTIFS).reshape(4,N_MOTIFS).astype(np.int64)

def make_kernel(affinity,mapping,beta=BETA,temperature=THETA):
    logits=np.broadcast_to(np.asarray(affinity,float)[None,:,:],(4,N_MOTIFS,4)).copy()
    for s,f in enumerate(tuple(mapping)): logits[s,:,int(f)]+=float(beta)
    x=logits/float(temperature); x-=x.max(axis=2,keepdims=True); ex=np.exp(x); return ex/ex.sum(axis=2,keepdims=True)

def jsd_bits(p,q):
    p=np.asarray(p,float).reshape(-1); q=np.asarray(q,float).reshape(-1); p=p/p.sum(); q=q/q.sum(); m=.5*(p+q); mp=p>0; mq=q>0
    return float(.5*np.sum(p[mp]*np.log2(p[mp]/m[mp]))+.5*np.sum(q[mq]*np.log2(q[mq]/m[mq])))

def c_down_primary(pop,affinity,mapping=NATIVE,beta=BETA,temperature=THETA):
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

def params_for():
    p=default_parameters(); p['segment_favored_met']=np.asarray(NATIVE,dtype=np.int64); p['bias_strength']=BETA; p['temperature']=THETA; p['mutation_rate']=MU; p['n_gens']=N_GENS; return p

def observe_with_uniforms(pop,params,uniforms):
    return compute_fitnesses_and_observations(pop,params['motif_affinity_matrix'],params['segment_favored_met'],params['bias_strength'],params['productive_pairs'],params['anti_pairs'],params['reward_strength'],params['penalty_strength'],params['temperature'],uniforms)

def specificity(pop,params,uniforms):
    motifs=motif_tensor(pop); kn=make_kernel(params['motif_affinity_matrix'],NATIVE,BETA,THETA); kr=make_kernel(params['motif_affinity_matrix'],REVERSED,BETA,THETA)
    cn=np.cumsum(kn,axis=2); cr=np.cumsum(kr,axis=2); cn[:,:,-1]=1.0; cr[:,:,-1]=1.0
    vals=probe_two_mapping_fitnesses(motifs,cn,cr,params['productive_pairs'],params['anti_pairs'],float(params['reward_strength']),float(params['penalty_strength']),np.asarray(uniforms,float))
    means=vals.mean(axis=1); return {'native_mean':float(means[0]),'reversed_mean':float(means[1]),'R':float(means[0]-means[1]),'draw_values':vals}

def _write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def _write_json(path,obj): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')

def run_p_pair(block_id,p_id,p_inherit,seed,selected_run_id,neutral_run_id,outdir:Path,validation_version='v1.0.0'):
    params=params_for(); affinity=params['motif_affinity_matrix']; nw=params['n_cells']*params['n_seqs']*(params['seq_len']-4)
    init_rng=make_generator(int(seed),'fidelity-initialization'); pop0=init_population(params['n_cells'],params['n_seqs'],params['seq_len'],init_rng); pop_s=pop0.copy(); pop_n=pop0.copy()
    u0=make_generator(int(seed),'fidelity-g0-observation').random(nw); fs0,_,_=observe_with_uniforms(pop_s,params,u0); fn0,_,_=observe_with_uniforms(pop_n,params,u0)
    obs_s=make_generator(int(seed),'fidelity-propagation',str(p_id),'observation'); obs_n=make_generator(int(seed),'fidelity-propagation',str(p_id),'observation')
    rep_s=make_generator(int(seed),'fidelity-propagation',str(p_id),'reproduction'); rep_n=make_generator(int(seed),'fidelity-propagation',str(p_id),'reproduction')
    fs=fs0; fn=fn0
    for g in range(1,N_GENS+1):
        pop_s=reproduce_with_partitioning(pop_s,fs,MU,float(p_inherit),rep_s)
        pop_n=reproduce_with_partitioning(pop_n,np.ones_like(fn),MU,float(p_inherit),rep_n)
        if g==N_GENS:
            ue=make_generator(int(seed),'fidelity-endpoint-observation',str(p_id)).random(nw); fs,_,_=observe_with_uniforms(pop_s,params,ue); fn,_,_=observe_with_uniforms(pop_n,params,ue)
        else:
            us=obs_s.random(nw); un=obs_n.random(nw); fs,_,_=observe_with_uniforms(pop_s,params,us); fn,_,_=observe_with_uniforms(pop_n,params,un)
    cds=c_down_primary(pop_s,affinity)['jsd_bits']; cdn=c_down_primary(pop_n,affinity)['jsd_bits']
    uspec=make_generator(int(seed),'fidelity-specificity-crn',str(p_id)).random((N_SPEC_DRAWS,nw)); rs=specificity(pop_s,params,uspec); rn=specificity(pop_n,params,uspec)
    anc_hash=state_hash(pop0)
    common={'block_id':block_id,'p_id':p_id,'p_inherit':float(p_inherit),'base_seed_uint32':int(seed),'ancestor_hash':anc_hash,'validation_version':validation_version}
    es={**common,'run_id':selected_run_id,'mode':'selected','F0':float(fs0.mean()),'F250':float(fs.mean()),'C_down_g250':float(cds),'native_g250':rs['native_mean'],'reversed_g250':rs['reversed_mean'],'R_g250':float(rs['R']),'population_hash_g250':state_hash(pop_s)}
    en={**common,'run_id':neutral_run_id,'mode':'neutral','F0':float(fn0.mean()),'F250':float(fn.mean()),'C_down_g250':float(cdn),'native_g250':rn['native_mean'],'reversed_g250':rn['reversed_mean'],'R_g250':float(rn['R']),'population_hash_g250':state_hash(pop_n)}
    pair={**common,'F0':float(fs0.mean()),'F250_selected':float(fs.mean()),'F250_neutral':float(fn.mean()),'DeltaF':float(fs.mean()-fn.mean()),'C_selected':float(cds),'C_neutral':float(cdn),'DeltaC_down':float(cds-cdn),'R_selected':float(rs['R']),'R_neutral':float(rn['R']),'DeltaR':float(rs['R']-rn['R'])}
    # Save final states and compact endpoint metrics.
    np.savez_compressed(outdir/'raw'/'states'/f'{selected_run_id}_g250.npz',population=pop_s,base_seed_uint32=np.uint32(seed),p_inherit=float(p_inherit),mode='selected',ancestor_hash=anc_hash)
    np.savez_compressed(outdir/'raw'/'states'/f'{neutral_run_id}_g250.npz',population=pop_n,base_seed_uint32=np.uint32(seed),p_inherit=float(p_inherit),mode='neutral',ancestor_hash=anc_hash)
    _write_csv(outdir/'raw'/'metrics'/f'{selected_run_id}_metrics.csv',[es]); _write_csv(outdir/'raw'/'metrics'/f'{neutral_run_id}_metrics.csv',[en])
    _write_json(outdir/'raw'/'endpoints'/f'{selected_run_id}_endpoint.json',es); _write_json(outdir/'raw'/'endpoints'/f'{neutral_run_id}_endpoint.json',en); _write_json(outdir/'raw'/'endpoints'/f'{block_id}_{p_id}_PAIR.json',pair)
    return pair
