from annotations import CASES,TOKEN_OUTCOMES
from formation_tests import FORMATIONS
covered={r['Entry_ID'] for r in FORMATIONS if r['Language_ID']=='Telugu'}
for c in CASES:
 if c['entry_id'] in covered or 'Telugu' not in c['outcomes']:continue
 top,forms,note=c['outcomes']['Telugu'];ws=[w for w in forms.split('|') if TOKEN_OUTCOMES.get((c['entry_id'],'Telugu',w),top)=='D']
 if not ws:continue
 print(c['entry_id'],c['concept'],c['reconstruction'],' || '.join(ws))
 print(c['input_support']);print(c['derivation']);print()
