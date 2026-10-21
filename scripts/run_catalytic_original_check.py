from pathlib import Path
import subprocess,os,sys,hashlib,shutil
ROOT=Path(__file__).resolve().parents[1]
orig=list((ROOT/'provenance/original_campaigns/canonical/catalytic/original_prospective').rglob('run_confirmatory.py'))[0].parent
ref=orig
out=ROOT/'work/catalytic_original_check'
if out.exists(): shutil.rmtree(out)
out.mkdir(parents=True)
env=os.environ.copy(); env['SCO_OUTPUT_DIR']=str(out)
p=subprocess.run([sys.executable,str(ROOT/'experiments/catalytic/original_prospective/run.py')],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
print(p.stdout[-3000:])
if p.returncode: raise SystemExit(p.returncode)
files=['CONFIRM_BLOCK_RESULTS.csv','CONFIRM_DIRECTION_RESULTS.csv','CONFIRM_DIRECTION_SUMMARY.csv','CONFIRM_CATALYTIC_MATRIX.csv','CONFIRM_STATS.json','CONFIRM_ENDPOINT_STATES.npz']; bad=[]
for f in files:
    a=out/f; b=ref/f; ok=hashlib.sha256(a.read_bytes()).hexdigest()==hashlib.sha256(b.read_bytes()).hexdigest(); print(('PASS' if ok else 'FAIL'),f); bad += ([] if ok else [f])
raise SystemExit(1 if bad else 0)
