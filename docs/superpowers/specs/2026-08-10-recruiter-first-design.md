# Recruiter-First Site Direction

**Status:** Owner-approved recruiter-first rewrite, 2026-08-10
**Scope:** `/`, `/career/`, `/work/`, `/media/`, plus `assets/nick-giulioni-resume.pdf`
**Design authority:** Preserve the connected-letterhead system in `styles.css`.

## Objective

Make the site read as a recruiter's first 30 seconds on Nick Giulioni: a single
clear target role, one proof point (Ballpark), and one obvious next step
(downloadable resume, email). Remove mixed signals (Best Notes, venues, real
estate, 48-hour STR, "operator and product builder" subtitle) and remove every
content the existing letterhead design was already carrying as decoration rather
than as evidence a recruiter needs.

## Primary nav

```
Home /              — operator thesis + target role
Resume /career/     — recruiter-ready printable resume + PDF
Selected work /work/— Ballpark case study + receipts
Contact             — mailto:nick@giulioni.com (visible in nav)
```

`/media/` keeps its directory and seven incumbent URLs but is **not** in the
primary nav. A small "Earlier media" link in the page footer or colophon carries
it. `/services/` is out of scope for this build.

## Home

- Keep the lede "I'm an operator who builds his own tools."
- Drop the "Carmel, Indiana · Operator and product builder" subtitle (it
  pre-empts the target role with a location label a recruiter doesn't need in
  the first viewport).
- Below the lede: a single conservative target-role paragraph naming
  **AI Product, AI Solutions, and Industry Principal roles** for
  **construction tech and field-service software**, remote or Indianapolis.
  This text is grounded in `Research/Career Options Brainstorm 2026-08.md`
  (top consensus W-2 lane) and in
  `Projects/Employment Post-Bailout.md` (analogues: Procore, Buildertrend,
  ServiceTitan, Jobber, Housecall Pro).
- Three primary actions, in this order:
  - **View resume** → `/career/`
  - **See selected work** → `/work/`
  - **Contact** → `mailto:nick@giulioni.com`
- Secondary action: **Download resume (PDF)** → `/assets/nick-giulioni-resume.pdf`
- Drop the "Career / What I'm Working On" two-destination cards. The
  recruiter-first design replaces them with the action list above.

## Resume (was /career/)

Page title becomes **"Resume"**. Sections, in order:

1. **Target role** — single line: AI Product, AI Solutions, Industry
   Principal — construction tech and field-service software. Remote or
   Indianapolis.
2. **Contact** — `nick@giulioni.com` and `linkedin.com/in/nickgiulioni`,
   both as clickable links.
3. **Download resume (PDF)** — `/assets/nick-giulioni-resume.pdf`,
   `download="Nick-Giulioni-Resume.pdf"`.
4. **Summary** — three sentences. Operator who built his own tools. Ran a
   $3M+ construction business and a $150M annual e-commerce budget. Now ships
   AI products with one foot still in the operating world (Ballpark).
5. **Ballpark bridge** — one short paragraph explaining the hinge from
   construction operator to AI builder. Status: current product work.
6. **Experience** — recent roles only, with truthful titles, dates, and
   metrics (Off Leash Construction $3M+, 3,000+ doors, Ballpark launch;
   Meta FRL; Corsair awards; Razer $150M).
7. **Earlier experience** — compact four-row list (TP-LINK USA, D-Link,
   Arclyte, Newegg) preserving truthful titles and dates.
8. **Operating history** — subordinate, one short block naming Laural Mill,
   The Wilds, Off Leash Investments without venue/STR/48-hour claims.
9. **Education** — "University of Southern California — Marshall School of
   Business, 2009–2012." No degree or major claimed.

The printable page (already styled for `@media print`) must fit on **two US
Letter pages** with a minimum print body size of **7.8 pt**.

## Selected work (was /work/)

Page title becomes **"Selected work"**. One case study, one receipt trio.

- **01 Ballpark** — compact editorial case with four labelled facts in
  this order: **Operating context**, **Problem**, **Built**, **Status**.
  No customer or adoption claims. No ROI, savings, or public-launch claim.
  No fake URL or fake screenshot.
- **02 Also shipped — A Little True** — compact single-line entry linking
  exactly `https://alittletrue.com`. No destination URL other than that.
- **Operating receipts** — three receipts only: **$3M+**, **3,000+**,
  **$150M**. The 48-hour STR pitch kit receipt is removed. Best Notes,
  venues, and real-estate entries are removed.

## Earlier media (was /media/)

Page title becomes **"Earlier media archive"**. The seven incumbent
appearances (Roots Realty, Leverage Podcast, Circle Investor, Billy Keels,
Get IN., Simple Quarters, Hacking Real Estate Podcast) keep their existing
URLs and exact episode titles. No new appearances. No new logos. No
publisher-owned marks referenced. `/media/` is not in the primary nav; a
small footer link points to it as a secondary archive.

## Portable CSS (read-only port from `work-media-responsive` worktree)

The recruiter-first site ports only these structural CSS additions from the
`work-media-responsive` worktree. **Content and assets are not ported.**

- `viewport-fit=cover` and three safe-area CSS variables
  (`--safe-left`, `--safe-right`, `--safe-bottom`).
- `env(safe-area-inset-*, 0px)` padding on `.sheet`.
- `@media (pointer: coarse)` rule with `min-width: 44px; min-height: 44px`
  for every nav action, contact link, destination link, episode-title link,
  and home-destination heading link.
- `@media (prefers-reduced-motion: reduce)` rule.
- 560 px and 800 px breakpoints preserved.

## Non-goals

- No `/services/`, no consulting pricing, no fractional-offer copy.
- No new top-level pages, CMS, framework, analytics, or scripts.
- No invented customer, adoption, ROI, savings, or public-launch claims for
  Ballpark.
- No Best Notes, venues, real estate, or 48-hour STR claims on Home or
  Selected work.
- No changes to CSP, root-relative URL discipline, no-scripts rule,
  no-inline-styles rule, no-cards/pills/gradients/shadows/radii rule, or
  the existing security-header posture in `vercel.json`.
- No edits to the Second Brain or to `nicks-agent-skills`.

## Verification

- `python3 -m unittest discover -s tests -v` green.
- `tools/regen_resume_pdf.sh` produces a ≤ 2-page PDF with selectable
  text; `pdfinfo` and `pdftotext` checks pass.
- `curl` smoke against `/`, `/career/`, `/work/`, `/media/`, and
  `/assets/nick-giulioni-resume.pdf` returns 200 from a local server.
- `npx impeccable detect` against changed HTML files returns clean or
  zero actionable findings.
- Diff against `feat/recruiter-first` parent commit is contained to the
  scope above.
