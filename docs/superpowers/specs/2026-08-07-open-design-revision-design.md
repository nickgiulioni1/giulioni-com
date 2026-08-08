# Open Design Revision — Career, Homepage, and Social Links

## Objective

Refine the approved Open Design direction without changing its printed-letterhead character. The revision addresses three gaps: Career ordering, missing Laural Mill history, and a homepage that currently points only to Work.

## Career page

- Present the three chapters in reverse-career order: current AI product work first, Indiana operator work second, and e-commerce leadership last. Within each chapter, present entries newest to oldest.
- Preserve the three-chapter scan structure: AI product builder, Indiana operator, and e-commerce leadership.
- Use GitHub issues #1, #2, #6, and #7 in `nickgiulioni1/giulioni-com`, including their comments, as the authoritative content and date source. Do not reconstruct Career history from memory.
- Add Laural Mill to the Indiana operator chapter as an owned/operated wedding venue acquired in March 2023.
- Within each chapter, order entries by most recent start or acquisition date. Current overlapping roles remain grouped in their chapter; the chapter structure intentionally takes precedence over one globally interleaved timeline.
- Keep Ballpark as the bridge between construction operations and current AI product work.
- Retain the existing print-specific treatment, verified facts, contact information, and restrained letterhead system.

## Homepage

Open Design may make the final density choice. Start from the recommended “two-door front sheet” approach unless a stronger solution emerges during visual refinement.

- Keep the existing operator-first introduction and portrait.
- Give Career and What I’m Working On equal visual weight as the two primary next destinations.
- Give each destination one concise evidence line, no more than 90 characters, using only facts from GitHub issues #1, #2, #6, and #7. Open Design has copywriting latitude within those factual constraints.
- Preserve the typographic navigation and the current no-card, no-pill, rules-not-boxes system.
- On narrow screens, stack the two destinations while preserving their rank and readability.

## Social links

Add a restrained contact/social line using verified destinations only:

- Email: `mailto:nick@giulioni.com`
- LinkedIn: `https://www.linkedin.com/in/nickgiulioni`
- X: `https://x.com/NickGiulioni`
- Instagram: `https://www.instagram.com/nickgiulioni/`

The social links should remain secondary to the site’s content and email contact. Add the same Email · LinkedIn · X · Instagram typographic link set to the contact/footer area of Home, Career, and Work. Email must appear alongside the social links on every page. Use no icons, pills, or platform-colored treatments.

## Artifact location and files in scope

Revise only the existing Open Design project at:

`/Users/nickgiulioni/Library/Application Support/Open Design/namespaces/release-stable/data/projects/giulioni-com-career-credibility`

The production repository remains unchanged except for this planning specification.

- Open Design homepage entry (`index.html`) is canonical.
- Preserve `home.html` as a byte-for-byte homepage mirror because the existing Open Design project contains it. After the revision, copy the final canonical homepage content to `home.html`; all internal Home links must target `index.html`.
- Open Design Career page (`career.html`)
- Shared Open Design stylesheet (`giulioni-site.css`)
- Work page only where shared navigation or social treatment requires consistency
- Open Design design documentation when implementation rules change

## Verification

- Career chapters read current-to-earliest, and entries within each chapter read newest-to-oldest.
- Laural Mill appears with the March 2023 acquisition date and no invented details.
- Home offers balanced paths to Career and Work.
- Career and Work pointers use the same heading level, type treatment, and layout area; on narrow screens they stack in the same source order.
- LinkedIn, X, and Instagram use the exact verified URLs above.
- Use the preview URL returned by the completed Open Design run. Home, Career, shared CSS, and the portrait must return HTTP 200 from that preview root, and Work must remain reachable through its internal link.
- All internal links and local assets return successfully.
- HTML parses and the shared stylesheet has an equal count of opening and closing braces.
- Preserve the existing 800px and 560px responsive breakpoints.
- Career print output retains contact/social links and the existing letter-size print treatment; the new homepage destinations do not affect Career print layout.
- No scripts, gradients, cards, shadows, radii, pills, placeholder content, or new external assets are introduced.
