# giulioni.com

Personal site for Nick Giulioni. Static — no build step.

## Local preview

```sh
python3 -m http.server 8791 --directory .
```

Open `http://127.0.0.1:8791/`, `http://127.0.0.1:8791/career/`,
`http://127.0.0.1:8791/work/`, or `http://127.0.0.1:8791/media/`.

## Deploy subset

| Path | Role |
|---|---|
| `index.html` | Home page (recruiter-first thesis + target role + primary actions) |
| `career/index.html` | Resume page (target role, summary, Ballpark bridge, experience, education) |
| `work/index.html` | Selected work page (Ballpark case + Also shipped + receipts) |
| `media/index.html` | Earlier media archive (seven incumbent podcast appearances) |
| `styles.css` | Connected-letterhead design system |
| `assets/portrait-nick.jpg` | Hero plate |
| `assets/nick-giulioni-resume.pdf` | Downloadable resume (PDF) |
| `vercel.json` | Security headers (CSP allows Google Fonts) |

## Regenerating the resume PDF

The resume PDF is generated from `career/index.html` using headless Chrome.
It must stay at two Letter pages with selectable text and the required
contact tokens.

```sh
./tools/regen_resume_pdf.sh
```

The script:

1. Picks a free local port.
2. Starts `python3 -m http.server` against the repo root on that port.
3. Waits for the server to respond.
4. Renders `/career/` with `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
   `--headless --print-to-pdf=...` and `@page letter` from the existing
   print CSS.
5. Validates the PDF: `pdfinfo` page count `<= 2`, `pdftotext` returns
   `resume`, `nick@giulioni.com`, `linkedin.com/in/nickgiulioni`, and
   `ballpark`.
6. Moves the temp PDF to `assets/nick-giulioni-resume.pdf`.
7. Tears the local server down on `EXIT` / `INT` / `TERM`.

Override the Chrome binary, `pdfinfo`, or `pdftotext` paths via
`CHROME_BIN`, `PDFINFO_BIN`, `PDFTOTEXT_BIN`. Override the port via
`RESUME_PDF_PORT`. No immutable cache is written; the script can be re-run
freely.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

Tests cover the recruiter-first nav, primary actions, mixed-signal
removal, the Resume page sections, the Selected work case study, the
Earlier media archive, the resume PDF, the responsive / safe-area /
coarse-pointer / reduced-motion CSS, the print body size floor, CSP,
markup hygiene, balanced CSS braces, root-relative references, and the
absence of prohibited design patterns.

## Provenance

Recruiter-first rewrite on `feat/recruiter-first`, 2026-08-10. CSS additions
(viewport-fit, safe-area, coarse-pointer 44 px, reduced-motion) ported
from the parallel `work-media-responsive` worktree. No content or media
assets copied from that worktree.
