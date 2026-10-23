import pathlib,json,threading,http.server,functools,time
from playwright.sync_api import sync_playwright
base=pathlib.Path('/tmp/gc-beautify-evidence')
repo='/Users/nickgiulioni/.t3/worktrees/giulioni-com/t3-54c8c056'
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=repo))
threading.Thread(target=server.serve_forever,daemon=True).start()
styles={'before':pathlib.Path('/tmp/gc-beautify-before/styles.css').read_text(),'after':pathlib.Path(repo+'/styles.css').read_text()}
variants={'current':'', 'native-sans':'@media(max-width:520px){body{font-size-adjust:.51}}', 'body-none':'@media(max-width:520px){body{font-size-adjust:none}}', 'deck-native':'.page-deck{font-size-adjust:.51}', 'deck-more-leading':'.page-deck{line-height:1.7}', 'summary-36rem':'.resume-section>p{max-width:36rem}', 'summary-38rem':'.resume-section>p{max-width:38rem}', 'summary-40rem':'.resume-section>p{max-width:40rem}', 'summary-42rem':'.resume-section>p{max-width:42rem}', 'desktop-deck': '@media(min-width:521px){.page-deck{font-size:1.125rem;max-width:58ch}}', 'summary-none':'.resume-section>p{font-size-adjust:none}', 'summary-native':'.resume-section>p{font-size-adjust:.51}', 'article-native':'.media-entry{font-size-adjust:.51}.media-entry .episode-title{font-size-adjust:.4405}', 'native-metrics':'@media(max-width:520px){body{font-size-adjust:.51}h1,h2,.page-title,.site-name,.media-entry .episode-title{font-size-adjust:.4405}}', 'title-baseline':'@media(max-width:520px){.page-title{font-size:2rem;font-size-adjust:none}}'}

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
    state={'released':False,'routes':[]}
    def hold_font(route):
     if state['released']:route.continue_()
     else:state['routes'].append(route)
    page.route('https://fonts.gstatic.com/**',hold_font)
    page.add_init_script('''window.shifts=[];new PerformanceObserver(list=>{for(const e of list.getEntries()){if(!e.hadRecentInput)window.shifts.push({value:e.value,sources:e.sources.map(s=>({node:s.node?.className,previous:s.previousRect,current:s.currentRect}))})}}).observe({type:'layout-shift',buffered:true});''')
    page.goto(f'http://127.0.0.1:{server.server_port}{path}',wait_until='domcontentloaded')
    page.wait_for_function('document.fonts.size>0 && Array.from(document.fonts).some(f=>f.status==="loading")')
    page.wait_for_timeout(500)
    page.evaluate('async()=>{await new Promise(requestAnimationFrame);await new Promise(requestAnimationFrame)}')
    fallback=page.evaluate('Array.from(document.fonts,f=>({family:f.family,status:f.status}))')
    state['released']=True
    for route in state['routes']:route.continue_()
    page.evaluate('document.fonts.ready');page.wait_for_timeout(200)
    r={'width':width,'page':name,'variant':variant,'fallback_fonts':fallback,'shifts':page.evaluate('window.shifts')};r['cls']=sum(x['value'] for x in r['shifts']);r['font_metrics']=page.evaluate('''() => {const c=document.createElement('canvas').getContext('2d');return Object.fromEntries(['Instrument Sans','Helvetica Neue','Newsreader','Georgia'].map(f=>{c.font='1000px "'+f+'"';const m=c.measureText('x');return [f,{xHeight:m.actualBoundingBoxAscent/1000,width:m.width/1000}]}))}''');results.append(r)
    print(width,name,variant,r['cls'],flush=True);page.close()
 b.close()
server.shutdown();server.server_close()
(base/'forced-font-diagnosis.json').write_text(json.dumps(results,indent=2))
