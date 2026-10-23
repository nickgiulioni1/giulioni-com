from pathlib import Path
import os,subprocess,json,hashlib,shutil,tempfile,struct
root=Path('/tmp/gc-beautify-round2');repo=Path('/Users/nickgiulioni/.t3/worktrees/giulioni-com/t3-54c8c056')
def git(*args,env=None,cwd=repo,input=None):
 return subprocess.run(['git',*args],cwd=cwd,env=env,input=input,text=True,check=True,stdout=subprocess.PIPE).stdout.strip()
head=git('rev-parse','HEAD');assert git('branch','--show-current')=='t3/site-beautification-pass';assert not git('status','--porcelain')
assert git('diff','--name-only','8ede86d..HEAD')=='styles.css'
summary=json.loads((root/'summary.json').read_text())
for key in ('origin_diffs','contrast_failures','hover_contrast_failures','focus_failures','overflow','intermediate_overflow','protected_files_changed'):assert not summary[key],(key,summary[key])
for entry in summary['lighthouse']:
 before_report=json.loads((root/'before'/f"lighthouse-{entry['page']}-{entry['mode']}.json").read_text())
 after_report=json.loads((root/'after'/f"lighthouse-{entry['page']}-{entry['mode']}.json").read_text())
 assert before_report['environment']['hostUserAgent']==after_report['environment']['hostUserAgent'],'Lighthouse browser version changed'
 for category in ('accessibility','best-practices','seo'):assert entry['after']['scores'][category]==100,(entry['page'],entry['mode'],category)
 assert entry['after']['cls']<=entry['before']['cls'],(entry['page'],entry['mode'],'CLS regression')
 if entry['mode']=='mobile':assert entry['after']['scores']['performance']>=entry['before']['scores']['performance'],(entry['page'],'mobile performance regression')
assert (root/'tests-exit-code.txt').read_text().strip()=='0'
assert (root/'evidence-exit-code.txt').read_text().strip()=='0'
protected=json.loads((root/'guardrails-before.json').read_text())
for file,digest in protected['files'].items():assert hashlib.sha256((repo/file).read_bytes()).hexdigest()==digest,file
style_hash=hashlib.sha256((repo/'styles.css').read_bytes()).hexdigest()
for name in ('source.json','lighthouse-source.json'):
 after=json.loads((root/'after'/name).read_text());assert after['sha']==head;assert after['stylesheet_sha256']==style_hash
 before=json.loads((root/'before'/name).read_text());assert before['sha']==git('rev-parse','8ede86d')
assert (root/'before/browser-version.txt').read_text()==(root/'after/browser-version.txt').read_text()
for phase in ('before','after'):
 for name in ('home','career','work','media','404'):
  for width in (1280,375):
   path=root/phase/f'{name}-{width}.png';data=path.read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';assert struct.unpack('>I',data[16:20])[0]==width
for width in (1280,375):assert json.loads((root/'after/browser.json').read_text())[f'home-{width}']['details_open']
remote_source=git('ls-remote','--heads','origin','t3/site-beautification-pass');assert remote_source.split()[0]==head
branch='pr-assets/site-beautification'
previous='e614fb8b9faa308519778430e28b16a6f08e7ee0'
remote=git('ls-remote','--heads','origin',branch)
assert remote.split()[0]==previous,'Asset branch changed; do not overwrite it'
assert git('rev-parse','refs/heads/'+branch)==previous
receipt=root/'assets-commit.txt'
for phase in ('before','after'):
 for page,result in json.loads((root/phase/'browser.json').read_text()).items():
  assert len(result['raw_origins'])==1 and result['raw_origins'][0].startswith('http://127.0.0.1:'),(phase,page,'third-party request')
  assert not result['failed_requests'],(phase,page,'failed request')
assert 'font-size-adjust:' not in (repo/'styles.css').read_text()
assert 'Ran 78 tests' in (root/'tests.log').read_text()
assets=Path(tempfile.mkdtemp(prefix='gc-beautify-assets-'))
for phase in ('before','after'):shutil.copytree(root/phase,assets/phase)
for name in ('README.md','summary.json','contrast-tokens.json','guardrails-before.json','tests.log','tests-exit-code.txt','evidence-exit-code.txt','source-cleanup.json'):shutil.copy2(root/name,assets/name)
(assets/'scripts').mkdir()
for name in ('capture.py','lighthouse-batch.py','audit.js','contrast.py','summarize.py','report.py','publish.py','batch.py'):
 shutil.copy2(root/'scripts'/name,assets/'scripts'/name)
env=os.environ.copy();env.update(GIT_DIR=git('rev-parse','--absolute-git-dir'),GIT_WORK_TREE=str(assets),GIT_INDEX_FILE=str(assets.parent/(assets.name+'-index')))
git('read-tree','--empty',env=env,cwd=assets);git('add','--all','--force',env=env,cwd=assets);tree=git('write-tree',env=env,cwd=assets)
message='Publish refreshed site beautification evidence\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\n'
sha=git('commit-tree',tree,'-p',previous,env=env,cwd=assets,input=message)
assert git('show','-s','--format=%P',sha)==previous
git('update-ref','refs/heads/'+branch,sha,previous);receipt.write_text(sha+'\n')
git('-c','pack.threads=1','push','origin','refs/heads/'+branch)
assert git('ls-remote','--heads','origin',branch).split()[0]==sha
assert git('rev-parse','HEAD')==head and not git('status','--porcelain')
print('Published orphan assets commit:',sha)
print('Asset staging directory:',assets)
