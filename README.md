# Site beautification evidence

Source head: `be1e10188be807b0163722c2d214257795294266`. Baseline: `71c1b57`.

- Stronger serif headings and consistent section spacing across all five pages.
- Alternating track record rows, wider case facts, and larger receipt figures.
- Two-column media archive with larger episode titles; one column on phones.
- Underlined current navigation and footer links, larger buttons, and contrasting keyboard focus.
- Darker rust text and corrected product-button hover contrast while retaining the existing palette.

## Screenshots

Full-page PNGs. Desktop viewport 1280 × 900; phone viewport 375 × 900. Device scale factor 1; touch enabled at 375px.

| Page | Before 1280 | After 1280 | Before 375 | After 375 |
|---|---|---|---|---|
| / | [before 1280](before/home-1280.png) | [after 1280](after/home-1280.png) | [before 375](before/home-375.png) | [after 375](after/home-375.png) |
| /career/ | [before 1280](before/career-1280.png) | [after 1280](after/career-1280.png) | [before 375](before/career-375.png) | [after 375](after/career-375.png) |
| /work/ | [before 1280](before/work-1280.png) | [after 1280](after/work-1280.png) | [before 375](before/work-375.png) | [after 375](after/work-375.png) |
| /media/ | [before 1280](before/media-1280.png) | [after 1280](after/media-1280.png) | [before 375](before/media-375.png) | [after 375](after/media-375.png) |
| /404.html | [before 1280](before/404-1280.png) | [after 1280](after/404-1280.png) | [before 375](before/404-375.png) | [after 375](after/404-375.png) |

## Lighthouse

Local static-server runs, not production measurements. The initial c78df86 after-results and corrections at 7045c34 and 4eacb98 failed the strict CLS gate. Their reports and screenshots are preserved under after/initial-c78df86, after/fix1-7045c34, and after/fix2-4eacb98. Each new source correction was committed before its combined screenshot and Lighthouse hold. The current after-results use the committed typography correction at the source head above. P/A/B/S = performance/accessibility/best-practices/SEO. Scores out of 100.

| Page | Mobile before → after P/A/B/S; CLS | Desktop before → after P/A/B/S; CLS |
|---|---|---|
| home | 100/100/100/100; CLS 0.00039626 → 100/100/100/100; CLS 0.00010186 | 100/100/100/100; CLS 0.00262970 → 100/100/100/100; CLS 0.00021286 |
| career | 100/100/100/100; CLS 0.00027107 → 100/100/100/100; CLS 0.00027107 | 100/100/100/100; CLS 0.01769141 → 100/100/100/100; CLS 0.01292795 |
| work | 100/100/100/100; CLS 0.00000000 → 100/100/100/100; CLS 0.00000000 | 100/100/100/100; CLS 0.01824761 → 100/100/100/100; CLS 0.00521761 |
| media | 100/100/100/100; CLS 0.00000000 → 100/100/100/100; CLS 0.00000000 | 100/100/100/100; CLS 0.00542809 → 100/100/100/100; CLS 0.00000000 |

## Network, accessibility, and scope

Origin differences: 0. Computed text contrast failures: 0. Hover contrast failures: 0. Keyboard focus failures: 0. Overflow at screenshot widths: 0. Protected files changed: 0.


| Page | Before and after request origins |
|---|---|
| home | http://127.0.0.1:65127, https://fonts.googleapis.com, https://fonts.gstatic.com |
| career | http://127.0.0.1:65127, https://fonts.googleapis.com, https://fonts.gstatic.com |
| work | http://127.0.0.1:65127, https://fonts.googleapis.com, https://fonts.gstatic.com |
| media | http://127.0.0.1:65127, https://fonts.googleapis.com, https://fonts.gstatic.com |
| 404 | http://127.0.0.1:65127, https://fonts.googleapis.com, https://fonts.gstatic.com |

All HTML, font links, fetch priorities, tests, and all 14 sanitized demo-image variants are unchanged. Only styles.css changed in the implementation branch.


Chrome: 155.0.8059.86. Python Playwright: 1.60.0. Lighthouse: 13.5.0.


## Unit tests

```text

----------------------------------------------------------------------
Ran 65 tests in 2.520s

OK
Exit code: 0
```


Not run: production Lighthouse, deployed browser checks, independent PR review. No PR opened or merge performed.
