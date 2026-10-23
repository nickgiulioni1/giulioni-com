from pathlib import Path
import json,hashlib,subprocess
root=Path('/tmp/gc-beautify-evidence')
before=json.loads((root/'before/browser.json').read_text());after=json.loads((root/'after/browser.json').read_text())
origin_diffs={k:{'before':before[k]['raw_origins'],'after':v['raw_origins']} for k,v in after.items() if before[k]['raw_origins']!=v['raw_origins']}
contrast=[{'page':k,**f} for k,v in after.items() for f in v['contrast']['failures']+v.get('details_contrast',{}).get('failures',[])]
hover=[{'page':k,'control':state['text'],**f} for k,v in after.items() for state in v['states'] for f in state['hover_contrast_failures']]
focus=[{'page':k,**state} for k,v in after.items() for state in v['states'] if not state['outline']['visible'] or state['outline']['style']=='none' or float(state['outline']['width'].replace('px',''))<2]
guards=json.loads((root/'guardrails-before.json').read_text())
changed=[f for f,h in guards['files'].items() if hashlib.sha256(Path(f).read_bytes()).hexdigest()!=h]
summary={'origin_diffs':origin_diffs,'origins':{k:v['raw_origins'] for k,v in after.items()},'contrast_failures':contrast,'hover_contrast_failures':hover,'focus_failures':focus,'overflow':[k for k,v in after.items() if v['overflow']],'intermediate_overflow':[k+'-'+w for k,v in after.items() for w,result in v.get('layout_widths',{}).items() if result['overflow']],'protected_files_changed':changed,'lighthouse':[]}
for mode in ('mobile','desktop'):
 for name in ('home','career','work','media'):
  pair={}
  for phase in ('before','after'):
   j=json.loads((root/phase/f'lighthouse-{name}-{mode}.json').read_text())
   pair[phase]={'scores':{k:round(v['score']*100) for k,v in j['categories'].items()},'cls':j['audits']['cumulative-layout-shift']['numericValue'],'version':j['lighthouseVersion']}
  summary['lighthouse'].append({'page':name,'mode':mode,**pair})
(root/'summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
