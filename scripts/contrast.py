import json,re
from pathlib import Path
css=Path('styles.css').read_text()
tokens=dict(re.findall(r'--([\w-]+):\s*(#[0-9a-fA-F]{6})',css))
def rgb(h):return [int(h[i:i+2],16)/255 for i in (1,3,5)]
def luminance(c):return sum(v*w for v,w in zip([v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c],[.2126,.7152,.0722]))
def ratio(a,b):
 a,b=sorted((luminance(a),luminance(b)));return (b+.05)/(a+.05)
records=[]
for foreground,background in [('ink','paper'),('ink','paper-band'),('ink-soft','paper'),('ink-soft','paper-band'),('ink-mute','paper'),('ink-mute','paper-band'),('rust-text','paper'),('rust-text','paper-band'),('paper','dark-band'),('paper','rust'),('ink','rust-on-dark'),('ink','paper'),('rust-on-dark','dark-band')]:
 value=ratio(rgb(tokens[foreground]),rgb(tokens[background]));records.append({'foreground':foreground,'background':background,'ratio':round(value,3),'minimum':4.5})
for alpha in (.68,.8):
 dark=rgb(tokens['dark-band']);paper=rgb(tokens['paper']);mixed=[alpha*a+(1-alpha)*b for a,b in zip(paper,dark)]
 records.append({'foreground':f'paper at {alpha}','background':'dark-band','ratio':round(ratio(mixed,dark),3),'minimum':4.5})
assert all(r['ratio']>=r['minimum'] for r in records)
Path('/tmp/gc-beautify-round2/contrast-tokens.json').write_text(json.dumps(records,indent=2))
print('PASS:',len(records),'text/background combinations; minimum contrast',min(r['ratio'] for r in records))
