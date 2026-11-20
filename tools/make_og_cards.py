#!/usr/bin/env python3
"""Render the 1200x630 social share cards in assets/.

Portrait plus title, limestone/green/brick palette. Run after changing card copy:

    python3 tools/make_og_cards.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(REPO_ROOT, "assets")
PORTRAIT = os.path.join(ASSETS, "portrait-nick.jpg")

W, H = 1200, 630
PAPER = (244, 239, 230)
INK = (21, 33, 27)
INK_SOFT = (70, 82, 75)
RUST = (154, 59, 26)

SERIF = os.path.join(ASSETS, "fonts/instrument-serif-latin-normal.woff2")
SANS = os.path.join(ASSETS, "fonts/instrument-sans-latin-wght.woff2")

CARDS = tuple(("og-"+key+".png", "Nick Giulioni", title, "Indianapolis north side & suburbs") for key,title in [
    ("home", "A practical eye for\nyour next move."),
    ("sell", "Thinking about\nselling your home?"),
    ("buy", "Find the town.\nThen find the home."),
    ("areas", "Find your area.\nPlan your move."),
    ("about", "An agent with\nan investor’s eye."),
    ("podcast", "Indiana real estate\nin conversation."),
])


def load_font(path, size):
    # FreeType builds vary in WOFF2 support; decode the self-hosted font if needed.
    from io import BytesIO
    from fontTools.ttLib import TTFont
    font = TTFont(path)
    font.flavor = None
    buffer = BytesIO()
    font.save(buffer)
    buffer.seek(0)
    return ImageFont.truetype(buffer, size)


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

    eyebrow_font = load_font(SANS, 26)
    title_font = load_font(SERIF, 78)
    footer_font = load_font(SANS, 24)

    x = 72
    draw.text((x, 104), eyebrow, font=eyebrow_font, fill=RUST)
    wrapped(draw, title, title_font, INK, x, 160, 84)
    draw.line([(x, H - 152), (x + 96, H - 152)], fill=RUST, width=3)
    draw.text((x, H - 122), footer, font=footer_font, fill=INK_SOFT)
    draw.text((x, H - 84), "giulioni.com", font=footer_font, fill=INK)

    out = os.path.join(ASSETS, name)
    card.save(out, "PNG", optimize=True)
    print("wrote %s" % out)


if __name__ == "__main__":
    for card in CARDS:
        render(*card)
