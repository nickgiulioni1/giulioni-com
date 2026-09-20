#!/usr/bin/env python3
"""Render the 1200x630 social share cards in assets/.

Portrait plus title, cream/forest/rust palette. Run after changing card copy:

    python3 tools/make_og_cards.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO_ROOT, "assets")
PORTRAIT = os.path.join(ASSETS, "portrait-nick.jpg")

W, H = 1200, 630
PAPER = (246, 243, 236)
INK = (22, 33, 28)
INK_SOFT = (74, 84, 78)
RUST = (184, 80, 31)

SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SANS = "/System/Library/Fonts/Helvetica.ttc"

CARDS = (
    (
        "og-home.png",
        "Nick Giulioni",
        "An operator who doesn't\naccept the status quo.",
        "AI product, solutions, enablement, forward-deployed",
    ),
    (
        "og-career.png",
        "Resume",
        "Razer, Corsair, Meta,\nOff Leash, Ballpark.",
        "Ten years commercial, then built and ran the business",
    ),
    (
        "og-work.png",
        "Selected work",
        "Ballpark: AI estimating\nbuilt inside the job.",
        "Shipped from the company that needed it",
    ),
)


def wrapped(draw, text, font, fill, x, y, leading):
    for line in text.split("\n"):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def render(name, eyebrow, title, footer):
    card = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(card)

    panel_w = 420
    portrait = Image.open(PORTRAIT).convert("RGB")
    scale = max(panel_w / portrait.width, H / portrait.height)
    portrait = portrait.resize(
        (round(portrait.width * scale), round(portrait.height * scale)),
        Image.LANCZOS,
    )
    left = (portrait.width - panel_w) // 2
    top = round(portrait.height * 0.08)
    top = min(max(top, 0), portrait.height - H)
    card.paste(portrait.crop((left, top, left + panel_w, top + H)), (W - panel_w, 0))
    draw.rectangle([W - panel_w - 6, 0, W - panel_w - 1, H], fill=RUST)

    eyebrow_font = ImageFont.truetype(SANS, 26)
    title_font = ImageFont.truetype(SERIF, 62)
    footer_font = ImageFont.truetype(SANS, 24)

    x = 72
    draw.text((x, 104), eyebrow.upper(), font=eyebrow_font, fill=RUST)
    wrapped(draw, title, title_font, INK, x, 168, 78)
    draw.line([(x, H - 152), (x + 96, H - 152)], fill=RUST, width=3)
    draw.text((x, H - 122), footer, font=footer_font, fill=INK_SOFT)
    draw.text((x, H - 84), "giulioni.com", font=footer_font, fill=INK)

    out = os.path.join(ASSETS, name)
    card.save(out, "PNG", optimize=True)
    print("wrote %s" % out)


if __name__ == "__main__":
    for card in CARDS:
        render(*card)
