import pathlib,threading,http.server,functools,subprocess,json,os,hashlib,sys
base=pathlib.Path('/tmp/gc-beautify-evidence')
roots={'before':'/tmp/gc-beautify-before','after':'/Users/nickgiulioni/.t3/worktrees/giulioni-com/t3-54c8c056'}
cli='/Users/nickgiulioni/.npm/_npx/0f94ee7615faf582/node_modules/lighthouse/cli/index.js'
chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
for phase,root in roots.items():
 if len(sys.argv)>1 and phase not in sys.argv[1:]:continue
 out=base/phase;out.mkdir(exist_ok=True)
 (out/'lighthouse-source.json').write_text(json.dumps({'sha':subprocess.check_output(['git','-C',root,'rev-parse','HEAD'],text=True).strip(),'stylesheet_sha256':hashlib.sha256((pathlib.Path(root)/'styles.css').read_bytes()).hexdigest()},indent=2))
 handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=root)
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
 for mode in ('mobile','desktop'):
  for name,path in [('home','/'),('career','/career/'),('work','/work/'),('media','/media/')]:
   target=out/f'lighthouse-{name}-{mode}.json'
   args=['node',cli,f'http://127.0.0.1:{server.server_port}{path}','--chrome-flags=--headless --no-sandbox','--only-categories=performance,accessibility,best-practices,seo','--output=json',f'--output-path={target}','--quiet']
   if mode=='desktop':args+=['--preset=desktop']
   print('START',phase,name,mode,flush=True)
   env=os.environ.copy();env['CHROME_PATH']=chrome
   r=subprocess.run(args,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
   (out/f'lighthouse-{name}-{mode}.log').write_text(r.stdout)
   if r.returncode:raise RuntimeError(f'Lighthouse {phase} {name} {mode} exit {r.returncode}: {r.stdout}')
   j=json.loads(target.read_text());print('DONE',phase,name,mode,{k:v['score'] for k,v in j['categories'].items()},'CLS',j['audits']['cumulative-layout-shift']['numericValue'],flush=True)
 server.shutdown();server.server_close()
