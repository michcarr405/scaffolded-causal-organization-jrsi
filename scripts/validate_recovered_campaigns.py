from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def run(name,cmd,cwd=None):
    p=subprocess.run(cmd,cwd=cwd or ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    print(f'[{name}]', 'PASS' if p.returncode==0 else 'FAIL')
    print(p.stdout[-3000:])
    checks.append((name,p.returncode)); return p
# Dense Model B has native dry-run and should report 660 pairs / 1320 runs.
p=run('model_b_dense22_dry_run',[sys.executable,str(ROOT/'experiments/recovered/model_b/scaffold_strength_dense_22point/scripts/run_strength_production.py'),'--dry-run'])
if p.returncode==0 and ('660' not in p.stdout or '1320' not in p.stdout): checks.append(('model_b_dense22_expected_counts',1))
# Syntax/import compile of all normalized recovered runners.
files=[
 ROOT/'experiments/recovered/catalytic/scaffold_strength_22point/code/run_campaign.py',
 ROOT/'experiments/recovered/catalytic/transmission_fidelity_18point/scripts/run_catalytic_fidelity_confirmatory.py',
 ROOT/'experiments/recovered/catalytic/reciprocal_history/preoutcome/run_history_specificity_confirmatory.py',
 ROOT/'experiments/recovered/lattice/original_prospective_control/scripts/run_confirmatory.py']
run('recovered_compile',[sys.executable,'-m','py_compile',*map(str,files)])
fail=[x for x in checks if x[1]]
print('RECOVERED CAMPAIGN VALIDATION:', 'PASS' if not fail else 'FAIL')
for x in fail: print(' -',x)
sys.exit(1 if fail else 0)
