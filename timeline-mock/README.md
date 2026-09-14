# Timeline mock

An isolated, event-driven homepage preview. Production `index.html`, shared CSS,
CSP, routing, and tests are unchanged. Nothing here is merged or deployed.

## Open the preview

1. From the repository root, run `python3 -m http.server 8000`.
2. Open http://localhost:8000/timeline-mock/.
3. Toggle Personal and Professional. Both checked shows their union, either alone
   includes matching mixed-tag entries, and neither checked shows an empty state.

You can also open `timeline-mock/index.html` directly with `file://`. The bundled
classic script and relative asset links support this. Google fonts need a network
connection; the existing serif and sans-serif fallbacks work offline.

## Edit an entry

`content/timeline/*.json` is the source of truth, with one object per file:

```json
{
  "date": "2026-09-14",
  "title": "An afternoon close to home [PLACEHOLDER]",
  "place": "Carmel, Indiana",
  "coords": null,
  "people": [],
  "tags": ["personal"],
  "photo_original": "/assets/portrait-nick.jpg",
  "photo_styled": null,
  "blurb": "[PLACEHOLDER] Fictional sample check-in.",
  "visibility": "public"
}
```

`date` is an ISO calendar date, `title` and `blurb` are plain text, `people` is an
array of names, and `tags` is a nonempty array containing `personal`,
`professional`, or both. `place`, `coords`, and photo fields are optional or null.
If supplied, `coords` is `{ "lat": 39.9, "lng": -86.1 }`; coordinates are not
rendered. Photo paths refer to local site assets. `visibility` is `public`,
`private`, or `draft`; only public entries are bundled and rendered.
Never put sensitive content into this static repository: source files can still
be served directly. Visibility is a preview convention, not access control.

After adding, editing, or removing JSON files, run:

```sh
python3 timeline-mock/generate_entries.py
```

This regenerates `timeline-mock/entries.js`, sorted newest first. The page reads
that bundle under both HTTP and file URLs; it does not discover or fetch JSON at
runtime. No application build or dependency installation is required. Refresh
after regeneration. Last updated and last entry both derive from the newest
public entry date, not the file modification time or current date. Filtering
does not change them; selecting the latest-entry link resets the filters so its
card is visible.

## What is stubbed

- Check-ins are manually authored JSON. There is no capture form, webhook, AI
  extraction, review queue, database, or real event ingestion. Intended flow:
  check-in → reviewed structured entry → file → homepage.
- Dates are illustrative timeline placement, not verified event dates. Career
  claims use the approved published facts. Fictional personal copy is explicitly
  marked `[PLACEHOLDER]`; the venue card is operating context, not an event claim.
- The portrait and Ballpark screenshot reuse existing assets. They are labeled
  mock assets and are not check-in photos. Original images appear first; setting
  `photo_styled` adds a labeled companion underneath. No image styling service is
  connected, and all supplied styled fields are null.
- JavaScript drives this local preview. Production CSP forbids scripts and remains
  unchanged. Deployment under that CSP will block this mock's scripts. The mock
  has a no-JavaScript explanation and `noindex`, not a production fallback.
- A production homepage swap requires a separately approved implementation,
  including public-content review and a static-rendering strategy compatible
  with the existing no-JS CSP. This mock does not change the homepage or navigation.
