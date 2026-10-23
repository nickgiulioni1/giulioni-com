import sys,json,threading,http.server,functools,pathlib,subprocess,hashlib
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
root,phase=sys.argv[1:]; out=pathlib.Path('/tmp/gc-beautify-evidence')/phase; out.mkdir(exist_ok=True)
(out/'source.json').write_text(json.dumps({'sha':subprocess.check_output(['git','-C',root,'rev-parse','HEAD'],text=True).strip(),'status':subprocess.check_output(['git','-C',root,'status','--short'],text=True),'stylesheet_sha256':hashlib.sha256((pathlib.Path(root)/'styles.css').read_bytes()).hexdigest()},indent=2))
if phase=='before':(pathlib.Path('/tmp/gc-beautify-evidence')/'evidence-exit-code.txt').unlink(missing_ok=True)
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=root)
port_file=pathlib.Path('/tmp/gc-beautify-evidence/screenshot-port.txt')
server=http.server.ThreadingHTTPServer(('127.0.0.1',int(port_file.read_text()) if phase=='after' else 0),handler)
if phase=='before':port_file.write_text(str(server.server_port))
threading.Thread(target=server.serve_forever,daemon=True).start()
base=f'http://127.0.0.1:{server.server_port}'
results={}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')
 (out/'browser-version.txt').write_text(browser.version+'\n')
 for width in (1280,375):
  for name,path in [('home','/'),('career','/career/'),('work','/work/'),('media','/media/'),('404','/404.html')]:
   page=browser.new_page(viewport={'width':width,'height':900},device_scale_factor=1,has_touch=width==375)
   origins=set(); errors=[]
   page.on('request',lambda r:origins.add(urlsplit(r.url).scheme+'://'+urlsplit(r.url).netloc))
   page.on('requestfailed',lambda r:errors.append({'url':r.url,'failure':r.failure}))
   page.goto(base+path,wait_until='networkidle')
   page.evaluate('document.fonts.ready')
   page.evaluate('async () => {for (let y=0;y<document.body.scrollHeight;y+=600) {window.scrollTo(0,y); await new Promise(r=>setTimeout(r,60));}window.scrollTo(0,0);}')
   page.screenshot(path=str(out/f'{name}-{width}.png'),full_page=True)
   results[f'{name}-{width}']={'raw_origins':sorted(origins),'origins':sorted('LOCAL' if x==base else x for x in origins),'failed_requests':errors,'overflow':page.evaluate('document.documentElement.scrollWidth > innerWidth'),'fonts':page.evaluate('Array.from(document.fonts, f=>({family:f.family,status:f.status}))')}
   print(phase,name,width,results[f'{name}-{width}'],flush=True)
   if phase=='after':
    results[f'{name}-{width}']['contrast']=page.evaluate(pathlib.Path('/tmp/gc-beautify-evidence/scripts/audit.js').read_text())
    states=[]
    for element in page.locator('a,summary,button').all():
     if not element.is_visible():continue
     element.hover()
     contrast=page.evaluate(pathlib.Path('/tmp/gc-beautify-evidence/scripts/audit.js').read_text())
     page.keyboard.press('Tab')
     element.focus()
     states.append({'text':element.inner_text(),'hover_contrast_failures':contrast['failures'],'outline':element.evaluate("e=>({visible:e.matches(':focus-visible'),width:getComputedStyle(e).outlineWidth,style:getComputedStyle(e).outlineStyle,color:getComputedStyle(e).outlineColor})")})
    results[f'{name}-{width}']['states']=states
    if name=='home':
     page.locator('summary').click()
     results[f'{name}-{width}']['details_open']=page.locator('details').get_attribute('open') is not None
     results[f'{name}-{width}']['details_contrast']=page.evaluate(pathlib.Path('/tmp/gc-beautify-evidence/scripts/audit.js').read_text())
     for element in page.locator('details a').all():
      element.hover()
      contrast=page.evaluate(pathlib.Path('/tmp/gc-beautify-evidence/scripts/audit.js').read_text())
      page.keyboard.press('Tab');element.focus()
      states.append({'text':element.inner_text(),'hover_contrast_failures':contrast['failures'],'outline':element.evaluate("e=>({visible:e.matches(':focus-visible'),width:getComputedStyle(e).outlineWidth,style:getComputedStyle(e).outlineStyle,color:getComputedStyle(e).outlineColor})")})
   if phase=='after' and width==1280:
    results[f'{name}-{width}']['layout_widths']={}
    for check_width in (320,520,700,900):
     page.set_viewport_size({'width':check_width,'height':900})
     results[f'{name}-{width}']['layout_widths'][str(check_width)]=page.evaluate('({overflow:document.documentElement.scrollWidth>innerWidth,width:innerWidth})')
   page.close()
 browser.close()
server.shutdown();server.server_close()
(out/'browser.json').write_text(json.dumps(results,indent=2))
if phase=='before':
 result=subprocess.run([sys.executable,__file__,'/Users/nickgiulioni/.t3/worktrees/giulioni-com/t3-54c8c056','after'])
 if result.returncode:
  (pathlib.Path('/tmp/gc-beautify-evidence')/'evidence-exit-code.txt').write_text(str(result.returncode)+'\n')
  sys.exit(result.returncode)
 print('Screenshot batch complete; starting Lighthouse in the same slot.',flush=True)
 with (pathlib.Path('/tmp/gc-beautify-evidence')/'lighthouse-batch.log').open('w') as log:
  result=subprocess.run([sys.executable,'/tmp/gc-beautify-evidence/scripts/lighthouse-batch.py'],stdout=log,stderr=subprocess.STDOUT)
 (pathlib.Path('/tmp/gc-beautify-evidence')/'evidence-exit-code.txt').write_text(str(result.returncode)+'\n')
 sys.exit(result.returncode)
