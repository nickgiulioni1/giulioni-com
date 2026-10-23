from pathlib import Path
import os,subprocess,json,hashlib,shutil,tempfile,struct
root=Path('/tmp/gc-beautify-evidence');repo=Path('/Users/nickgiulioni/.t3/worktrees/giulioni-com/t3-54c8c056')
def git(*args,env=None,cwd=repo,input=None):
 return subprocess.run(['git',*args],cwd=cwd,env=env,input=input,text=True,check=True,stdout=subprocess.PIPE).stdout.strip()
head=git('rev-parse','HEAD');assert git('branch','--show-current')=='t3/site-beautification-pass';assert not git('status','--porcelain')
assert git('diff','--name-only','71c1b57..HEAD')=='styles.css'
summary=json.loads((root/'summary.json').read_text())
for key in ('origin_diffs','contrast_failures','hover_contrast_failures','focus_failures','overflow','intermediate_overflow','protected_files_changed'):assert not summary[key],(key,summary[key])
for entry in summary['lighthouse']:
 before_report=json.loads((root/'before'/f"lighthouse-{entry['page']}-{entry['mode']}.json").read_text())
 after_report=json.loads((root/'after'/f"lighthouse-{entry['page']}-{entry['mode']}.json").read_text())
 assert before_report['environment']['hostUserAgent']==after_report['environment']['hostUserAgent'],'Lighthouse browser version changed'
 for category in ('accessibility','best-practices','seo'):assert entry['after']['scores'][category]==100,(entry['page'],entry['mode'],category)
 assert entry['after']['cls']<=entry['before']['cls']+1e-9,(entry['page'],entry['mode'],'CLS regression')
 if entry['mode']=='mobile':assert entry['after']['scores']['performance']>=entry['before']['scores']['performance'],(entry['page'],'mobile performance regression')
assert (root/'tests-exit-code.txt').read_text().strip()=='0'
assert (root/'evidence-exit-code.txt').read_text().strip()=='0'
protected=json.loads((root/'guardrails-before.json').read_text())
for file,digest in protected['files'].items():assert hashlib.sha256((repo/file).read_bytes()).hexdigest()==digest,file
style_hash=hashlib.sha256((repo/'styles.css').read_bytes()).hexdigest()
for name in ('source.json','lighthouse-source.json'):
 after=json.loads((root/'after'/name).read_text());assert after['sha']==head;assert after['stylesheet_sha256']==style_hash
 before=json.loads((root/'before'/name).read_text());assert before['sha']==git('rev-parse','71c1b57')
assert (root/'before/browser-version.txt').read_text()==(root/'after/browser-version.txt').read_text()
for phase in ('before','after'):
 for name in ('home','career','work','media','404'):
  for width in (1280,375):
   path=root/phase/f'{name}-{width}.png';data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';assert struct.unpack('>I',data[16:20])[0]==width
for width in (1280,375):assert json.loads((root/'after/browser.json').read_text())[f'home-{width}']['details_open']
remote_source=git('ls-remote','--heads','origin','t3/site-beautification-pass');assert remote_source.split()[0]==head
branch='pr-assets/site-beautification';remote=git('ls-remote','--heads','origin',branch)
receipt=root/'assets-commit.txt'
if remote:
 assert receipt.exists() and remote.split()[0]==receipt.read_text().strip(),'Asset branch already exists with an unexpected head'
 existing=receipt.read_text().strip()
 assert json.loads(git('show',existing+':after/source.json'))['sha']==head
 assert git('rev-parse',existing+':summary.json')==git('hash-object',str(root/'summary.json'))
 print('Already published assets:',existing);raise SystemExit(0)
assets=Path(tempfile.mkdtemp(prefix='gc-beautify-assets-'))
for phase in ('before','after'):shutil.copytree(root/phase,assets/phase)
for name in ('README.md','summary.json','contrast-tokens.json','guardrails-before.json','tests.log','tests-exit-code.txt','evidence-exit-code.txt'):shutil.copy2(root/name,assets/name)
(assets/'scripts').mkdir()
for name in ('capture.py','lighthouse-batch.py','audit.js','contrast.py','summarize.py','report.py','publish.py','diagnose-cls.py','final-batch.py','followup-diagnose.py','followup-force-fonts.py'):shutil.copy2(root/'scripts'/name,assets/'scripts'/name)
for name in ('cls-diagnosis.json','cls-diagnosis.log','followup-diagnosis.json','forced-font-diagnosis.json'):
 if (root/name).exists():shutil.copy2(root/name,assets/name)
env=os.environ.copy();env.update(GIT_DIR=git('rev-parse','--absolute-git-dir'),GIT_WORK_TREE=str(assets),GIT_INDEX_FILE=str(assets.parent/(assets.name+'-index')))
git('read-tree','--empty',env=env,cwd=assets);git('add','--all','--force',env=env,cwd=assets);tree=git('write-tree',env=env,cwd=assets)
message='Publish site beautification evidence\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n'
sha=git('commit-tree',tree,env=env,cwd=assets,input=message)
assert not git('show','-s','--format=%P',sha)
git('update-ref','refs/heads/'+branch,sha,'0'*40);receipt.write_text(sha+'\n')
git('-c','pack.threads=1','push','origin','refs/heads/'+branch)
assert git('ls-remote','--heads','origin',branch).split()[0]==sha
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
print('Published orphan assets commit:',sha)
print('Asset staging directory:',assets)
