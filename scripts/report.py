from pathlib import Path
import json,subprocess,importlib.metadata
root=Path('/tmp/gc-beautify-evidence');summary=json.loads((root/'summary.json').read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
lines=[f'# Site beautification evidence\n\nSource head: `{head}`. Baseline: `71c1b57`.\n',
'- Stronger serif headings and consistent section spacing across all five pages.\n- Alternating track record rows, wider case facts, and larger receipt figures.\n- Two-column media archive with larger episode titles; one column on phones.\n- Underlined current navigation and footer links, larger buttons, and contrasting keyboard focus.\n- Darker rust text and corrected product-button hover contrast while retaining the existing palette.\n',
'## Screenshots\n\nFull-page PNGs. Desktop viewport 1280 × 900; phone viewport 375 × 900. Device scale factor 1; touch enabled at 375px.\n\n| Page | Before 1280 | After 1280 | Before 375 | After 375 |\n|---|---|---|---|---|']
for name,label in [('home','/'),('career','/career/'),('work','/work/'),('media','/media/'),('404','/404.html')]:
 lines.append('| '+label+' | '+' | '.join(f'[{phase} {width}]({phase}/{name}-{width}.png)' for width in (1280,375) for phase in ('before','after'))+' |')
lines+=['\n## Lighthouse\n\nLocal static-server runs, not production measurements. The initial c78df86 after-results and corrections at 7045c34 and 4eacb98 failed the strict CLS gate. Their reports and screenshots are preserved under after/initial-c78df86, after/fix1-7045c34, and after/fix2-4eacb98. Each new source correction was committed before its combined screenshot and Lighthouse hold. The current after-results use the committed typography correction at the source head above. P/A/B/S = performance/accessibility/best-practices/SEO. Scores out of 100.\n\n| Page | Mobile before → after P/A/B/S; CLS | Desktop before → after P/A/B/S; CLS |\n|---|---|---|']
for name in ('home','career','work','media'):
 cells=[]
 for mode in ('mobile','desktop'):
  entry=next(x for x in summary['lighthouse'] if x['page']==name and x['mode']==mode)
  def format_result(phase):
   data=entry[phase];scores=data['scores'];return '/'.join(str(scores[k]) for k in ('performance','accessibility','best-practices','seo'))+f"; CLS {data['cls']:.8f}"
  cells.append(format_result('before')+' → '+format_result('after'))
 lines.append('| '+name+' | '+' | '.join(cells)+' |')
lines+=['\n## Network, accessibility, and scope\n',f"Origin differences: {len(summary['origin_diffs'])}. Computed text contrast failures: {len(summary['contrast_failures'])}. Hover contrast failures: {len(summary['hover_contrast_failures'])}. Keyboard focus failures: {len(summary['focus_failures'])}. Overflow at screenshot widths: {len(summary['overflow'])}. Protected files changed: {len(summary['protected_files_changed'])}.\n",'\n| Page | Before and after request origins |\n|---|---|']
for name in ('home','career','work','media','404'):
 lines.append('| '+name+' | '+', '.join(summary['origins'][name+'-1280'])+' |')
lines+=['\nAll HTML, font links, fetch priorities, tests, and all 14 sanitized demo-image variants are unchanged. Only styles.css changed in the implementation branch.\n',f"\nChrome: {(root/'after/browser-version.txt').read_text().strip()}. Python Playwright: {importlib.metadata.version('playwright')}. Lighthouse: {summary['lighthouse'][0]['after']['version']}.\n",'\n## Unit tests\n\n```text\n'+'\n'.join((root/'tests.log').read_text().splitlines()[-5:])+'\nExit code: 0\n```\n','\nNot run: production Lighthouse, deployed browser checks, independent PR review. No PR opened or merge performed.\n']
(root/'README.md').write_text('\n'.join(lines))
print('Evidence report written.')
