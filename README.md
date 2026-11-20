# giulioni.com

Nick Giulioni’s static Central Indiana buyer and seller site. Limestone, Monon green and brick, self-hosted Instrument Serif and Instrument Sans, and no executable page scripts.

Pages: `/`, `/sell/`, `/buy/`, `/areas/`, `/areas/carmel/`, `/areas/westfield/`, `/areas/fishers/`, `/areas/north-indianapolis/`, `/areas/noblesville/`, `/areas/zionsville/`, `/about/`, `/contact/`, `/podcast/`, `/privacy/`, `/contact/thanks/`, `/contact/error/`, and `404.html`.

## Local preview

Run `python3 -m http.server 8000`, then open `http://localhost:8000`. This previews static pages only. Use `vercel dev` for the same-origin function; keep notification credentials unset for local failure-path testing.

Shared values live in `site.json`. After changing them or page copy, run `python3 tools/render_site.py` and commit the generated HTML. There is no deployment build step. Share cards regenerate with `python3 tools/make_og_cards.py` using Pillow, fonttools and brotli, installed in a local virtual environment. The tool uses the repository fonts and existing portrait.

## Consult requests

Plain HTML forms POST to `api/consult.js`. It validates, applies a best-effort in-memory limit, sends email through Resend and a text through Quo, then redirects. No database or campaign enrollment. Email is the stored record; text failure does not discard a successful email. No dependencies are needed at runtime.

Configuration names: `RESEND_API_KEY`, `NOTIFY_EMAIL_TO`, `NOTIFY_EMAIL_FROM`, `QUO_API_KEY`, `QUO_FROM_NUMBER`, `NOTIFY_SMS_TO`. See DEPLOYMENT.md for setup requirements. Leave these unset until Nick authorizes configuration.

## Checks

`python3 -m unittest discover -s tests -v`

`node --test`

Tests cover static structure, shared copy, links, forms, headers, image metadata, redirects, and mocked function notifications. No test makes a real notification request.

## Photos

All photos are driven by `site.json` and must be metadata-stripped (EXIF, GPS, XMP, ICC) before they are committed; the tests check every file under `assets/`. Each photo is a set of files named `<id>-<size>.<avif|webp|jpg>`, where size is the long edge in pixels (800, 1200, 1600 and, for wide area photos, 2400). Empty slots render nothing (the home hero falls back to the existing portrait).

- `work_gallery`: ordered list of `{"id", "place", "detail", "alt"}`; files in `assets/work/`. `work_gallery_credit` is an optional credit line.
- `hero_photo`: `null` or `{"id", "alt"}`; files in `assets/nick/`. Portrait 2:3.
- `about_photos`: up to three `{"id", "alt", "caption"?, "credit"?, "fit"?}`; files in `assets/nick/`. Portrait 4:5 for the first two photos, side by side above 600px wide and stacked at 600px and below, with a full-width 3:2 landscape below when three are supplied; landscape 3:2 for one. `"fit": "contain"` shows the full 4:5 frame with `object-fit: contain` and no `object-position`, never cropped; the family photo must keep it.
- `area_photos`: one key per area slug, `null` or `{"id", "alt", "caption", "credit", "license"?, "license_url"?, "source_url"?}`; files in `assets/areas/`. Landscape 3:2. A credit is required.

After editing, run `python3 tools/render_site.py` and both test commands, and commit the regenerated HTML.

The sunflower composited into the family photo uses Google’s [Noto Emoji U+1F33B artwork](https://github.com/googlefonts/noto-emoji/blob/22e564626297b4df0a40570ad81d6c05cc7c38bd/svg/emoji_u1f33b.svg), copyright 2013 Google, Inc., under the [Apache License 2.0](https://github.com/googlefonts/noto-emoji/blob/22e564626297b4df0a40570ad81d6c05cc7c38bd/svg/LICENSE). The artwork was scaled and composited into the photograph.
