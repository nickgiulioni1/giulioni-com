import pathlib,json,threading,http.server,functools,time
from playwright.sync_api import sync_playwright
base=pathlib.Path('/tmp/gc-beautify-evidence')
repo='/Users/nickgiulioni/.t3/worktrees/giulioni-com/t3-54c8c056'
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=repo))
threading.Thread(target=server.serve_forever,daemon=True).start()
styles={'before':pathlib.Path('/tmp/gc-beautify-before/styles.css').read_text(),'after':pathlib.Path(repo+'/styles.css').read_text()}
variants={'current':'','wrap':'h1,h2{text-wrap:wrap}','heading-line':'h1{line-height:1.3}','heading-adjust':'h1{font-size-adjust:.5}','body-adjust':'body{font-size-adjust:.5}h1,h2,.site-name{font-size-adjust:.46}','inline-block':'h1{display:flow-root}h1::first-line{line-height:1.1}','fixed-heading':'h1{contain:paint}', 'baseline-type':'.site-name{font-size:1.25rem}.hero-lede{font-size:clamp(2rem,4.5vw,3.25rem);line-height:1.15;max-width:none}.page-title{font-size:clamp(2rem,5vw,3.5rem)}.page-deck{font-size:1.1rem;max-width:60ch}@media(max-width:520px){.hero-lede{font-size:clamp(1.625rem,5vw,2rem)}}', 'text-box':'h1{text-box:trim-both cap alphabetic}', 'center-cap':'h1{text-box:trim-both cap alphabetic;align-content:center;min-height:1.1em}.hero-lede{min-height:2.16em}@media(max-width:520px){.hero-lede{min-height:3.24em}}', 'modest-type':'.page-title{font-size:clamp(2.5rem,5.5vw,4rem)}@media(max-width:520px){.hero-lede{font-size:2rem}}', 'modest-type-wrap':'.page-title{font-size:clamp(2.5rem,5.5vw,4rem)}h1,h2{text-wrap:wrap}@media(max-width:520px){.hero-lede{font-size:2rem}}'}
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 for width,height in [(412,823),(1350,940)]:
  for name,path in [('home','/'),('career','/career/')]:
   for variant,extra in [('before','')]+list(variants.items()):
    page=b.new_page(viewport={'width':width,'height':height},device_scale_factor=1.75 if width==412 else 1,is_mobile=width==412,has_touch=width==412)
    page.route('**/styles.css',lambda route:route.fulfill(body=styles['before' if variant=='before' else 'after']+extra,content_type='text/css'))
    page.route('https://fonts.gstatic.com/**',lambda route:(time.sleep(.25),route.continue_()))
    page.add_init_script('''window.shifts=[];new PerformanceObserver(list=>{for(const e of list.getEntries()){if(!e.hadRecentInput)window.shifts.push({value:e.value,sources:e.sources.map(s=>({node:s.node?.className,previous:s.previousRect,current:s.currentRect}))})}}).observe({type:'layout-shift',buffered:true});''')
    page.goto(f'http://127.0.0.1:{server.server_port}{path}',wait_until='networkidle');page.evaluate('document.fonts.ready');page.wait_for_timeout(150)
    r={'width':width,'page':name,'variant':variant,'shifts':page.evaluate('window.shifts')};r['cls']=sum(x['value'] for x in r['shifts']);results.append(r)
    print(width,name,variant,r['cls'],flush=True);page.close()
 b.close()
server.shutdown();server.server_close()
(base/'cls-diagnosis.json').write_text(json.dumps(results,indent=2))
