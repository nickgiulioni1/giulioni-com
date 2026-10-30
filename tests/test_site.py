"""Static-site contract for giulioni.com (cream/forest/rust editorial system).

Deterministic, standard-library-only checks describing the approved final
production state: a four-page static site (Home, Resume, Selected work,
Podcasts and talks) that leads with Nick's T&H Realty Services role, with
root-relative internal links and assets, the approved contact links (Email,
LinkedIn), the primary nav, one owner-facing primary CTA, the Indy REI guest
credit, the single Ballpark card, one-line career history, the Selected work
Ballpark case + A Little True + three receipts, the media URLs, the content
that must never appear, the resume PDF, the full-bleed band (#60) and media
grid (#61) layouts, the responsive / safe-area / coarse-pointer / reduced-motion CSS,
CSP-safe markup, balanced CSS braces, and none of the prohibited Open
Design-only artifacts (data-od-id attributes, sidecars, home.html,
DESIGN.md, brand-spec.md).

Run:

    python3 -m unittest discover -s tests -v
"""

import glob
import hashlib
import html
import json
import os
import re
import shutil
import struct
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = {
    "home": "index.html",
    "resume": "career/index.html",
    "work": "work/index.html",
    "media": "media/index.html",
}

# Approved contact links (exact strings, no trailing variants).
SOCIAL_HREFS = (
    "mailto:nick@giulioni.com",
    "https://www.linkedin.com/in/nickgiulioni",
)

# T&H role copy, exact strings from the Oct 30, 2026 brief.
TH_URL = "https://www.threaltyinc.com/"
TH_LETS_TALK = "https://www.threaltyinc.com/lets-talk/"
TH_RENTAL_ANALYSIS = "https://www.threaltyinc.com/free-rental-analysis/"
TH_ROLE = "Director of Sales and Marketing"
TH_DESCRIPTION = (
    "T&amp;H Realty Services is an Indianapolis property management company"
    " and real estate brokerage serving investors and landlords across"
    " Central Indiana."
)
TH_SCOPE = (
    "I help rental owners and investors find the right management for their"
    " properties, and I lead T&amp;H's investor community."
)

# Guest credit on Indy REI with T&H Realty: (episode title, URL, date).
INDY_REI_SHOW = "https://www.threaltyinc.com/indy-rei-with-th-realty-podcast/"
INDY_REI_EPISODES = (
    (
        "Trading 75 Rentals for 10 Elite Assets with Nick Giulioni",
        "https://indyreiwiththrealty.podbean.com/e/trading-75-rentals-for-10-elite-assets-with-nick-giulioni/",
        "Nov 18, 2025",
    ),
    (
        "Picking the Right Partner with Nick Giulioni (Part 1): Contractors",
        "https://indyreiwiththrealty.podbean.com/e/picking-the-right-team-contractors/",
        "Sep 10, 2024",
    ),
    (
        "The State of the Short-Term and Mid-Term Rental Market in Central"
        " Indiana with Nick Giulioni",
        "https://indyreiwiththrealty.podbean.com/e/the-state-of-the-short-term-and-midterm-rental-market-in-central-indiana/",
        "Jan 30, 2024",
    ),
)

BALLPARK_CARD_TITLE = "Ballpark, a product I'm building (2025 to present)"
BALLPARK_CARD_COPY = (
    "Ballpark is market intelligence for Central Indiana real estate pros. It"
    " turns listings, rentals and sales into comps, condition grades and"
    " leads, and it's bringing AI repair estimates into the same platform."
)

# Approved Media appearances: (episode title, URL), exact strings, in order.
MEDIA_ENTRIES = tuple((title, url) for title, url, _date in INDY_REI_EPISODES) + (
    (
        "9.5.24 Indy Investor Masterclass | Nick Giulioni &amp; Mark Nottingham",
        "https://www.youtube.com/watch?v=zmVUoNDVfcg",
    ),
    (
        "Everything You Need to Know About Midterm Rentals In Indianapolis"
        " &amp; Why They're HOT",
        "https://www.simplequarters.com/podcasts/everything-you-need-to-know-about-midterm-rentals-in-indianapolis-why-theyre-hot",
    ),
    (
        "Ep.02: Nick Giulioni: FAANG to FI",
        "https://www.youtube.com/watch?v=pI3Cgnx-ZVI",
    ),
    (
        "You WON'T BELIEVE Nick Giulioni's Journey from Tech to Real Estate",
        "https://www.rootsrealty.co/podcast/nick-giulioni-real-estate",
    ),
    (
        "The Leverage Podcast - Nick Giulioni",
        "https://www.youtube.com/watch?v=_A2HrOjWe50",
    ),
    (
        "Episode 1 - Nick Giulioni: How To Go From Side Hustle To Real Business",
        "https://www.youtube.com/watch?v=dv72SopKqeM",
    ),
    (
        "Convert I.T. Skills Into Long Distance Real Estate Investing Success"
        " - Nick Giulioni",
        "https://www.youtube.com/watch?v=B3gRQMjCng0",
    ),
    (
        "Why He Left Facebook to Build a Multimillion-Dollar Portfolio"
        " in the Midwest",
        "https://getindiana.com/podcast/nick-giulioni-off-leash-construction",
    ),
    (
        "Finding Deals In Today's Real Estate Market",
        "https://www.simplequarters.com/podcasts/finding-deals-in-todays-real-estate-market",
    ),
    (
        "Episode 4 Nick Giulioni",
        "https://www.hackingrealestatepodcast.com/episodes/104-nick-giulioni",
    ),
)

# External schemes that are exempt from the root-relative rule.
EXTERNAL_PREFIXES = ("#", "mailto:", "tel:", "data:", "http://", "https://")


def _path(rel):
    return os.path.join(REPO_ROOT, rel)


def _read_page(name):
    rel = PAGES[name]
    path = _path(rel)
    if not os.path.isfile(path):
        raise AssertionError("required page %r is missing (%s)" % (rel, path))
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _image_chunks(path):
    """(chunk id, payload) pairs of a PNG or RIFF WebP file, by content not extension."""
    with open(path, "rb") as fh:
        data = fh.read()
    chunks = []
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        i = 8
        while i + 8 <= len(data):
            n = int.from_bytes(data[i:i + 4], "big")
            chunks.append((data[i + 4:i + 8].decode("latin-1"), data[i + 8:i + 8 + n]))
            i += 12 + n
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        i = 12
        while i + 8 <= len(data):
            n = int.from_bytes(data[i + 4:i + 8], "little")
            chunks.append((data[i:i + 4].decode("latin-1"), data[i + 8:i + 8 + n]))
            i += 8 + n + (n & 1)
    else:
        raise AssertionError("%s is neither PNG nor WebP" % path)
    return dict(chunks)


def _image_size(path):
    """(width, height) of a PNG or WebP (VP8, VP8L, or VP8X) file."""
    chunks = _image_chunks(path)
    if "IHDR" in chunks:
        ihdr = chunks["IHDR"]
        return int.from_bytes(ihdr[0:4], "big"), int.from_bytes(ihdr[4:8], "big")
    if "VP8X" in chunks:
        x = chunks["VP8X"]
        return int.from_bytes(x[4:7], "little") + 1, int.from_bytes(x[7:10], "little") + 1
    if "VP8L" in chunks:
        bits = int.from_bytes(chunks["VP8L"][1:5], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    frame = chunks["VP8 "]
    return (int.from_bytes(frame[6:8], "little") & 0x3FFF,
            int.from_bytes(frame[8:10], "little") & 0x3FFF)


def _strip_html_comments(html):
    return re.sub(r"<!--.*?-->", "", html, flags=re.S)


def _anchor_pairs(html):
    """List of (quote, href) for every <a> tag, in document order."""
    html = _strip_html_comments(html)
    return re.findall(
        r'<a\b[^>]*?\bhref\s*=\s*(["\'])(.*?)\1',
        html,
        flags=re.S | re.I,
    )


def _nav_block(html):
    html = _strip_html_comments(html)
    return "\n".join(re.findall(r"<nav\b.*?</nav>", html, flags=re.S | re.I))


def _local_refs(html):
    """Every local href/src value (external/data/hash/mailto/tel excluded)."""
    html = _strip_html_comments(html)
    refs = []
    for attr in ("href", "src"):
        refs.extend(
            val
            for _q, val in re.findall(
                r'\b' + attr + r'\s*=\s*(["\'])(.*?)\1',
                html,
                flags=re.S | re.I,
            )
        )
    return [v for v in refs if v and not v.startswith(EXTERNAL_PREFIXES)]


def _class_tokens(html):
    html = _strip_html_comments(html)
    pairs = re.findall(r'\bclass\s*=\s*(["\'])(.*?)\1', html, flags=re.S | re.I)
    return {token for _q, val in pairs for token in val.split()}


def _normalized_text(text):
    return re.sub(r"\s+", "", text.lower())


def _visible_text(html_text):
    """Page text with tags, comments and entities resolved, whitespace collapsed."""
    text = re.sub(r"<[^>]+>", " ", _strip_html_comments(html_text))
    return re.sub(r"\s+", " ", html.unescape(text))


def _section(html_text, open_tag):
    """The element that starts with open_tag, up to its first close tag."""
    html_text = _strip_html_comments(html_text)
    start = html_text.index(open_tag)
    tag = re.match(r"<(\w+)", open_tag).group(1)
    return html_text[start:html_text.index("</%s>" % tag, start)]


class StructureTests(unittest.TestCase):
    """The site is four directory-rooted pages."""

    def test_required_pages_exist(self):
        for name, rel in PAGES.items():
            with self.subTest(page=name):
                self.assertTrue(
                    os.path.isfile(_path(rel)),
                    "required page %r is missing" % rel,
                )

    def test_every_track_record_label_has_a_year_range(self):
        home = _read_page("home")
        labels = re.findall(
            r'<div class="track-label">(.*?)</div>', home, flags=re.S | re.I
        )

        self.assertTrue(labels, "home page needs Track record labels")
        for label in labels:
            text = html.unescape(re.sub(r"<[^>]+>", "", label))
            with self.subTest(label=text):
                self.assertRegex(text, r"\d{4}–(?:\d{4}|present)")

    def test_favicon_links_and_assets_exist(self):
        self.assertTrue(os.path.isfile(_path("favicon.svg")))
        self.assertTrue(os.path.isfile(_path("favicon.ico")))
        touch_icon_path = _path("apple-touch-icon.png")
        self.assertTrue(os.path.isfile(touch_icon_path))
        with open(touch_icon_path, "rb") as touch_icon:
            png_header = touch_icon.read(24)
        self.assertEqual(png_header[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(png_header[12:16], b"IHDR")
        self.assertEqual((180, 180), struct.unpack(">II", png_header[16:24]))
        icon_pages = {**PAGES, "404": "404.html"}
        for name, rel in icon_pages.items():
            with self.subTest(page=name):
                with open(_path(rel), encoding="utf-8") as page_file:
                    html = page_file.read()
                self.assertRegex(
                    html,
                    r'<link rel="icon" href="/favicon\.svg" type="image/svg\+xml">',
                )
                self.assertRegex(
                    html,
                    r'<link rel="icon" href="/favicon\.ico" sizes="any">',
                )
                self.assertRegex(
                    html,
                    r'<link rel="apple-touch-icon" href="/apple-touch-icon\.png">',
                )


class LcpImagePriorityTests(unittest.TestCase):
    """Desktop LCP images stay eager and receive high fetch priority."""

    @staticmethod
    def _image_in_figure(html, figure_class):
        figure = re.search(
            r'<figure class="' + re.escape(figure_class) + r'">.*?</figure>',
            html,
            flags=re.S,
        )
        if figure is None:
            raise AssertionError("figure %r is missing" % figure_class)
        image = re.search(r"<img\b[^>]*>", figure.group(0), flags=re.I)
        if image is None:
            raise AssertionError("figure %r has no image" % figure_class)
        return image.group(0)

    def test_desktop_lcp_images_are_eager_and_prioritized(self):
        home = _read_page("home")
        portrait = self._image_in_figure(home, "portrait")
        self.assertIn('fetchpriority="high"', portrait)
        self.assertNotRegex(portrait, r'\bloading\s*=\s*["\']lazy["\']')


class SitemapTests(unittest.TestCase):
    def test_sitemap_lists_every_page_canonical(self):
        sitemap = ET.parse(_path("sitemap.xml"))
        locations = [
            node.text
            for node in sitemap.findall(
                ".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
            )
        ]
        canonicals = []
        for name in PAGES:
            html = _read_page(name)
            matches = re.findall(
                r'<link\b[^>]*\brel="canonical"[^>]*\bhref="([^"]+)"',
                html,
                flags=re.I,
            )
            self.assertEqual(len(matches), 1, "%s needs one canonical URL" % name)
            canonicals.extend(matches)
        self.assertCountEqual(locations, canonicals)
        self.assertEqual(len(locations), 4)


class CanonicalUrlTests(unittest.TestCase):
    """Each page names its public URL, with trailing slashes enforced by Vercel."""

    def test_each_page_has_self_referencing_canonical_in_head(self):
        urls = {
            "home": "https://giulioni.com/",
            "resume": "https://giulioni.com/career/",
            "work": "https://giulioni.com/work/",
            "media": "https://giulioni.com/media/",
        }
        for name, url in urls.items():
            with self.subTest(page=name):
                html = _strip_html_comments(_read_page(name))
                head = re.search(r"<head\b[^>]*>(.*?)</head>", html, re.S | re.I)
                self.assertIsNotNone(head, "%s must have a head element" % name)
                canonicals = re.findall(
                    r'<link\b[^>]*\brel="canonical"[^>]*>',
                    head.group(1),
                    flags=re.I,
                )
                self.assertEqual(
                    ['<link rel="canonical" href="%s">' % url],
                    canonicals,
                    "%s must have exactly one self-referencing canonical" % name,
                )

    def test_vercel_enforces_trailing_slashes(self):
        with open(_path("vercel.json"), encoding="utf-8") as fh:
            vercel = json.load(fh)
        self.assertIs(vercel.get("trailingSlash"), True)

    def test_vercel_redirects_www_to_apex(self):
        with open(_path("vercel.json"), encoding="utf-8") as fh:
            vercel = json.load(fh)
        self.assertEqual(
            vercel.get("redirects"),
            [
                {
                    "source": "/(.*)",
                    "has": [{"type": "host", "value": "www.giulioni.com"}],
                    "destination": "https://giulioni.com/$1",
                    "permanent": True,
                }
            ],
        )


class NavigationTests(unittest.TestCase):
    """Approved primary nav: Home, Resume, Selected work, Contact."""

    PRIMARY_NAV_LABELS = ("Home", "Resume", "Selected work", "Contact")
    PRIMARY_NAV_HREFS = (
        "/",
        "/career/",
        "/work/",
        "mailto:nick@giulioni.com",
    )

    def test_each_page_has_approved_primary_navigation(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            hrefs = {h for _q, h in _anchor_pairs(_nav_block(html))}
            nav_block = _nav_block(html)
            with self.subTest(page=name):
                self.assertTrue(
                    "/" in hrefs or "/index.html" in hrefs,
                    "%s nav missing Home link (/ or /index.html)" % name,
                )
                self.assertIn(
                    "/career/", hrefs, "%s nav missing /career/ (Resume)" % name
                )
                self.assertIn(
                    "/work/", hrefs, "%s nav missing /work/ (Selected work)" % name
                )
                self.assertIn(
                    "mailto:nick@giulioni.com",
                    hrefs,
                    "%s nav missing Contact mailto link" % name,
                )
                # The four primary labels must appear inside the nav block.
                for label in self.PRIMARY_NAV_LABELS:
                    self.assertIn(
                        ">" + label + "<",
                        nav_block,
                        "%s nav missing primary label %r" % (name, label),
                    )

    def test_media_is_not_in_primary_nav(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            nav_block = _nav_block(html)
            with self.subTest(page=name):
                self.assertNotIn(
                    ">Media<",
                    nav_block,
                    "%s primary nav must not contain literal Media label" % name,
                )
                self.assertNotIn(
                    "/media/",
                    nav_block,
                    "%s primary nav must not link /media/" % name,
                )


class HomeTests(unittest.TestCase):
    """Home leads with the T&H role and tells owners why to work with Nick."""

    def _hero(self):
        return _section(_read_page("home"), '<section class="home-hero"')

    def test_home_title_leads_with_th_role(self):
        self.assertIn(
            "<title>Nick Giulioni | Director of Sales and Marketing,"
            " T&amp;H Realty Services</title>",
            _read_page("home"),
        )

    def test_hero_tagline_role_and_th_link(self):
        hero = self._hero()
        self.assertIn('<h1 class="hero-lede">If you can\'t sell it, rent it.</h1>', hero)
        self.assertIn(TH_ROLE, hero)
        self.assertIn('href="%s"' % TH_URL, hero)

    def test_hero_has_exactly_one_primary_cta_to_lets_talk(self):
        hero = self._hero()
        buttons = re.findall(r'<a class="btn btn-primary" href="([^"]+)">([^<]+)</a>', hero)
        self.assertEqual(
            buttons, [(TH_LETS_TALK, "Talk to me about managing your rental")]
        )
        self.assertNotIn("btn-secondary", hero)

    def test_home_page_has_only_one_primary_button(self):
        html = _strip_html_comments(_read_page("home"))
        self.assertEqual(html.count("btn-primary"), 1)

    def test_hero_secondary_link_is_quiet_rental_analysis(self):
        self.assertIn(
            '<a class="hero-link" href="%s">' % TH_RENTAL_ANALYSIS, self._hero()
        )

    def test_home_no_longer_reads_as_a_job_search(self):
        text = _visible_text(_read_page("home")).lower()
        for phrase in ("forward-deployed", "looking for", "new opportunity",
                       "download resume", "status quo"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_track_record_leads_with_th_role_copy(self):
        html = _strip_html_comments(_read_page("home"))
        labels = re.findall(r'<div class="track-label">([^<]+)<', html)
        self.assertEqual(labels[0], "T&amp;H Realty Services")
        lead = html[html.index('<div class="track-row track-row-lead">'):]
        lead = lead[:lead.index('<div class="track-row">')]
        self.assertIn("%s, Nov 2026–present" % TH_ROLE, lead)
        for copy in (TH_DESCRIPTION, TH_SCOPE, 'href="%s"' % TH_URL):
            with self.subTest(copy=copy):
                self.assertIn(copy, lead)

    def test_home_has_track_record_section(self):
        html = _strip_html_comments(_read_page("home"))
        self.assertIn("track-record", html)
        for label in ("T&amp;H Realty Services", "Ballpark", "Off Leash Investments",
                      "Off Leash Construction", "Meta", "Corsair", "Razer"):
            with self.subTest(label=label):
                self.assertIn('<div class="track-label">%s<' % label, html)

    def test_each_track_record_row_is_one_line(self):
        html = _strip_html_comments(_read_page("home"))
        rows = re.findall(r'<div class="track-row[^"]*">(.*?)\n      </div>', html, re.S)
        self.assertEqual(len(rows), 7)
        for row in rows:
            with self.subTest(row=row[:60]):
                self.assertEqual(row.count('class="track-line"'), 1)
                self.assertNotRegex(row, r"track-(problem|did|outcome)")

    def test_home_tells_the_owner_story(self):
        story = _section(_read_page("home"), '<section class="owner-story"')
        self.assertIn("owner's side of the table", story)
        self.assertIn("since 2016", story)

    def test_band_is_indy_rei_guest_credit_with_three_episodes(self):
        band = _section(_read_page("home"), '<aside class="product-band"')
        self.assertIn(
            'Guest on <a href="%s">Indy REI with T&amp;H Realty</a>' % INDY_REI_SHOW,
            band,
        )
        self.assertNotRegex(_visible_text(band).lower(), r"\bhost(ed)?\b")
        links = re.findall(
            r'<li><a href="([^"]+)">([^<]+)</a>'
            r'<span class="episode-date">([^<]+)</span></li>', band
        )
        self.assertEqual(
            links, [(url, title, date) for title, url, date in INDY_REI_EPISODES]
        )

    def test_home_has_one_ballpark_card_and_no_estimate_image(self):
        html = _strip_html_comments(_read_page("home"))
        self.assertEqual(html.count('<article class="ballpark-card">'), 1)
        card = _section(html, '<article class="ballpark-card">')
        self.assertIn("<h2>%s</h2>" % BALLPARK_CARD_TITLE, card)
        self.assertIn("<p>%s</p>" % BALLPARK_CARD_COPY, card)
        self.assertIn('href="https://ballpark.build"', card)
        self.assertNotIn("<img", card)
        self.assertNotIn("ballpark-estimate", html)
        self.assertNotIn("product-image", html)

    def test_home_btn_classes_meet_coarse_pointer_44px_rule(self):
        css = _read_css()
        coarse = re.search(r"@media \(pointer: coarse\)\s*\{(.*?)\n\}", css, re.S)
        self.assertIsNotNone(coarse, "styles.css must define @media (pointer: coarse)")
        body = coarse.group(1)
        self.assertIn(".btn", body, "coarse-pointer rule must cover .btn buttons")
        self.assertRegex(
            body,
            r"min-height:\s*44px",
            "coarse-pointer rule must set min-height: 44px",
        )

    def test_home_carries_meta_unit_growth_figures(self):
        html = _strip_html_comments(_read_page("home"))
        for token in ("Meta", "Portal", "Oculus", "300%", "450%"):
            with self.subTest(token=token):
                self.assertIn(
                    token,
                    html,
                    "home must carry Meta tenure token %r" % token,
                )
        self.assertRegex(
            html,
            r"units.{0,20}300%|300%.{0,20}units",
            "home must mention units near 300% figure",
        )
        self.assertRegex(
            html,
            r"units.{0,20}450%|450%.{0,20}units",
            "home must mention units near 450% figure",
        )


class ResponsiveImageTests(unittest.TestCase):
    """Each picture has local WebP candidates and a resized legacy fallback."""

    def test_variants_exist_and_are_referenced(self):
        widths = [160, 200, 320, 348, 400, 636]
        self.assertEqual(re.findall(r"<picture>", _read_page("work")), [])
        pictures = re.findall(r"<picture>.*?</picture>", _read_page("home"), re.S)
        self.assertEqual(len(pictures), 1)
        tags = re.findall(r"<(?:source|img)\b[^>]*>", pictures[0])
        self.assertEqual(len(tags), 2)
        source, fallback = [dict(re.findall(r'([\w-]+)="([^"]*)"', tag)) for tag in tags]
        self.assertEqual(source["type"], "image/webp")
        self.assertEqual(source["sizes"], fallback["sizes"])
        self.assertTrue(source["sizes"])
        for attributes, fmt in ((source, "webp"), (fallback, "jpg")):
            candidates = [value.strip() for value in attributes["srcset"].split(",")]
            self.assertEqual(candidates, [
                "/assets/portrait-nick-%s.%s %sw" % (width, fmt, width)
                for width in widths
            ])
            for candidate in candidates:
                path = _path(candidate.split()[0].lstrip("/"))
                self.assertTrue(os.path.isfile(path), path)
                self.assertGreater(os.path.getsize(path), 0)
        self.assertIn(fallback["src"], [
            candidate.split()[0] for candidate in fallback["srcset"].split(", ")
        ])
        self.assertTrue(fallback["alt"])
        self.assertEqual((fallback["width"], fallback["height"]), ("636", "954"))
        self.assertIsNone(fallback.get("loading"))

    def test_old_ballpark_estimate_image_is_gone(self):
        """No estimate or signed-in screenshots of Ballpark ship on the site."""
        self.assertEqual(glob.glob(_path("assets/ballpark-estimate*")), [])
        for name in PAGES:
            with self.subTest(page=name):
                self.assertNotIn("ballpark-estimate", _read_page(name))


class ShareCardTests(unittest.TestCase):
    """All four pages ship portrait+title share cards.

    Cards carry Nick's portrait only: no child faces in any public media."""

    CARDS = {
        "home": "og-home.png",
        "resume": "og-career.png",
        "work": "og-work.png",
        "media": "og-media.png",
    }

    PAGE_URLS = {
        "home": "https://giulioni.com/",
        "resume": "https://giulioni.com/career/",
        "work": "https://giulioni.com/work/",
        "media": "https://giulioni.com/media/",
    }

    def test_share_card_images_exist_at_1200x630(self):
        for card in sorted(set(self.CARDS.values())):
            path = os.path.join(REPO_ROOT, "assets", card)
            with self.subTest(card=card):
                self.assertTrue(os.path.isfile(path), "missing share card %r" % card)
                with open(path, "rb") as handle:
                    header = handle.read(24)
                self.assertEqual(
                    header[:8], b"\x89PNG\r\n\x1a\n", "%r must be PNG" % card
                )
                width = int.from_bytes(header[16:20], "big")
                height = int.from_bytes(header[20:24], "big")
                self.assertEqual((width, height), (1200, 630))

    def test_pages_declare_absolute_card_urls_and_twitter_equivalents(self):
        for name, card in self.CARDS.items():
            html = _strip_html_comments(_read_page(name))
            url = "https://giulioni.com/assets/%s" % card
            with self.subTest(page=name):
                for tag in (
                    '<meta property="og:image" content="%s">' % url,
                    '<meta property="og:url" content="%s">' % self.PAGE_URLS[name],
                    '<meta property="og:image:width" content="1200">',
                    '<meta property="og:image:height" content="630">',
                    '<meta name="twitter:card" content="summary_large_image">',
                    '<meta name="twitter:image" content="%s">' % url,
                ):
                    self.assertIn(tag, html, "%s missing %r" % (name, tag))
                self.assertRegex(
                    html,
                    r'<meta property="og:image:alt" content="[^"]{10,}">',
                    "%s needs og:image:alt text" % name,
                )

    def test_media_page_ships_share_card(self):
        html = _strip_html_comments(_read_page("media"))
        self.assertIn(
            '<meta property="og:image" content="https://giulioni.com/assets/og-media.png">',
            html,
        )


class MixedSignalTests(unittest.TestCase):
    """Home and Selected work must not carry Best Notes, venues, or 48-hour
    STR claims."""

    MIXED_TOKENS = (
        "Best Notes",
        "The Wilds",
        "Laural Mill",
        "48 hours",
    )

    def test_home_and_work_carry_no_mixed_signal_tokens(self):
        for page in ("home", "work"):
            normalized = _normalized_text(_strip_html_comments(_read_page(page)))
            for token in self.MIXED_TOKENS:
                with self.subTest(page=page, token=token):
                    self.assertNotIn(_normalized_text(token), normalized)


def _pdf_text():
    return subprocess.run(
        ["pdftotext", "-layout", _path("assets/nick-giulioni-resume.pdf"), "-"],
        check=True, capture_output=True, text=True,
    ).stdout


class NeverOnSiteTests(unittest.TestCase):
    """Content the Oct 30, 2026 brief rules out on every page and in the PDF."""

    FORBIDDEN = (
        # The T&H deal, people and internals.
        r"\bJeremy\b", r"\bTallman\b", r"\bacqui(?:re|red|sition)\b",
        r"\bsale of\b", r"\bownership\b", r"\bhandbook\b", r"\bmeetings?\b",
        r"\bcompensation\b", r"\bsalary\b", r"\bcommission\b", r"\bbonus\b",
        r"\blicen[cs]e[ds]?\b", r"\btargets?\b", r"\bquota\b", r"\bschedule\b",
        # Family and personal details.
        r"\bBailey\b", r"\bdaughter\b", r"\bson\b", r"\bwife\b",
        r"\brobbe(?:d|ry)\b", r"\blawsuit\b", r"\blegal\b",
        r"\bperformance review\b",
        # Street addresses.
        r"\b\d+\s+\w+(?:\s\w+)?\s(?:St|Street|Ave|Avenue|Rd|Road|Dr|Drive|Blvd|Ln|Lane)\b",
        # Ballpark vendors and AI model names.
        r"\bOpenAI\b", r"\bGPT", r"\bClaude\b", r"\bAnthropic\b", r"\bGemini\b",
        # The unapproved Part 2 podcast episode.
        r"Part 2", r"part-2",
    )

    def _sources(self):
        for name in PAGES:
            page = _read_page(name)
            hrefs = " ".join(h for _q, h in _anchor_pairs(page))
            yield name, _visible_text(page) + " " + hrefs
        yield "resume-pdf", _pdf_text()

    def test_no_forbidden_content_on_any_page_or_pdf(self):
        for name, text in self._sources():
            for pattern in self.FORBIDDEN:
                with self.subTest(source=name, pattern=pattern):
                    self.assertNotRegex(text, re.compile(pattern, re.I))

    def test_portrait_is_the_only_photo(self):
        """No child photos or other people: Nick's portrait only."""
        for name in PAGES:
            with self.subTest(page=name):
                for src in re.findall(r'\bsrcs?e?t?="([^"]+)"', _read_page(name)):
                    for candidate in src.split(","):
                        self.assertTrue(
                            candidate.strip().startswith("/assets/portrait-nick"),
                            candidate,
                        )


class ResumeTests(unittest.TestCase):
    """/career/ renders the recruiter-first Resume."""

    REQUIRED_SECTIONS = (
        "Summary",
        "Experience",
        "Earlier experience",
        "Operating history",
        "Education",
    )

    def test_resume_title_and_metadata(self):
        html = _read_page("resume")
        self.assertIn("<title>Resume | Nick Giulioni</title>", html)
        self.assertIn(
            '<meta property="og:title" content="Resume | Nick Giulioni">', html
        )

    def test_resume_has_required_sections(self):
        html = _strip_html_comments(_read_page("resume"))
        for section in self.REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(
                    section,
                    html,
                    "resume must include section heading %r" % section,
                )

    def test_resume_carries_contact_block_and_pdf_link(self):
        html = _read_page("resume")
        self.assertIn("mailto:nick@giulioni.com", html)
        self.assertIn("linkedin.com/in/nickgiulioni", html)
        self.assertIn(
            'href="/assets/nick-giulioni-resume.pdf"', html,
            "resume must link the downloadable PDF"
        )
        self.assertIn(
            'download="Nick-Giulioni-Resume.pdf"', html,
            "resume PDF link must carry the canonical download filename",
        )

    def test_th_role_leads_experience(self):
        html = _strip_html_comments(_read_page("resume"))
        first = _section(html, '<article class="career-entry')
        self.assertIn("<h3>T&amp;H Realty Services</h3>", first)
        self.assertIn('<p class="role">%s</p>' % TH_ROLE, first)
        self.assertIn('<p class="date">Nov 2026–present</p>', first)
        for copy in (TH_DESCRIPTION, TH_SCOPE, 'href="%s"' % TH_URL):
            with self.subTest(copy=copy):
                self.assertIn(copy, first)

    def test_resume_no_longer_reads_as_a_job_search(self):
        text = _visible_text(_read_page("resume")).lower()
        for phrase in ("forward-deployed", "looking for", "new opportunity",
                       "target role", "ballpark bridge"):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_every_other_role_is_one_line(self):
        html = _strip_html_comments(_read_page("resume"))
        entries = re.findall(r'<article class="career-entry[^"]*">.*?</article>', html, re.S)
        names = [re.search(r"<h3>([^<]+)</h3>", e).group(1) for e in entries]
        self.assertEqual(names, [
            "T&amp;H Realty Services", "Ballpark", "Off Leash Construction",
            "Facebook / Meta", "Corsair", "Razer", "TP-LINK USA", "D-Link",
            "Arclyte Technologies", "Newegg.com", "Off Leash Investments",
            "The Wilds Wedding Venue", "Laural Mill",
        ])
        for name, entry in zip(names[1:], entries[1:]):
            with self.subTest(role=name):
                detail = entry[entry.index('<div class="entry-detail">'):]
                self.assertEqual(detail.count("<p>"), 1)
                self.assertNotIn("<li>", detail)

    def test_operating_businesses_stay_short(self):
        html = _strip_html_comments(_read_page("resume"))
        section = html[html.index("Operating history"):html.index("Education")]
        lines = re.findall(r'<div class="entry-detail"><p>(.*?)</p></div>', section)
        self.assertEqual(len(lines), 3)
        for line in lines:
            with self.subTest(line=line):
                self.assertLessEqual(len(line.split()), 8)

    def test_resume_preserves_truthful_titles_dates_metrics(self):
        html = _read_page("resume")
        for token in (
            "$150 million",
            "team of six",
            "$3 million",
            "3,000+ doors",
            "Oct 2023",
            "Jul 2026",
            "Nov 2019",
            "Mar 2022",
            "Apr 2016",
            "Oct 2017",
            "May 2015",
            "Jul 2014",
            "Jun 2013",
            "Jun 2014",
            "Dec 2011",
            "May 2013",
        ):
            with self.subTest(token=token):
                self.assertIn(
                    token,
                    html,
                    "resume must preserve truthful token %r" % token,
                )

    def test_resume_off_leash_title_is_ceo_only(self):
        html = _read_page("resume")
        self.assertNotIn(
            "Brand Ambassador",
            html,
            "Off Leash Construction title must be CEO only, not Brand Ambassador"
        )

    def test_resume_education_attendance_without_degree_or_major(self):
        html = _strip_html_comments(_read_page("resume"))
        self.assertIn("University of Southern California", html)
        self.assertIn("Marshall School of Business", html)
        self.assertIn("2009", html)
        self.assertIn("2012", html)
        forbidden = ("B.S.", "B.A.", "BS", "BA", "Bachelor", "MBA", "major")
        for token in forbidden:
            self.assertNotIn(
                token,
                html,
                "resume education must not claim degree or major %r" % token,
            )

    def test_resume_carries_meta_unit_growth_figures(self):
        html = _strip_html_comments(_read_page("resume"))
        for token in ("Facebook / Meta", "Portal", "Oculus", "300%", "450%"):
            with self.subTest(token=token):
                self.assertIn(
                    token,
                    html,
                    "resume must carry Meta tenure token %r" % token,
                )
        self.assertRegex(
            html,
            r"units.{0,20}300%|300%.{0,20}units",
            "resume must mention units near 300% figure",
        )
        self.assertRegex(
            html,
            r"units.{0,20}450%|450%.{0,20}units",
            "resume must mention units near 450% figure",
        )


class JobTitleTests(unittest.TestCase):
    """Home and career job titles consistently abbreviate Senior as Sr."""

    def test_job_titles_do_not_spell_out_senior(self):
        for page in ("home", "resume"):
            with self.subTest(page=page):
                html = _strip_html_comments(_read_page(page))
                titles = re.findall(
                    r'<(?:p|span)\b[^>]*\bclass="(?:role|track-years)"[^>]*>'
                    r'(.*?)</(?:p|span)>',
                    html,
                    flags=re.S,
                )
                self.assertTrue(titles, "%s must contain job titles" % page)
                for title in titles:
                    self.assertNotRegex(title, r"\bSenior\s")

    def test_corsair_and_razer_use_approved_abbreviated_titles(self):
        for page in ("home", "resume"):
            for title in ("Sr. Ecommerce Sales Manager", "Sr. Ecommerce Manager"):
                with self.subTest(page=page, title=title):
                    self.assertIn(title, _read_page(page))


class SelectedWorkTests(unittest.TestCase):
    """/work/ renders one Ballpark case + one Also shipped + three receipts."""

    def test_work_title_and_metadata(self):
        html = _read_page("work")
        self.assertIn("<title>Selected work | Nick Giulioni</title>", html)
        self.assertIn(
            '<meta property="og:title" content="Selected work | Nick Giulioni">',
            html,
        )

    def test_ballpark_case_carries_four_labelled_facts(self):
        html = _read_page("work")
        ballpark = re.search(
            r'<article\b[^>]*data-project="ballpark".*?</article>', html, re.S
        )
        self.assertIsNotNone(ballpark, "Ballpark case article missing")
        block = ballpark.group(0)
        facts = re.findall(r'data-fact="([^"]+)"', block)
        self.assertEqual(len(facts), 4)
        self.assertEqual(
            sorted(facts),
            sorted(["context", "problem", "built", "status"]),
            "Ballpark must carry Operating context / Problem / Built / Status",
        )
        forbidden_phrases = (
            "public launch",
            "publicly launched",
            "ROI",
            "savings",
            "customer count",
            "adoption",
            "live at",
        )
        for phrase in forbidden_phrases:
            self.assertNotIn(
                phrase.lower(),
                block.lower(),
                "Ballpark must not carry claim %r" % phrase,
            )

    def test_ballpark_case_matches_market_intelligence_positioning(self):
        html = _strip_html_comments(_read_page("work"))
        block = _section(html, '<article class="work-case" data-project="ballpark">')
        self.assertIn("Market intelligence for Central Indiana real estate pros", block)
        self.assertIn("AI repair estimates", block)
        self.assertIn('href="https://ballpark.build"', block)
        self.assertNotIn("<img", block)

    def test_a_little_true_is_compact_also_shipped_with_one_link(self):
        html = _strip_html_comments(_read_page("work"))
        self.assertIn("Also shipped", html)
        self.assertIn('href="https://alittletrue.com"', html)
        self.assertEqual(html.count('href="https://alittletrue.com"'), 1)
        also = re.search(
            r'<article\b[^>]*data-project="a-little-true".*?</article>', html, re.S
        )
        self.assertIsNotNone(also)
        block = also.group(0)
        urls = re.findall(r'href="(https?://[^"]+)"', block)
        self.assertEqual(urls, ["https://alittletrue.com"])

    def test_work_receipts_are_exactly_three(self):
        html = _strip_html_comments(_read_page("work"))
        receipts_block = re.search(
            r'<section\s+class="receipts">.*?</section>', html, re.S
        )
        self.assertIsNotNone(receipts_block)
        block = receipts_block.group(0)
        numbers = re.findall(r"<strong>([^<]+)</strong>", block)
        self.assertEqual(sorted(numbers), sorted(["3,000+", "$3M+", "$150M"]))
        for forbidden in (
            "48 hours",
            "Best Notes",
            "The Wilds",
            "Laural Mill",
            "Off Leash Investments",
            "short-term rental",
        ):
            self.assertNotIn(
                forbidden,
                block,
                "receipts must not carry %r" % forbidden,
            )


class MediaArchiveTests(unittest.TestCase):
    """/media/ lists every approved appearance and stays out of the
    primary nav."""

    def test_media_title_and_metadata(self):
        html = _read_page("media")
        self.assertIn("<title>Podcasts and talks | Nick Giulioni</title>", html)
        self.assertIn(
            '<meta property="og:title" content="Podcasts and talks | Nick Giulioni">',
            html,
        )

    def test_entries_are_the_approved_titles_in_order(self):
        html = _strip_html_comments(_read_page("media"))
        found = re.findall(
            r'<p class="episode-title"><a href="([^"]+)">([^<]+)</a></p>', html
        )
        self.assertEqual(found, [(url, title) for title, url in MEDIA_ENTRIES])

    def test_indy_rei_entries_are_guest_credits_with_dates(self):
        html = _strip_html_comments(_read_page("media"))
        for title, url, date in INDY_REI_EPISODES:
            with self.subTest(title=title):
                entry = re.search(
                    r'<article class="media-entry">(?:(?!</article>).)*href="%s"'
                    r'(?:(?!</article>).)*</article>' % re.escape(url),
                    html, re.S,
                ).group(0)
                self.assertIn("Indy REI with T&amp;H Realty (guest)", entry)
                self.assertIn('<p class="media-date">%s</p>' % date, entry)
        self.assertNotRegex(_visible_text(html).lower(), r"\bhost(ed)?\b")

    def test_intrigue_podcast_show_name(self):
        html = _strip_html_comments(_read_page("media"))
        entry = re.search(
            r'<article class="media-entry">(?:(?!</article>).)*'
            r'href="https://www\.youtube\.com/watch\?v=dv72SopKqeM"'
            r'(?:(?!</article>).)*</article>',
            html,
            flags=re.S,
        )
        self.assertIsNotNone(entry, "The Intrigue episode must stay on /media/")
        self.assertIn("The Intrigue Podcast", entry.group(0))

    def test_each_approved_url_appears_exactly_once_as_href(self):
        html = _strip_html_comments(_read_page("media"))
        for _title, url in MEDIA_ENTRIES:
            with self.subTest(url=url):
                self.assertEqual(
                    html.count('href="%s"' % url),
                    1,
                    "Earlier media must link %r exactly once" % url,
                )

    def test_no_external_image_assets_on_media(self):
        html = _strip_html_comments(_read_page("media"))
        self.assertNotRegex(
            html,
            r"<img\b",
            "Earlier media must not carry any <img> tags (no media-logo assets)",
        )


def _pdf_link_urls(data):
    """Read literal URI annotations, including Flate-compressed object streams."""
    chunks = [data]
    for stream in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, re.S):
        try:
            chunks.append(zlib.decompress(stream[1]))
        except zlib.error:
            continue
    urls = []
    for chunk in chunks:
        for uri in re.finditer(rb"/URI\s*\(((?:\\.|[^\\)])*)\)", chunk, re.S):
            value = re.sub(
                rb"\\([0-7]{1,3}|\r\n|[\s\S])",
                lambda match: (
                    bytes([int(match[1], 8)]) if match[1][:1] in b"01234567"
                    else {b"n": b"\n", b"r": b"\r", b"t": b"\t",
                          b"b": b"\b", b"f": b"\f", b"\n": b"",
                          b"\r": b"", b"\r\n": b""}.get(match[1], match[1])
                ),
                uri[1],
            )
            urls.append(value.decode("utf-8"))
    return urls


class ResumePdfTests(unittest.TestCase):
    """The downloadable resume PDF is generated, two pages, and contains
    the required tokens."""

    REQUIRED_PDF_TOKENS = (
        "resume",
        "nick@giulioni.com",
        "linkedin.com/in/nickgiulioni",
        "ballpark",
        "director of sales and marketing",
        "t&h realty services",
        "nov 2026",
        "investor community",
    )

    @staticmethod
    def _pdf_path():
        return _path("assets/nick-giulioni-resume.pdf")

    def test_pdf_exists(self):
        self.assertTrue(
            os.path.isfile(self._pdf_path()),
            "resume PDF must be committed at assets/nick-giulioni-resume.pdf",
        )

    def test_pdf_links_are_absolute_and_public(self):
        urls = _pdf_link_urls(Path(self._pdf_path()).read_bytes())
        self.assertTrue(urls, "resume PDF must contain readable link annotations")
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(urlsplit(url).scheme, "PDF links must be absolute")
                self.assertNotRegex(url.lower(), r"127\.0\.0\.1|localhost|0\.0\.0\.0")
        self.assertIn("https://giulioni.com/work/", urls)
        self.assertIn(TH_URL, urls)
        for contact in SOCIAL_HREFS:
            self.assertIn(contact, urls)

    def test_pdf_link_reader_handles_compressed_and_escaped_uris(self):
        annotations = (rb"<< /URI (http://local\150ost/work/) >>"
                       rb"<< /URI (https://giulioni.com/work/\(example\)) >>")
        for payload in (annotations, b"<< /Filter /FlateDecode >>\nstream\n"
                        + zlib.compress(annotations) + b"\nendstream"):
            self.assertEqual(_pdf_link_urls(payload), [
                "http://localhost/work/", "https://giulioni.com/work/(example)",
            ])

    def test_pdf_is_at_most_two_pages(self):
        if not os.path.isfile(self._pdf_path()):
            self.skipTest("PDF not yet generated; run tools/regen_resume_pdf.sh")
        info = subprocess.run(
            ["pdfinfo", self._pdf_path()],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        match = re.search(r"^Pages:\s+(\d+)", info, re.M)
        self.assertIsNotNone(match, "pdfinfo must report a Pages count")
        pages = int(match.group(1))
        self.assertLessEqual(pages, 2, "resume PDF must be at most 2 pages")

    def test_pdf_text_contains_required_tokens(self):
        if not os.path.isfile(self._pdf_path()):
            self.skipTest("PDF not yet generated; run tools/regen_resume_pdf.sh")
        text = subprocess.run(
            ["pdftotext", "-layout", self._pdf_path(), "-"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        normalized = _normalized_text(text)
        for token in self.REQUIRED_PDF_TOKENS:
            with self.subTest(token=token):
                self.assertIn(
                    _normalized_text(token),
                    normalized,
                    "resume PDF must contain %r" % token,
                )


class ResumePdfRegenTests(unittest.TestCase):
    @staticmethod
    def _tiny_pdf(text, pages=1, uri="https://giulioni.com/work/"):
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            ("<< /Type /Pages /Kids [%s] /Count %d >>" % (
                " ".join("%d 0 R" % (5 + i) for i in range(pages)), pages
            )).encode(),
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        ]
        content = ("BT /F1 12 Tf 40 750 Td (%s) Tj ET" % text).encode()
        objects.append(b"<< /Length %d >>\nstream\n" % len(content)
                       + content + b"\nendstream")
        objects.extend([b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                        b"/Resources << /Font << /F1 3 0 R >> >> /Contents 4 0 R "
                        + ("/Annots [%d 0 R] >>" % (5 + pages)).encode()] * pages)
        objects.append(("<< /Type /Annot /Subtype /Link /Rect [40 730 200 750] "
                        "/A << /S /URI /URI (%s) >> >>" % uri).encode())
        pdf = b"%PDF-1.4\n"
        offsets = [0]
        for number, obj in enumerate(objects, 1):
            offsets.append(len(pdf))
            pdf += b"%d 0 obj\n" % number + obj + b"\nendobj\n"
        xref = len(pdf)
        pdf += b"xref\n0 %d\n0000000000 65535 f \n" % len(offsets)
        for offset in offsets[1:]:
            pdf += b"%010d 00000 n \n" % offset
        pdf += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(offsets), xref)).encode()
        return pdf

    def test_chrome_exit_requires_a_fresh_valid_pdf(self):
        valid = self._tiny_pdf(
            "Resume nick@giulioni.com linkedin.com/in/nickgiulioni Ballpark"
        )
        cases = (
            ("missing", None, 2, False, "no fresh, non-empty PDF"),
            ("empty", b"", 0, False, "no fresh, non-empty PDF"),
            ("valid_teardown", valid, 2, True, "Chrome exited 2"),
            ("valid", valid, 0, True, "Wrote"),
            ("invalid", b"not a PDF", 2, False, "pdfinfo"),
            ("missing_text", self._tiny_pdf("Resume"), 2, False, "missing required token"),
            ("too_many_pages", self._tiny_pdf("Resume", pages=3), 2, False, "page count"),
            ("stale", valid, 2, False, "no fresh, non-empty PDF"),
        ) + tuple(
            ("bad_link_%d" % i, self._tiny_pdf(
                "Resume nick@giulioni.com linkedin.com/in/nickgiulioni Ballpark",
                uri=url,
            ), 0, False, "PDF link validation failed")
            for i, url in enumerate((
                "http://127.0.0.1:58890/work/", "http://localhost/work/",
                "http://0.0.0.0/work/", "/work/", "work/",
                "//giulioni.com/work/",
            ))
        )
        for name, payload, chrome_status, success, message in cases:
            with self.subTest(case=name), tempfile.TemporaryDirectory() as root:
                os.makedirs(os.path.join(root, "tools"))
                os.makedirs(os.path.join(root, "career"))
                os.makedirs(os.path.join(root, "assets"))
                script = os.path.join(root, "tools", "regen_resume_pdf.sh")
                shutil.copyfile(_path("tools/regen_resume_pdf.sh"), script)
                for page in ("index.html", "career/index.html"):
                    with open(os.path.join(root, page), "w") as handle:
                        handle.write('<html><link href="/styles.css">Resume '
                                     '<a href="/work/">Selected work</a>'
                                     '<a href="../media/">Media</a>'
                                     '<a href="mailto:nick@giulioni.com">Email</a>'
                                     '<a href="https://www.linkedin.com/in/nickgiulioni">'
                                     'LinkedIn</a></html>')
                Path(root, "styles.css").write_text("/* local styles */")
                source_html = Path(root, "career/index.html").read_bytes()
                default_output = os.path.join(root, "assets", "nick-giulioni-resume.pdf")
                output_dir = os.path.join(root, "output with spaces")
                os.mkdir(output_dir)
                output = os.path.join(output_dir, "resume.pdf")
                original = b"existing PDF must survive a failed render"
                for path in (default_output, output):
                    with open(path, "wb") as handle:
                        handle.write(original)
                fixture = os.path.join(root, "fixture.pdf")
                if payload is not None:
                    with open(fixture, "wb") as handle:
                        handle.write(payload)
                chrome = os.path.join(root, "fake-chrome")
                with open(chrome, "w") as handle:
                    handle.write("""#!/usr/bin/env python3
import os
import shutil
import sys
from urllib.parse import urljoin
from urllib.request import urlopen
url = sys.argv[-1]
with urlopen(url) as response:
    html = response.read().decode()
assert '<a href="https://giulioni.com/work/">' in html
assert '<a href="https://giulioni.com/media/">' in html
assert '<a href="mailto:nick@giulioni.com">' in html
assert '<a href="https://www.linkedin.com/in/nickgiulioni">' in html
assert '<link href="/styles.css">' in html
with urlopen(urljoin(url, '/styles.css')) as response:
    assert response.read() == b'/* local styles */'
output = next(arg.split('=', 1)[1] for arg in sys.argv[1:]
              if arg.startswith('--print-to-pdf='))
if os.path.exists(os.environ['FAKE_PDF']):
    shutil.copyfile(os.environ['FAKE_PDF'], output)
    if os.environ['FAKE_MODE'] == 'stale':
        os.utime(output, (1, 1))
sys.exit(int(os.environ['FAKE_STATUS']))
""")
                os.chmod(chrome, 0o755)
                env = dict(os.environ, CHROME_BIN=chrome, OUT=output,
                           FAKE_PDF=fixture, FAKE_MODE=name,
                           FAKE_STATUS=str(chrome_status), RESUME_PDF_PORT="0")
                result = subprocess.run(
                    ["bash", script], env=env, capture_output=True, text=True, timeout=30
                )
                logs = result.stdout + result.stderr
                self.assertEqual(result.returncode == 0, success, logs)
                self.assertIn(message, logs)
                with open(output, "rb") as handle:
                    self.assertEqual(handle.read(), payload if success else original)
                with open(default_output, "rb") as handle:
                    self.assertEqual(handle.read(), original)
                self.assertEqual(os.listdir(output_dir), ["resume.pdf"])
                self.assertEqual(Path(root, "career/index.html").read_bytes(), source_html)
                if not success:
                    self.assertNotIn("Wrote", result.stdout)


class ResponsiveAndA11yTests(unittest.TestCase):
    """Viewport-fit, safe-area, coarse-pointer 44px, reduced-motion are
    all present across pages and CSS."""

    def test_all_pages_use_cover_viewport(self):
        viewport = (
            'content="width=device-width, initial-scale=1, viewport-fit=cover"'
        )
        for page in PAGES:
            with self.subTest(page=page):
                self.assertIn(viewport, _read_page(page))

    def test_css_has_safe_area_touch_and_motion_guards(self):
        css = _read_css()
        for token in (
            "env(safe-area-inset-left, 0px)",
            "env(safe-area-inset-right, 0px)",
            "env(safe-area-inset-bottom, 0px)",
            "@media (pointer: coarse)",
            "@media (prefers-reduced-motion: reduce)",
        ):
            with self.subTest(token=token):
                self.assertIn(token, css)

    def test_coarse_pointer_rule_includes_interactive_elements(self):
        css = _read_css()
        coarse = re.search(r"@media \(pointer: coarse\)\s*\{(.*?)\n\}", css, re.S)
        self.assertIsNotNone(coarse)
        body = coarse.group(1)
        for selector in (
            ".site-nav a",
            ".btn",
            ".destination-link",
            ".media-entry .episode-title a",
            ".contact-line a",
        ):
            with self.subTest(selector=selector):
                self.assertIn(
                    selector,
                    body,
                    "coarse-pointer rule must cover %s" % selector,
                )
        self.assertRegex(
            body,
            r"min-height:\s*44px",
            "coarse-pointer rule must set min-height: 44px",
        )

    def test_print_css_keeps_min_7_8pt_body_size(self):
        css = _read_css()
        print_block = re.search(r"@media print\s*\{(.*?)\n\}", css, re.S)
        self.assertIsNotNone(print_block)
        body_size = re.search(
            r"body\s*\{[^}]*font-size:\s*([0-9.]+)pt", print_block.group(1)
        )
        self.assertIsNotNone(body_size)
        size = float(body_size.group(1))
        self.assertGreaterEqual(
            size, 7.8, "print body font-size must be at least 7.8pt"
        )


class RootRelativeTests(unittest.TestCase):
    """Directory routing requires root-relative references from any depth."""

    def test_all_local_references_are_root_relative(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            local = _local_refs(html)
            with self.subTest(page=name):
                self.assertTrue(
                    local, "%s has no local references to assert against" % name
                )
                bad = sorted(r for r in local if not r.startswith("/"))
                self.assertEqual(
                    bad,
                    [],
                    "%s has non-root-relative references: %r" % (name, bad),
                )


class SocialLinksTests(unittest.TestCase):
    """Every page carries the approved contact links, exact URLs."""

    def test_each_page_lists_approved_contact_links(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            hrefs = {h for _q, h in _anchor_pairs(html)}
            with self.subTest(page=name):
                for href in SOCIAL_HREFS:
                    self.assertIn(
                        href,
                        hrefs,
                        "%s missing approved contact link %r" % (name, href),
                    )


class MarkupHygieneTests(unittest.TestCase):
    """Markup stays CSP-safe: no scripts, inline styles, handlers."""

    def test_no_script_tags(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            with self.subTest(page=name):
                self.assertNotRegex(
                    _strip_html_comments(html),
                    r"<script\b",
                    "%s must not contain <script> tags" % name,
                )

    def test_no_inline_style_blocks_or_attributes(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            clean = _strip_html_comments(html)
            with self.subTest(page=name):
                self.assertNotRegex(
                    clean, r"<style\b", "%s must not contain inline <style> blocks" % name
                )
                self.assertNotRegex(
                    clean,
                    r'(?<![A-Za-z-])style\s*=\s*["\']',
                    "%s must not use style= attributes" % name,
                )

    def test_no_inline_event_handlers_or_javascript_urls(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            clean = _strip_html_comments(html)
            with self.subTest(page=name):
                self.assertNotRegex(
                    clean,
                    r'(?<![A-Za-z-])on[a-z]+\s*=\s*["\']',
                    "%s must not use inline event handlers" % name,
                )
                self.assertNotRegex(
                    clean,
                    r"(?i)javascript:",
                    "%s must not use javascript: URLs" % name,
                )

    def test_no_open_design_data_attributes(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            with self.subTest(page=name):
                self.assertNotIn(
                    "data-od-id",
                    _strip_html_comments(html),
                    "%s must not carry Open Design data-od-id attributes" % name,
                )


def _read_css():
    path = _path("styles.css")
    if not os.path.isfile(path):
        raise AssertionError("styles.css is missing")
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class CssTests(unittest.TestCase):
    """styles.css is balanced and properly structured."""

    @classmethod
    def _css_noise_stripped(cls):
        css = _read_css()
        css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
        css = re.sub(r'"[^"]*"', '""', css)
        css = re.sub(r"'[^']*'", "''", css)
        return css

    def test_styles_css_exists_and_braces_balance(self):
        css = self._css_noise_stripped()
        self.assertEqual(
            css.count("{"),
            css.count("}"),
            "styles.css has unbalanced braces",
        )

    def test_css_uses_new_palette(self):
        css = _read_css()
        self.assertIn("#f6f3ec", css, "CSS must use paper/cream color #f6f3ec")
        self.assertIn("#16211c", css, "CSS must use ink/forest color #16211c")
        self.assertIn("#b8501f", css, "CSS must use rust accent #b8501f")

    def test_css_does_not_use_old_palette(self):
        css = _read_css()
        self.assertNotIn("#1f2ec4", css, "CSS must not use old ultramarine #1f2ec4")

    @staticmethod
    def _rule(css, selector):
        match = re.search(r"(?m)^" + re.escape(selector) + r"\s*\{([^}]*)\}", css)
        if match is None:
            raise AssertionError("missing top-level rule for %s" % selector)
        return match.group(1)

    def test_dark_band_bleeds_to_viewport_edges(self):
        """#60: the width cap lives on .page-main's children, not .page-main,
        so the band's negative margins always reach the viewport edges."""
        css = _read_css()
        self.assertNotRegex(self._rule(css, ".page-main"), r"(?<![-\w])width:")
        self.assertRegex(self._rule(css, ".page-main > *"), r"max-width:\s*1160px")
        band = self._rule(css, ".product-band")
        self.assertRegex(band, r"max-width:\s*none")
        self.assertIn("calc(-2.5rem - var(--safe-left))", band)
        self.assertNotIn("100vw", css, "vw bleeds overflow with classic scrollbars")

    def test_media_grid_last_odd_entry_spans_both_columns(self):
        """#61: works for any entry count, so no empty cell after the last."""
        self.assertRegex(
            self._rule(_read_css(), ".media-entry:last-child:nth-child(odd)"),
            r"grid-column:\s*1\s*/\s*-1",
        )


class OpenDesignArtifactTests(unittest.TestCase):
    """Open Design-only files must not ship to production."""

    def test_no_open_design_sidecar_or_source_files(self):
        forbidden_names = {"home.html", "DESIGN.md", "brand-spec.md"}
        found = []
        for dirpath, _dirs, files in os.walk(REPO_ROOT):
            if os.path.basename(dirpath) == ".git":
                continue
            for fname in files:
                rel = os.path.relpath(os.path.join(dirpath, fname), REPO_ROOT)
                if fname in forbidden_names or fname.endswith(".artifact.json"):
                    found.append(rel)
        self.assertEqual(
            [],
            sorted(found),
            "Open Design-only files must not ship to production: %r" % sorted(found),
        )


class NotFoundPageTests(unittest.TestCase):
    """Root 404.html: Vercel serves it for unknown paths with status 404."""

    def setUp(self):
        path = _path("404.html")
        self.assertTrue(os.path.isfile(path), "404.html is missing at repo root")
        with open(path, encoding="utf-8") as fh:
            self.html = _strip_html_comments(fh.read())

    def test_links_back_to_main_pages(self):
        hrefs = {h for _q, h in _anchor_pairs(self.html)}
        for href in ("/", "/career/", "/work/"):
            with self.subTest(href=href):
                self.assertIn(href, hrefs, "404.html missing link to %r" % href)

    def test_is_noindex(self):
        self.assertRegex(
            self.html,
            r'<meta\s+name="robots"\s+content="noindex"\s*>',
            "404.html must carry <meta name=\"robots\" content=\"noindex\">",
        )

    def test_uses_shared_stylesheet_and_csp_safe_markup(self):
        self.assertIn('<link rel="stylesheet" href="/styles.css">', self.html)
        self.assertNotRegex(self.html, r"<script\b|<style\b")
        self.assertNotRegex(self.html, r'(?<![A-Za-z-])(style|on[a-z]+)\s*=\s*["\']')
        bad = sorted(r for r in _local_refs(self.html) if not r.startswith("/"))
        self.assertEqual(bad, [], "404.html has non-root-relative references")

    def test_unknown_paths_are_not_rewritten_to_200(self):
        with open(_path("vercel.json"), encoding="utf-8") as fh:
            vercel = fh.read()
        self.assertNotIn('"rewrites"', vercel, "rewrites would serve 404.html as 200")


class DeploymentReferences(HTMLParser):
    """URLs used by markup, including responsive images and share cards."""

    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.urls.extend(attrs[key] for key in ("href", "src") if attrs.get(key))
        for candidate in attrs.get("srcset", "").split(","):
            if candidate.strip():
                self.urls.append(candidate.split()[0])
        if tag == "meta" and attrs.get("property", attrs.get("name")) in (
            "og:image", "twitter:image",
        ):
            self.urls.append(attrs["content"])


class VercelIgnoreTests(unittest.TestCase):
    """Internal files stay out; pages and their dependencies remain deployable."""

    def ignored_paths(self, paths):
        # Let Git parse its own syntax, isolated from repo/global ignore rules.
        with tempfile.TemporaryDirectory() as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            Path(directory, ".gitignore").write_text(
                Path(_path(".vercelignore")).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            result = subprocess.run(
                ["git", "-c", "core.excludesFile=/dev/null", "check-ignore",
                 "--no-index", "-z", "--stdin"],
                cwd=directory, input="\0".join(sorted(paths)) + "\0",
                text=True, capture_output=True,
            )
            self.assertIn(result.returncode, (0, 1), result.stderr)
            return set(result.stdout.split("\0")) - {""}

    def test_internal_paths_are_excluded(self):
        paths = {
            "AGENTS.md", "DEPLOYMENT.md", "README.md", "NOTES.md",
            "PLAN", "PLAN.txt", "PLAN-release.json", ".github/workflows/check.yml",
            ".gitignore", ".vercelignore", "assets/favicon-preview.png",
            "docs/future/note.txt", "tests/future/test.py", "tools/future/script.sh",
        }
        for directory in ("docs", "tests", "tools"):
            paths.update(
                str(path.relative_to(REPO_ROOT))
                for path in Path(_path(directory)).rglob("*") if path.is_file()
            )
        self.assertEqual(paths, self.ignored_paths(paths))

    def test_font_assets_and_licenses_are_kept(self):
        paths = {
            "assets/fonts/instrument-sans-latin-wght.woff2",
            "assets/fonts/instrumentsans-OFL.txt",
            "assets/fonts/newsreader-OFL.txt",
            "assets/fonts/newsreader-latin-italic.woff2",
            "assets/fonts/newsreader-latin-normal.woff2",
        }
        self.assertEqual(set(), self.ignored_paths(paths))

    def test_nested_markdown_is_excluded(self):
        paths = {
            "assets/fonts/README.md", "future/notes.md",
            "future/deep/nested/notes.md",
        }
        self.assertEqual(paths, self.ignored_paths(paths))

    def test_site_files_and_references_are_kept(self):
        root = Path(REPO_ROOT)
        pages = sorted(root.rglob("*.html"))
        paths = {"styles.css", "robots.txt", "sitemap.xml", "vercel.json",
                 "favicon.ico", "favicon.svg", "apple-touch-icon.png"}
        paths.update(str(page.relative_to(root)) for page in pages)
        paths.update(
            str(path.relative_to(root)) for path in (root / "assets").rglob("*")
            if path.is_file() and path.name != "favicon-preview.png"
            and path.suffix != ".md"
        )
        urls = []
        for page in pages:
            parser = DeploymentReferences()
            parser.feed(page.read_text(encoding="utf-8"))
            base = "https://giulioni.com/" + str(page.relative_to(root))
            urls.extend((base, url) for url in parser.urls)
        urls.extend(
            ("https://giulioni.com/", node.text)
            for node in ET.parse(_path("sitemap.xml")).iter()
            if node.tag.endswith("}loc")
        )
        urls.extend(
            ("https://giulioni.com/", url)
            for url in re.findall(r"(?im)^Sitemap:\s*(\S+)",
                                  Path(_path("robots.txt")).read_text())
        )
        urls.extend(
            ("https://giulioni.com/styles.css", url.strip("\"' "))
            for url in re.findall(r"url\(([^)]+)\)", _read_css())
        )
        for base, reference in urls:
            url = urlsplit(urljoin(base, reference))
            if url.scheme not in ("http", "https") or url.hostname not in (
                "giulioni.com", "www.giulioni.com",
            ):
                continue
            path = unquote(url.path).lstrip("/")
            if not path or url.path.endswith("/") or (root / path).is_dir():
                path += "index.html"
            self.assertTrue((root / path).is_file(), "missing site reference: " + path)
            paths.add(path)
        self.assertEqual(set(), self.ignored_paths(paths))


class CspTests(unittest.TestCase):
    """The deployed CSP never grants inline or eval execution."""

    def test_csp_forbids_unsafe_inline_and_eval(self):
        path = _path("vercel.json")
        self.assertTrue(os.path.isfile(path), "vercel.json is missing")
        with open(path, encoding="utf-8") as fh:
            vercel = fh.read()
        self.assertNotIn("'unsafe-inline'", vercel, "CSP must not allow 'unsafe-inline'")
        self.assertNotIn("'unsafe-eval'", vercel, "CSP must not allow 'unsafe-eval'")

    def test_styles_and_fonts_are_same_origin_only(self):
        with open(_path("vercel.json"), encoding="utf-8") as fh:
            vercel = json.load(fh)
        policies = [
            header["value"]
            for rule in vercel["headers"]
            for header in rule["headers"]
            if header["key"].lower() == "content-security-policy"
        ]
        self.assertTrue(policies, "a CSP must be configured")
        for policy in policies:
            directives = dict(
                (parts[0], parts[1:])
                for directive in policy.split(";")
                if (parts := directive.split())
            )
            self.assertEqual(["'self'"], directives.get("style-src"))
            self.assertEqual(["'self'"], directives.get("font-src"))


class FontTests(unittest.TestCase):
    """The existing typefaces load locally without a third-party CSS request."""

    FACES = {
        "instrument-sans-latin-wght.woff2": ("Instrument Sans", "normal", "400 600"),
        "newsreader-latin-normal.woff2": ("Newsreader", "normal", "400"),
        "newsreader-latin-italic.woff2": ("Newsreader", "italic", "400"),
    }

    def test_no_google_font_references_in_any_page_css_or_csp(self):
        paths = ["styles.css", "vercel.json"]
        for directory, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            paths.extend(
                os.path.relpath(os.path.join(directory, name), REPO_ROOT)
                for name in files if name.endswith(".html")
            )
        for path in paths:
            with self.subTest(path=path), open(_path(path), encoding="utf-8") as fh:
                self.assertNotRegex(fh.read(), r"(?i)(?:googleapis|gstatic)\.com")

    def test_font_faces_reference_real_woff2_files_with_original_styles(self):
        faces = re.findall(r"@font-face\s*\{([^}]+)\}", _read_css())
        self.assertEqual(len(self.FACES), len(faces))
        referenced = set()
        for face in faces:
            match = re.search(r'url\("(/assets/fonts/([^"/]+))"\)', face)
            self.assertIsNotNone(match, "font sources must be root-relative")
            url, filename = match.groups()
            self.assertIn(filename, self.FACES)
            referenced.add(filename)
            family, style, weight = self.FACES[filename]
            self.assertIn('font-family: "%s";' % family, face)
            self.assertIn("font-style: %s;" % style, face)
            self.assertIn("font-weight: %s;" % weight, face)
            self.assertIn("font-display: swap;", face)
            with open(_path(url.lstrip("/")), "rb") as fh:
                self.assertEqual(b"wOF2", fh.read(4), "must be a WOFF2 file")
        self.assertEqual(set(self.FACES), referenced)

    def test_each_page_preloads_only_the_two_above_fold_faces(self):
        expected = {
            "/assets/fonts/instrument-sans-latin-wght.woff2",
            "/assets/fonts/newsreader-latin-normal.woff2",
        }
        for name, path in {**PAGES, "not_found": "404.html"}.items():
            with self.subTest(page=name):
                with open(_path(path), encoding="utf-8") as fh:
                    head = fh.read().split("</head>", 1)[0]
                links = re.findall(r'<link\b[^>]*\brel="preload"[^>]*>', head)
                self.assertEqual(2, len(links))
                urls = set()
                for link in links:
                    attrs = dict(re.findall(r'(\w+)="([^"]*)"', link))
                    self.assertEqual("font", attrs.get("as"))
                    self.assertEqual("font/woff2", attrs.get("type"))
                    self.assertRegex(link, r"\bcrossorigin(?:\s|=|>)")
                    urls.add(attrs.get("href"))
                self.assertEqual(expected, urls)

    def test_both_font_licenses_ship_with_the_fonts(self):
        for family in ("instrumentsans", "newsreader"):
            with open(_path("assets/fonts/%s-OFL.txt" % family), encoding="utf-8") as fh:
                self.assertIn("SIL OPEN FONT LICENSE Version 1.1", fh.read())


if __name__ == "__main__":
    unittest.main()
