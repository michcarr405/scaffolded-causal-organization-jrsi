from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_no_mnt_data_in_public_python():
    for p in ROOT.glob('experiments/**/*.py'): assert '/mnt/data/' not in p.read_text(errors='ignore'), p
def test_recovery_status_closed():
    import json
    d=json.loads((ROOT/'provenance/CAMPAIGN_REPRODUCIBILITY_STATUS_v1.2.0.json').read_text()); assert d['remaining_C_or_D_main_campaigns']==0
def test_recovered_originals_exist():
    assert (ROOT/'provenance/original_campaigns/recovered/model_b/scaffold_strength_dense_22point').exists()
    assert (ROOT/'provenance/original_campaigns/recovered/catalytic/scaffold_strength_22point').exists()
    assert (ROOT/'provenance/original_campaigns/recovered/catalytic/transmission_fidelity_18point').exists()
    assert (ROOT/'provenance/original_campaigns/recovered/catalytic/reciprocal_history').exists()
    assert (ROOT/'provenance/original_campaigns/recovered/lattice/original_prospective_control').exists()
