# giulioni.com

Personal site for Nick Giulioni. Static — no build step.

## Local preview

```sh
python3 -m http.server 8791 --directory .
```

Open `http://127.0.0.1:8791/`.

## Deploy subset

| Path | Role |
|---|---|
| `index.html` | Page |
| `styles.css` | System |
| `assets/portrait-nick.jpg` | Hero plate (only asset referenced) |
| `vercel.json` | Security headers (CSP allows Google Fonts) |

## Provenance

Exported from Buzz Nest workspace `OUTBOX/GIULIONI_COM_SITE` after owner accept (2026-08-05). Framing A / hybrid C per redesign brief. Independent re-crits closed with zero must-fixes before publish setup.
