"""Static-site contract for giulioni.com.

Deterministic, standard-library-only checks describing the approved final
production state: a four-page static site (Home, Career, What I'm Working On,
Media) with root-relative internal links and assets, the approved contact
links (Email, LinkedIn, X, Instagram), the approved Career chapter order, the
approved Media appearance entries, CSP-safe markup, balanced CSS braces, and
none of the prohibited design patterns (scripts, cards, pills, gradients,
shadows, radii) or Open Design-only artifacts (data-od-id attributes, sidecars,
home.html, DESIGN.md, brand-spec.md).

Run:

    python3 -m unittest discover -s tests -v
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PAGES = {
    "home": "index.html",
    "career": "career/index.html",
    "work": "work/index.html",
    "media": "media/index.html",
}

# Approved contact links (exact strings, no trailing variants).
SOCIAL_HREFS = (
    "mailto:nick@giulioni.com",
    "https://www.linkedin.com/in/nickgiulioni",
    "https://x.com/NickGiulioni",
    "https://www.instagram.com/nickgiulioni/",
)

# Approved Career chapter order: chapter-name headings in document order.
CAREER_CHAPTERS = ["AI product work", "Indiana operator", "E-commerce leadership"]

# Approved Media appearances: (episode title, URL), exact strings.
MEDIA_ENTRIES = (
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


class StructureTests(unittest.TestCase):
    """The site is three directory-rooted pages, not one sheet."""

    def test_required_pages_exist(self):
        for name, rel in PAGES.items():
            with self.subTest(page=name):
                self.assertTrue(
                    os.path.isfile(_path(rel)),
                    "required page %r is missing" % rel,
                )


class NavigationTests(unittest.TestCase):
    """Approved primary nav: Home, Career, What I'm Working On, Media."""

    def test_each_page_has_approved_navigation(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            hrefs = {h for _q, h in _anchor_pairs(_nav_block(html))}
            with self.subTest(page=name):
                self.assertTrue(
                    "/" in hrefs or "/index.html" in hrefs,
                    "%s nav missing Home link (/ or /index.html)" % name,
                )
                self.assertIn("/career/", hrefs, "%s nav missing /career/" % name)
                self.assertIn("/work/", hrefs, "%s nav missing /work/" % name)
                self.assertIn("/media/", hrefs, "%s nav missing /media/" % name)

    def test_media_is_an_interactive_link_with_no_planned_markup(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            clean = _strip_html_comments(html)
            with self.subTest(page=name):
                self.assertIn(
                    '<a href="/media/"',
                    clean,
                    "%s nav must link Media via <a href=\"/media/\"" % name,
                )
                for stale in ("nav-planned", "planned-note", "aria-disabled"):
                    self.assertNotIn(
                        stale,
                        clean,
                        "%s must not carry stale planned-Media markup %r"
                        % (name, stale),
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
    """Every page carries the four approved contact links, exact URLs."""

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


class CareerContentTests(unittest.TestCase):
    """Career chapter order and facts match the approved design."""

    def test_career_chapter_order(self):
        html = _strip_html_comments(_read_page("career"))
        names = re.findall(
            r'<h2\b[^>]*\bclass\s*=\s*(["\'])[^"\']*chapter-name[^"\']*\1[^>]*>(.*?)</h2>',
            html,
            flags=re.S | re.I,
        )
        names = [re.sub(r"<.*?>", "", n).strip() for _q, n in names]
        self.assertEqual(
            names,
            CAREER_CHAPTERS,
            "Career chapter-name headings must be, in order: %r (got %r)"
            % (CAREER_CHAPTERS, names),
        )

    def test_career_records_laural_mill_acquired_mar_2023(self):
        html = _read_page("career")
        self.assertIn(
            "Acquired Mar 2023",
            html,
            "Career page must record Laural Mill as 'Acquired Mar 2023'",
        )

    def test_career_includes_laural_mill_entry(self):
        html = _strip_html_comments(_read_page("career"))
        self.assertIn(
            "Laural Mill", html, "Career page must include the Laural Mill entry"
        )


class MediaContentTests(unittest.TestCase):
    """Media page carries exactly the seven approved appearances."""

    @staticmethod
    def _entries_block():
        html = _strip_html_comments(_read_page("media"))
        opens = re.findall(r'<section\s+class="media-entries">', html)
        if len(opens) != 1:
            raise AssertionError(
                "media page must contain exactly one "
                '<section class="media-entries"> (found %d)' % len(opens)
            )
        start = html.index('<section class="media-entries">')
        end = html.index("</section>", start)
        block = html[start : end + len("</section>")]
        if "<section" in block[1:]:
            raise AssertionError(
                "media-entries section must not contain nested <section>"
            )
        return block

    def test_exactly_one_media_entries_section_with_no_nesting(self):
        self._entries_block()

    def test_each_approved_url_appears_exactly_once_as_href(self):
        block = self._entries_block()
        for _title, url in MEDIA_ENTRIES:
            with self.subTest(url=url):
                self.assertEqual(
                    block.count('href="%s"' % url),
                    1,
                    "media-entries must link %r exactly once" % url,
                )

    def test_every_external_href_in_block_is_an_approved_url(self):
        block = self._entries_block()
        found = set(re.findall(r'href="(https://[^"]*)"', block))
        self.assertEqual(
            found,
            {url for _title, url in MEDIA_ENTRIES},
            "media-entries external hrefs must equal the approved seven URLs",
        )

    def test_each_approved_episode_title_appears(self):
        block = self._entries_block()
        for title, _url in MEDIA_ENTRIES:
            with self.subTest(title=title):
                self.assertIn(
                    title, block, "media-entries missing episode title %r" % title
                )

    def test_media_head_block_and_current_nav_state(self):
        html = _read_page("media")
        self.assertIn("<title>Media | Nick Giulioni</title>", html)
        self.assertIn(
            '<meta property="og:title" content="Media | Nick Giulioni">', html
        )
        self.assertIn(
            '<meta property="og:description" content="Podcast and interview '
            "appearances by Nick Giulioni, from real-estate investing to "
            'operating businesses in Indiana.">',
            html,
        )
        self.assertIn('<a href="/media/" aria-current="page">Media</a>', html)

    def test_no_embed_markup_on_any_page(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            clean = _strip_html_comments(html).lower()
            with self.subTest(page=name):
                for tag in ("<iframe", "<embed", "<object", "<script"):
                    self.assertNotIn(
                        tag, clean, "%s must not contain %s markup" % (name, tag)
                    )


class MarkupHygieneTests(unittest.TestCase):
    """Markup stays CSP-safe: no scripts, inline styles, handlers, or
    Open Design-only data attributes."""

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


class CssTests(unittest.TestCase):
    """styles.css is balanced and free of prohibited design patterns."""

    @staticmethod
    def _read_css():
        path = _path("styles.css")
        if not os.path.isfile(path):
            raise AssertionError("styles.css is missing")
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    @classmethod
    def _css_noise_stripped(cls):
        css = cls._read_css()
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

    def test_no_prohibited_design_patterns(self):
        css = self._css_noise_stripped().lower()
        for needle in ("gradient", "shadow", "border-radius", "text-shadow"):
            self.assertNotIn(
                needle,
                css,
                "styles.css uses prohibited design pattern %r" % needle,
            )


class ProhibitedClassTests(unittest.TestCase):
    """No card or pill class names anywhere in markup."""

    def test_no_card_or_pill_class_names(self):
        for name in PAGES:
            try:
                html = _read_page(name)
            except AssertionError as exc:
                self.fail(str(exc))
            tokens = _class_tokens(html)
            with self.subTest(page=name):
                for forbidden in ("card", "pill"):
                    self.assertNotIn(
                        forbidden,
                        tokens,
                        "%s uses forbidden class %r" % (name, forbidden),
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


class CspTests(unittest.TestCase):
    """The deployed CSP never grants inline or eval execution."""

    def test_csp_forbids_unsafe_inline_and_eval(self):
        path = _path("vercel.json")
        self.assertTrue(os.path.isfile(path), "vercel.json is missing")
        with open(path, encoding="utf-8") as fh:
            vercel = fh.read()
        self.assertNotIn("'unsafe-inline'", vercel, "CSP must not allow 'unsafe-inline'")
        self.assertNotIn("'unsafe-eval'", vercel, "CSP must not allow 'unsafe-eval'")


if __name__ == "__main__":
    unittest.main()
