from pathlib import Path
import subprocess,sys
root=Path('/tmp/gc-beautify-round2')
with (root/'tests.log').open('w') as log:
 result=subprocess.run(['python3','-m','unittest','discover','-s','tests','-v'],stdout=log,stderr=subprocess.STDOUT)
(root/'tests-exit-code.txt').write_text(str(result.returncode)+'\n')
if result.returncode:raise SystemExit(result.returncode)
result=subprocess.run(['python3',str(root/'scripts/capture.py'),'/tmp/gc-beautify-before-r2','before'])
(root/'evidence-exit-code.txt').write_text(str(result.returncode)+'\n')
sys.exit(result.returncode)
