import pathlib,json,threading,http.server,functools,time
from playwright.sync_api import sync_playwright
base=pathlib.Path('/tmp/gc-beautify-evidence')
repo='/Users/nickgiulioni/.t3/worktrees/giulioni-com/t3-54c8c056'
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=repo))
threading.Thread(target=server.serve_forever,daemon=True).start()
styles={'before':pathlib.Path('/tmp/gc-beautify-before/styles.css').read_text(),'after':pathlib.Path(repo+'/styles.css').read_text()}
variants={'current':'','hero-wrap':'.hero-lede{text-wrap:wrap}','deck-baseline':'.page-deck{font-size:1.1rem;max-width:60ch;font-size-adjust:none}', 'deck-unadjusted':'.page-deck{font-size-adjust:none}', 'deck-small':'.page-deck{font-size:1.1rem;max-width:60ch}','target-adjust':'.hero-targeting{font-size-adjust:.5}', 'target-width':'.hero-targeting{max-width:36rem}', 'target-both':'.hero-targeting{font-size-adjust:.5;max-width:36rem}', 'body-adjust-hero-none':'body{font-size-adjust:.5}.hero-lede{font-size-adjust:none}', 'body-adjust-hero-small':'body{font-size-adjust:.5}.hero-lede{font-size-adjust:.46}', 'mobile-serif-none':'@media(max-width:520px){.media-entry .episode-title{font-size-adjust:none}}', 'mobile-serif':'@media(max-width:520px){.media-entry .episode-title,.closing-cta p,.receipt strong{font-size-adjust:.46}}', 'mobile-baseline':'@media(max-width:520px){body,h1,h2,.page-title,.site-name{font-size-adjust:none}.page-title{font-size:2rem}.hero-lede{font-size:clamp(1.625rem,5vw,2rem)}}'}
failed=[]
for name in ('home','career','work','media'):
 for mode in ('mobile','desktop'):
  b=json.loads((base/'before'/f'lighthouse-{name}-{mode}.json').read_text())
  a=json.loads((base/'after'/f'lighthouse-{name}-{mode}.json').read_text())
  if a['audits']['cumulative-layout-shift']['numericValue']>b['audits']['cumulative-layout-shift']['numericValue']+1e-9:failed.append((name,mode))

if not failed:
 server.shutdown();server.server_close();print('No CLS regression; no follow-up browser work needed.',flush=True);raise SystemExit(0)
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 for width,height in [(412,823),(1350,940)]:
  for name,path in [('home','/'),('career','/career/'),('work','/work/'),('media','/media/')]:
   if (name,'mobile' if width==412 else 'desktop') not in failed:continue
   for variant,extra in [('before','')]+list(variants.items()):
    page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1.75 if width==412 else 1,is_mobile=width==412,has_touch=width==412)
    page.route('**/styles.css',lambda route:route.fulfill(body=styles['before' if variant=='before' else 'after']+extra,content_type='text/css'))
    page.route('https://fonts.gstatic.com/**',lambda route:(time.sleep(.25),route.continue_()))
    page.add_init_script('''window.shifts=[];new PerformanceObserver(list=>{for(const e of list.getEntries()){if(!e.hadRecentInput)window.shifts.push({value:e.value,sources:e.sources.map(s=>({node:s.node?.className,previous:s.previousRect,current:s.currentRect}))})}}).observe({type:'layout-shift',buffered:true});''')
    page.goto(f'http://127.0.0.1:{server.server_port}{path}',wait_until='networkidle');page.evaluate('document.fonts.ready');page.wait_for_timeout(150)
    r={'width':width,'page':name,'variant':variant,'shifts':page.evaluate('window.shifts')};r['cls']=sum(x['value'] for x in r['shifts']);r['font_metrics']=page.evaluate('''() => {const c=document.createElement('canvas').getContext('2d');return Object.fromEntries(['Instrument Sans','Helvetica Neue','Newsreader','Georgia'].map(f=>{c.font='1000px "'+f+'"';const m=c.measureText('x');return [f,{xHeight:m.actualBoundingBoxAscent/1000,width:m.width/1000}]}))}''');results.append(r)
    print(width,name,variant,r['cls'],flush=True);page.close()
 b.close()
server.shutdown();server.server_close()
(base/'followup-diagnosis.json').write_text(json.dumps(results,indent=2))
