from pathlib import Path
import json, sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]
required=['README.md','requirements.txt','provenance/CAMPAIGN_REPRODUCIBILITY_STATUS_v1.2.0.json','experiments/recovered/model_b/scaffold_strength_dense_22point/scripts/run_strength_production.py','experiments/recovered/catalytic/scaffold_strength_22point/code/run_campaign.py','experiments/recovered/catalytic/transmission_fidelity_18point/scripts/run_catalytic_fidelity_confirmatory.py','experiments/recovered/catalytic/reciprocal_history/preoutcome/run_history_specificity_confirmatory.py','experiments/recovered/lattice/original_prospective_control/scripts/run_confirmatory.py']
for r in required:
    if not (ROOT/r).exists(): errors.append('missing '+r)
# no machine-specific paths in public experiment Python
for p in ROOT.glob('experiments/**/*.py'):
    txt=p.read_text(errors='ignore')
    if '/mnt/data/' in txt: errors.append('public hard-coded path: '+str(p.relative_to(ROOT)))
status=json.loads((ROOT/'provenance/CAMPAIGN_REPRODUCIBILITY_STATUS_v1.2.0.json').read_text())
if status.get('remaining_C_or_D_main_campaigns')!=0: errors.append('status registry still reports C/D campaigns')
print('REPOSITORY STRUCTURE:', 'PASS' if not errors else 'FAIL')
for e in errors: print(' -',e)
sys.exit(1 if errors else 0)
