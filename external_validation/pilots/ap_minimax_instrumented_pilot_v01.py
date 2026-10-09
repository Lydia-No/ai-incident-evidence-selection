"""Frozen controlled fixture v0.1. SELF-AUDITED. No external validation."""
H = ('config', 'dependency', 'permissions')
PROBES = {
 'config_diff': {'cost': 2, 'outcomes': {'config': 'changed', 'dependency': 'unchanged', 'permissions': 'unchanged'}},
 'dependency_lock': {'cost': 1, 'outcomes': {'config': 'stable', 'dependency': 'drift', 'permissions': 'stable'}},
 'access_audit': {'cost': 3, 'outcomes': {'config': 'allowed', 'dependency': 'allowed', 'permissions': 'denied'}},
}
TRUTH = 'permissions'
CASE = {'id':'controlled-benign-001','hypotheses':list(H),'prior':{h:1/3 for h in H},
        'cutoff_observations':['Service failed immediately after routine deployment.'],
        'probes':{p:{'cost':v['cost'],'description':p.replace('_',' ')} for p,v in PROBES.items()}}

def evaluate(selected, truth):
    report={}
    for name,p in selected.items():
        observation=PROBES[p]['outcomes'][truth]
        compatible=[h for h in H if PROBES[p]['outcomes'][h]==observation]
        report[name]={'probe':p,'cost':PROBES[p]['cost'],'compatible_count':len(compatible),
                      'true_state_retained':truth in compatible,'first_probe_discriminates':len(compatible)<len(H),
                      'justified_closure':len(compatible)==1}
    return report
