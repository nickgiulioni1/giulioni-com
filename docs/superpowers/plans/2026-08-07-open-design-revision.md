# Open Design Career and Homepage Revision Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Revise the approved Open Design prototype so Career reads current-to-earliest, Laural Mill is included, Home gives Career and Work balanced weight, and verified social links appear consistently.

**Architecture:** Modify only the existing Open Design-owned static artifact. Keep `index.html` canonical, mirror it to `home.html`, use `giulioni-site.css` as the shared visual system, and limit `work.html` changes to the shared contact treatment.

**Tech Stack:** Static HTML5, shared CSS, Open Design local preview, shell-based structural and HTTP checks.

**Source spec:** `docs/superpowers/specs/2026-08-07-open-design-revision-design.md`

---

## Chunk 1: Revise and verify the Open Design artifact

### Task 1: Establish the factual and structural baseline

**Files:**
- Read: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/index.html`
- Read: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/home.html`
- Read: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/career.html`
- Read: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/work.html`
- Read: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/giulioni-site.css`
- Read: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/DESIGN.md`
- Read: GitHub issues `nickgiulioni1/giulioni-com#1`, `#2`, `#6`, and `#7`, including comments

- [ ] **Step 1: Read every scoped artifact file and the four GitHub issue threads**

Confirm the current page hierarchy, breakpoint rules, print rules, dates, roles, and verified metrics before changing content.

- [ ] **Step 2: Record the baseline assertions**

Confirm that `index.html`, `career.html`, and `work.html` parse; `index.html` and `home.html` are currently equivalent; and the shared stylesheet has balanced braces.

### Task 2: Commission the Open Design revision

**Execution ownership:** Open Design is the sole writer for all file changes in Tasks 3–6. Those changes are requirements for the run prompt, not instructions for the orchestrator to edit artifact files directly. The orchestrator performs the post-run verification steps in Task 6.

- [ ] **Step 1: Start the revision run**

Start a new run in project `giulioni-com-career-credibility` with this plan and the approved spec as the authoritative instructions. Include every file-change requirement from Tasks 3–6 in the run prompt.

- [ ] **Step 2: Monitor the run**

Poll every 30–60 seconds until the run succeeds or fails. Do not substitute manual artifact writing while the run is in flight. On success, capture the returned preview and Studio URLs.

### Task 3: Make Career current-to-earliest

**Files:**
- Modify: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/career.html`

- [ ] **Step 1: Reorder the chapter structure**

Order the page as current AI product work, Indiana operator work, then e-commerce leadership. Within each chapter, order entries by newest start or acquisition date.

- [ ] **Step 2: Add Laural Mill**

Add Laural Mill to the Indiana operator chapter as an owned/operated wedding venue acquired in March 2023. Do not add an unverified title, metric, location, or acquisition story.

- [ ] **Step 3: Preserve the Ballpark bridge and print structure**

Keep Ballpark connecting the construction chapter to current AI product work. Preserve the existing letter-size print rules and scan-friendly chapter hierarchy.

- [ ] **Step 4: Verify Career facts and ordering**

Check every role, date, metric, and claim against issues #1, #2, #6, and #7 and their comments. Confirm current-to-earliest chapter order and newest-to-oldest entry order.

### Task 4: Give Home two balanced destinations

**Files:**
- Modify: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/index.html`
- Modify: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/giulioni-site.css`

- [ ] **Step 1: Refine the homepage composition**

Let Open Design make the final density call. Start from two equal typographic destinations—Career and What I’m Working On—beneath the existing operator-first introduction and portrait.

- [ ] **Step 2: Add bounded evidence copy**

Give each destination one evidence line of at most 90 characters using only facts from issues #1, #2, #6, and #7.

- [ ] **Step 3: Preserve responsive behavior**

Keep the existing 800px and 560px breakpoints. Stack the destinations in source order on narrow screens without cards, pills, shadows, radii, or new decoration.

- [ ] **Step 4: Verify equal destination treatment**

Confirm the Career and Work pointers use the same heading level, CSS selector/type treatment, and layout area on desktop, and the same stacked container on narrow screens.

### Task 5: Add the verified contact set consistently

**Files:**
- Modify: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/index.html`
- Modify: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/career.html`
- Modify: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/work.html`

- [ ] **Step 1: Add one identical typographic link set to each page**

Use exactly:

```text
Email · LinkedIn · X · Instagram
```

with these exact destinations:

```text
mailto:nick@giulioni.com
https://www.linkedin.com/in/nickgiulioni
https://x.com/NickGiulioni
https://www.instagram.com/nickgiulioni/
```

- [ ] **Step 2: Keep the links secondary**

Place the set in each page’s contact/footer area using ordinary underlined text links and the existing muted/ultramarine palette.

### Task 6: Synchronize and verify the deliverable

**Files:**
- Modify: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/home.html`
- Modify if needed: `/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility/DESIGN.md`

- [ ] **Step 1: Mirror the canonical homepage**

Copy the final `index.html` content byte-for-byte to `home.html`. Ensure all internal Home links target `index.html`.

- [ ] **Step 2: Update the design documentation**

Record the balanced Career/Work homepage destinations and consistent typographic social treatment if they are not already represented.

- [ ] **Step 3: Run structural verification**

Parse all HTML files with Python's `html.parser`, verify equal opening/closing CSS brace counts, verify `cmp -s index.html home.html`, and use `rg` to search for prohibited scripts, placeholders, cards, shadows, radii, pills, gradients, icon markup, external asset URLs, and platform-specific social colors. Expected result: every HTML file parses, brace counts match, homepage files match, and the prohibited-pattern search has no implementation matches.

- [ ] **Step 4: Crawl the completed preview**

Use the preview URL returned by the completed Open Design run. Extract every internal page, stylesheet, and local asset URL from all HTML pages, request each target, and expect HTTP 200. Click through Home → Career → Work and confirm all contact links use the exact URLs above.

- [ ] **Step 5: Verify Career print rendering**

Open Career from the completed preview with print media emulation at US Letter size. Confirm the letter-size rules apply, content is not clipped, and Email · LinkedIn · X · Instagram remain present. If Open Design's exporter fails, record the exact exporter error and use browser print emulation or a print screenshot as the fallback.

- [ ] **Step 6: Report the visible result and any verification limitation**

Provide the refreshed Open Design preview and Studio links. State what now works and identify any exporter or preview failure by location, cause, and available fallback.
