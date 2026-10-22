# Issue 26 figure screenshots

Before: already-redacted main at 7354e8b.
After: ebda5df4a7b52d3639364ecbc637f0da4b7e9dfe.

Captured the rendered Ballpark figure on / and /work/ with a local python3 -m http.server on port 8768 and headless Chrome through Puppeteer. Desktop 1440x1000 DPR1. Mobile 390x844 DPR2. External requests were blocked, so both sides use the same local font fallbacks. Only the figure is captured.

Crop: PIL box (38, 104, 1214, 750), right and bottom exclusive. Output master 1176x646. Existing redaction pixels are preserved exactly in the lossless master.
