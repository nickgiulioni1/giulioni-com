from pathlib import Path
import subprocess,sys
root=Path('/tmp/gc-beautify-evidence')
commands=[['python3',str(root/'scripts/capture.py'),'/Users/nickgiulioni/.t3/worktrees/giulioni-com/t3-54c8c056','after'],['python3',str(root/'scripts/lighthouse-batch.py'),'after'],['python3',str(root/'scripts/followup-force-fonts.py')]]
for cmd in commands:
 result=subprocess.run(cmd)
 if result.returncode:break
(root/'evidence-exit-code.txt').write_text(str(result.returncode)+'\n')
sys.exit(result.returncode)
