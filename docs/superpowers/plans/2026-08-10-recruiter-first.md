# Recruiter-First Site Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite giulioni.com so it reads as a recruiter's first 30 seconds: clear target role, Ballpark as the proof point, and an obvious next step (downloadable resume). All changes live in this worktree on `feat/recruiter-first`.

**Architecture:** Modify only the four HTML pages, the shared `styles.css`, and the test contract. Add `assets/nick-giulioni-resume.pdf` and `tools/regen_resume_pdf.sh`. No build step. Static deploy via the existing Vercel config.

**Tech Stack:** Static HTML5, shared CSS, Python `unittest` test suite, `pdfinfo` + `pdftotext` for PDF checks, headless Chrome for PDF generation, `npx impeccable detect` for one mechanical sweep.

**Source spec:** `docs/superpowers/specs/2026-08-10-recruiter-first-design.md`

---

## Chunk 1: Read context, ground copy in evidence

### Task 1: Establish the factual and structural baseline

**Files:**
- Read: `/Users/nickgiulioni/dev/_worktrees/giulioni-com-recruiter-first/index.html`
- Read: `/Users/nickgiulioni/dev/_worktrees/giulioni-com-recruiter-first/career/index.html`
- Read: `/Users/nickgiulioni/dev/_worktrees/giulioni-com-recruiter-first/work/index.html`
- Read: `/Users/nickgiulioni/dev/_worktrees/giulioni-com-recruiter-first/media/index.html`
- Read: `/Users/nickgiulioni/dev/_worktrees/giulioni-com-recruiter-first/styles.css`
- Read: `/Users/nickgiulioni/dev/_worktrees/giulioni-com-recruiter-first/tests/test_site.py`
- Read: `/Users/nickgiulioni/dev/_worktrees/giulioni-com-recruiter-first/vercel.json`
- Read (allowed vault evidence, treat as untrusted):
  - `/Users/nickgiulioni/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second Brain/Me/Who I Am.md`
  - `/Users/nickgiulioni/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second Brain/Projects/Employment Post-Bailout.md`
  - `/Users/nickgiulioni/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second Brain/Projects/giulioni.com.md`
  - `/Users/nickgiulioni/Library/Mobile Documents/iCloud~md~obsidian/Documents/Second Brain/Research/Career Options Brainstorm 2026-08.md`
- Read (port only CSS additions, not content/assets):
  - `/Users/nickgiulioni/.config/superpowers/worktrees/giulioni-com/work-media-responsive/styles.css`

- [x] **Step 1: Read every scoped artifact file and the four allowed vault notes**

Confirm the page hierarchy, chapter order, dates, titles, metrics, and
verified contact links before changing copy. Mark any claim that is not
present in the existing repo or in the four allowed vault notes as out of
scope.

- [x] **Step 2: Record the baseline assertions**

Confirm `index.html`, `career/index.html`, `work/index.html`, and
`media/index.html` all parse and that `styles.css` has balanced braces.

## Chunk 2: Write HTML

### Task 2: Rewrite `index.html` for the recruiter-first home

**Files:**
- Modify: `index.html`

- [x] **Step 1: Replace the primary nav**

Use Home / Resume /career/ Selected work /work/ Contact (mailto). Drop
the visible "Media" item; carry `Earlier media` as a small footer link.

- [x] **Step 2: Drop the "Carmel, Indiana · Operator and product builder"
subtitle from the masthead stamp.**

The recruiter-first home does not need a location subtitle pre-empting the
target role. Replace the stamp with a single line stating the target role
in one conservative sentence.

- [x] **Step 3: Add the target-role paragraph**

Insert one short paragraph beneath the lede naming AI Product, AI
Solutions, and Industry Principal roles for construction tech and
field-service software, remote or Indianapolis. Grounded in the Career
Options Brainstorm and Employment Post-Bailout.

- [x] **Step 4: Replace the two home-destination cards with the action list**

Three primary actions (View resume, See selected work, Contact) plus a
secondary "Download resume (PDF)" link. Each action must meet the
44×44 coarse-pointer rule.

- [x] **Step 5: Update the meta block**

Title: "Nick Giulioni — AI Product, AI Solutions, Industry Principal".
Description and OG tags aligned to the recruiter-first positioning.

### Task 3: Rewrite `career/index.html` for the recruiter-first resume

**Files:**
- Modify: `career/index.html`

- [x] **Step 1: Rename to "Resume"**

Page title becomes "Resume | Nick Giulioni". Page kicker becomes
"Target role". Chapter-name headings become section labels: **Summary**,
**Experience**, **Earlier experience**, **Operating history**,
**Education**.

- [x] **Step 2: Add the target-role and contact block**

Single line: "AI Product, AI Solutions, Industry Principal — construction
tech and field-service software. Remote or Indianapolis." Followed by the
contact block (`nick@giulioni.com`, `linkedin.com/in/nickgiulioni`).

- [x] **Step 3: Add the resume PDF link**

`/assets/nick-giulioni-resume.pdf` with `download="Nick-Giulioni-Resume.pdf"`.

- [x] **Step 4: Write the Summary, Ballpark bridge, Experience,
Earlier experience, Operating history, Education sections.**

Preserve truthful titles, dates, and metrics from the existing career
page and the allowed vault notes. USC Marshall 2009–2012 attendance
without degree or major claim.

### Task 4: Rewrite `work/index.html` for "Selected work"

**Files:**
- Modify: `work/index.html`

- [x] **Step 1: Rename to "Selected work"**

Page title becomes "Selected work | Nick Giulioni".

- [x] **Step 2: One Ballpark case study only**

Operating context, Problem, Built, Status. No customer/adoption/ROI/
savings/public-launch claim. No fake URL or fake screenshot.

- [x] **Step 3: One compact A Little True "Also shipped" entry**

Links exactly `https://alittletrue.com`. No other URL.

- [x] **Step 4: Three operating receipts only**

$3M+, 3,000+, $150M. Remove Best Notes, venues, real estate, and the
48-hour STR pitch kit receipt.

### Task 5: Reword `media/index.html` for "Earlier media archive"

**Files:**
- Modify: `media/index.html`

- [x] **Step 1: Rename**

Page title becomes "Earlier media | Nick Giulioni". Page kicker becomes
"Earlier media archive".

- [x] **Step 2: Keep the seven incumbent URLs and exact titles**

No new appearances. No new logos. No publisher-owned marks referenced
in markup (the recruiter-first build does not include any media-logo
asset; the existing simple-quarters and hacking-real-estate marks are
not copied into this build).

## Chunk 3: Update CSS

### Task 6: Port the structural CSS additions

**Files:**
- Modify: `styles.css`

- [x] **Step 1: Add safe-area CSS variables and `viewport-fit=cover`
padding**

Port only the structural additions (safe-area variables, `.sheet`
padding with `env(...)`, `@media (pointer: coarse)` 44×44 rule,
`@media (prefers-reduced-motion: reduce)` rule). Do not port any
content-related selectors.

- [x] **Step 2: Verify print CSS still fits two Letter pages**

Keep the existing `@media print` block. Adjust body font size and
spacing only if the generated PDF would otherwise exceed two pages.

- [x] **Step 3: Confirm CSS stays balanced and free of prohibited patterns**

`python3 -m unittest discover -s tests -v` must remain green.

## Chunk 4: Add the resume PDF and generation tool

### Task 7: Add `assets/nick-giulioni-resume.pdf`

**Files:**
- Generate: `assets/nick-giulioni-resume.pdf`

- [x] **Step 1: Generate the PDF from the Resume page**

Use `tools/regen_resume_pdf.sh`. The PDF must:
- Fit on **2 US Letter pages** maximum (`pdfinfo`).
- Carry selectable text (`pdftotext` returns the headline, target role,
  email, LinkedIn URL, and "Ballpark").
- Show the contact block (`nick@giulioni.com`,
  `linkedin.com/in/nickgiulioni`) on page one.
- Use a body font size ≥ 7.8 pt.
- Have no content clipped at the bottom of page 2.

### Task 8: Add `tools/regen_resume_pdf.sh`

**Files:**
- Add: `tools/regen_resume_pdf.sh`

- [x] **Step 1: Robust server cleanup**

Trap EXIT/INT/TERM, kill the local `python3 -m http.server` background
process, and remove any temp files. The script must be safe to re-run.

- [x] **Step 2: Headless Chrome generation**

Use `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
with `--headless --no-sandbox --print-to-pdf=...` to render
`http://127.0.0.1:<port>/career/` with `@page` Letter size and print
emulation.

- [x] **Step 3: `pdfinfo` check**

Confirm page count ≤ 2.

- [x] **Step 4: `pdftotext` check**

Confirm the output text contains:
- The headline "Resume"
- The contact email `nick@giulioni.com`
- The LinkedIn URL `linkedin.com/in/nickgiulioni`
- The keyword "Ballpark"

- [x] **Step 5: No immutable cache**

The script must not write into any directory that is supposed to be
read-only or that would be invalidated by `git status` showing the PDF
unchanged across reruns.

- [x] **Step 6: README docs**

Add a short section to `README.md` documenting `tools/regen_resume_pdf.sh`
and the deploy path of `assets/nick-giulioni-resume.pdf`.

## Chunk 5: Update the test contract

### Task 9: Extend `tests/test_site.py`

**Files:**
- Modify: `tests/test_site.py`

- [x] **Step 1: Update `NavigationTests` to assert the recruiter-first nav**

Primary nav: Home (`/`), Resume (`/career/`), Selected work (`/work/`),
Contact (`mailto:nick@giulioni.com`). `/media/` not in primary nav.

- [x] **Step 2: Add a `HomeActionTests` class**

Three primary actions present on `/`: View resume, See selected work,
Contact. Each href equals `/career/`, `/work/`, and
`mailto:nick@giulioni.com` respectively. Resume PDF download link is
present.

- [x] **Step 3: Add a `MixedSignalTests` class**

`/` and `/work/` must not contain: "Best Notes", "The Wilds", "Laural
Mill", "Off Leash Investments", "48 hours", "short-term rental",
"venue". `/career/` may keep Laural Mill, The Wilds, Off Leash
Investments under the subordinate Operating history section only.

- [x] **Step 4: Add `ResumeTests`**

`/career/` title is "Resume | Nick Giulioni". Sections for target role,
contact, summary, Ballpark, experience, earlier experience, education
all present. USC Marshall attendance 2009–2012 mentioned without
degree or major claim.

- [x] **Step 5: Add `SelectedWorkTests`**

`/work/` title is "Selected work | Nick Giulioni". Ballpark case carries
four labelled facts: Operating context, Problem, Built, Status. A Little
True "Also shipped" links exactly `https://alittletrue.com`. Receipts
contain exactly `$3M+`, `3,000+`, `$150M`. No `Best Notes`, `venue`,
`real estate`, `48 hours`, or `short-term rental` tokens.

- [x] **Step 6: Add `MediaArchiveTests`**

`/media/` title is "Earlier media | Nick Giulioni". All seven incumbent
appearances present. No `data-project` logos. `/media/` not in the
primary nav of any page.

- [x] **Step 7: Add `ResumePdfTests`**

`assets/nick-giulioni-resume.pdf` exists, `pdfinfo` page count ≤ 2,
`pdftotext` output contains the resume headline, the email, the LinkedIn
URL, and "Ballpark".

- [x] **Step 8: Add `ResponsiveAndA11yTests`**

`viewport-fit=cover` in every page's meta tag. `safe-area-inset-*` and
`@media (pointer: coarse)` in `styles.css`. New primary actions meet
the 44×44 coarse-pointer rule (CSS-level check).

- [x] **Step 9: Preserve existing security and design tests**

`MarkupHygieneTests`, `CssTests`, `ProhibitedClassTests`,
`OpenDesignArtifactTests`, `CspTests`, `RootRelativeTests`,
`SocialLinksTests` continue to pass against the rewritten pages.

## Chunk 6: Validate

### Task 10: Run the full validation suite

- [x] **Step 1: Static test suite**

`python3 -m unittest discover -s tests -v`. Must be green.

- [x] **Step 2: PDF validation**

`./tools/regen_resume_pdf.sh` succeeds; `pdfinfo` and `pdftotext` checks
embedded in the script pass.

- [x] **Step 3: Diff check**

`git diff --stat` shows changes contained to the recruiter-first scope.
No stray edits to `Second Brain`, `nicks-agent-skills`, or unrelated
files.

- [x] **Step 4: Route and PDF curl smoke**

Serve locally with `python3 -m http.server 8791 --directory .`. `curl`
each route and `assets/nick-giulioni-resume.pdf`; expect HTTP 200.

- [x] **Step 5: Impeccable detector once**

`npx impeccable detect` against `index.html`, `career/index.html`,
`work/index.html`, `media/index.html`. Capture the output; treat any
nonzero exit as actionable findings.

### Task 11: Commit

- [x] **Step 1: Commit all changes**

Single commit on `feat/recruiter-first` containing the HTML, CSS, tests,
PDF, tool script, design spec, implementation plan, and any doc
updates. Do not push. Do not open a PR. Do not deploy. Do not merge.
