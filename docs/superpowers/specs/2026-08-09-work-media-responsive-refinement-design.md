# Work, Media, and Responsive Refinement

**Status:** Owner-approved visual direction, 2026-08-09  
**Scope:** Content changes on `/work/` and `/media/`; responsive regression coverage for `/`, `/career/`, `/work/`, `/media/`, and shared navigation/contact/footer  
**Design authority:** Preserve the incumbent connected-letterhead system in `styles.css`.

## Objective

Make the work behind Nick's products legible without turning the site into a portfolio-card grid. Add direct destinations for Best Notes, The Wilds, and Laural Mill; give appearances restrained visual identity; and make every page feel intentionally composed from 320px phones through large desktop screens.

## Approved direction

Use compact editorial mini case studies. Each work entry answers four questions in order: what problem existed, what Nick built, the product principle behind it, and its current status or destination. Keep numbered entries, typographic hierarchy, rules, paper, ink, and ultramarine. Do not redesign the masthead, introduce rounded cards, add decorative gradients, or create a logo wall.

## Public content

### Ballpark

- Position it as a construction-estimating product born inside a $3 million construction operator.
- Problem: estimating was slow and difficult to standardize.
- Built: reliable pricing and estimating workflows with AI as a replaceable seam.
- Principle: a sharp tool for real jobs, not an AI demo.
- Status: current product work. Do not link the private/product repository as the primary public destination unless a verified public product URL is found.

### A Little True

- Describe it as a private daily practice for saying, hearing, or marking what the user needs to hear.
- Name the three equal modes: speak, listen, and complete.
- State the product refusals concisely: on-device, free, no account, no ads, no streaks, no guilt.
- Link to `https://alittletrue.com`.

### Best Notes

- Describe it as a Markdown-first personal operating system for busy Apple users.
- Lead with the promise: “Know what matters today—and why.”
- Name the initial loop: Today → Capture → Meetings.
- State the data doctrine: user-owned open files remain the source of truth; AI is a satellite, not a silo.
- No verified public Best Notes destination exists yet: its repository is private and has no homepage. Render non-linked “Private development” status text until Nick supplies a verified public URL. Never link the private repository.

### Venues

- Treat The Wilds and Laural Mill as distinct operating businesses inside one numbered entry.
- Explain their relevance: hospitality, teams, facilities, demand, and operational details provide the real-world environment behind the product work.
- Link The Wilds to `https://thewildsvenue.com/` and Laural Mill to `https://lauralmill.com/`.
- Avoid unverified revenue, capacity, pricing, or ownership claims beyond the Second Brain's statement that Nick owns and operates them.

## Media identity

- Inventory all seven appearances before coding and define the exact approved asset/fallback for each one.
- Add a small, consistent show mark beside an appearance only when an official asset is available from the publisher's own site or channel.
- Self-host optimized assets; never hotlink them. Preserve originals byte-for-byte and document each source URL plus usage notes in `assets/media/README.md`.
- Use CSS grayscale only when the official mark remains permitted and legible. Otherwise display the official color mark. Never redraw, recolor, or typeset an imitation logo.
- Use explicit image dimensions and useful alt text. The show name remains visible text, so decorative marks may use empty alt text where appropriate.
- When no trustworthy official asset exists, retain the text-only entry. Missing artwork must never block an appearance.

## Responsive behavior

- Keep one information architecture at every width; reflow instead of hiding core content.
- Desktop: number, product identity, and case-study story use an asymmetric editorial grid with readable line lengths.
- Tablet: compress the identity column and allow the story to retain priority; no cramped four-column rows.
- Phone: each product becomes a single reading column after its number/title, facts stack vertically, and destination controls become at least 44×44 CSS-pixel touch targets.
- Media entries stack mark/show identity above episode detail on narrow screens. Logo dimensions remain bounded so artwork cannot dominate.
- Shared navigation and destination controls have 44×44 CSS-pixel hit areas for coarse pointers; inline episode-title links are exempt. Add `viewport-fit=cover` and safe-area side/bottom padding with `env(safe-area-inset-*, 0px)` fallbacks.
- Use fluid type and spacing with `clamp()`, content-driven breakpoints, reduced-motion-safe interaction, and no hover-only behavior.

## Verification

- Test visual layout at 320, 375, 390, 768, 1024, 1440, and a wide desktop viewport.
- Check portrait and landscape phone widths, keyboard focus, touch target sizing, horizontal overflow, and long show/product names.
- Verify every external URL returns a valid destination and every self-hosted image loads.
- Give every product entry semantic problem, built, principle, and status/destination elements and test for all four. Entry 04 may contain two independently linked venue sub-entries.
- Extend the existing test suite for the required public links, the approved seven-item logo/fallback inventory, image constraints, and responsive safeguards across every public page.
- Run repository tests, the Impeccable mechanical detector once on changed targets, and browser verification against the local server before merging.

## Non-goals

- No new top-level pages, CMS, JavaScript framework, analytics, product screenshots, or wholesale redesign.
- No Second Brain edits are required for this site refinement.
- No invented launch claims, customer counts, or product availability.
