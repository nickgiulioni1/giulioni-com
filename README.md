# giulioni.com

Nick Giulioni’s static Central Indiana buyer and seller site. Cream, forest, and rust, self-hosted Newsreader and Instrument Sans, and no executable page scripts.

Pages: `/`, `/sell/`, `/buy/`, `/areas/`, `/areas/carmel/`, `/areas/westfield/`, `/areas/fishers/`, `/about/`, `/contact/`, `/podcast/`, `/privacy/`, `/contact/thanks/`, `/contact/error/`, and `404.html`.

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
