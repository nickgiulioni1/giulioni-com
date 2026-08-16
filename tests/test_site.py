"""Static-site contract for giulioni.com (cream/forest/rust editorial system).

Deterministic, standard-library-only checks describing the approved final
production state: a four-page static site (Home, Resume, Selected work,
Earlier media) with root-relative internal links and assets, the approved
contact links (Email, LinkedIn), the recruiter-first primary nav, the
approved Resume section structure, the Selected work Ballpark case + A
Little True + three receipts, the seven Earlier media URLs, the resume
PDF, the responsive / safe-area / coarse-pointer / reduced-motion CSS,
CSP-safe markup, balanced CSS braces, and none of the prohibited Open
Design-only artifacts (data-od-id attributes, sidecars, home.html,
DESIGN.md, brand-spec.md).

Run:

    python3 -m unittest discover -s tests -v
"""

import hashlib
import os
import re
import subprocess
import unittest

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


def _normalized_text(text):
    return re.sub(r"\s+", "", text.lower())


class StructureTests(unittest.TestCase):
    """The site is four directory-rooted pages."""

    def test_required_pages_exist(self):
        for name, rel in PAGES.items():
            with self.subTest(page=name):
                self.assertTrue(
                    os.path.isfile(_path(rel)),
                    "required page %r is missing" % rel,
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
    """Home page carries hero, track record, product band, and closing CTA."""

    PRIMARY_HREFS = (
        "/career/",
        "/work/",
        "mailto:nick@giulioni.com",
        "/assets/nick-giulioni-resume.pdf",
    )

    def test_home_has_primary_actions_and_pdf_download(self):
        html = _strip_html_comments(_read_page("home"))
        for href in self.PRIMARY_HREFS:
            with self.subTest(href=href):
                self.assertIn(
                    'href="%s"' % href,
                    html,
                    "home must link %r as a primary action or PDF download" % href,
                )

    def test_home_has_hero_lede(self):
        html = _strip_html_comments(_read_page("home"))
        self.assertIn("operator who builds his own tools", html.lower())

    def test_home_has_approved_hero_thesis(self):
        html = _strip_html_comments(_read_page("home"))
        for phrase in (
            "expensive problem",
            "$150M annual budget",
            "$3M in its first year",
            "3,000+ doors",
            "Estimating was the thing that kept breaking",
            "Ballpark",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(
                    phrase,
                    html,
                    "hero thesis must contain approved phrase %r" % phrase,
                )

    def test_home_carries_target_role_language(self):
        html = _strip_html_comments(_read_page("home"))
        for phrase in (
            "AI product",
            "solutions",
            "enablement",
            "forward-deployed",
            "construction",
            "field service",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(
                    phrase.lower(),
                    html.lower(),
                    "home must carry target-role phrase %r" % phrase,
                )

    def test_home_has_track_record_section(self):
        html = _strip_html_comments(_read_page("home"))
        self.assertIn("track-record", html)
        for label in ("Ballpark", "Off Leash Construction", "Corsair", "Razer"):
            with self.subTest(label=label):
                self.assertIn(label, html)

    def test_home_track_record_has_three_cells_per_row(self):
        html = _strip_html_comments(_read_page("home"))
        self.assertIn("track-problem", html, "track record must have problem cells")
        self.assertIn("track-did", html, "track record must have what-I-did cells")
        self.assertIn("track-outcome", html, "track record must have outcome cells")

    def test_home_has_product_band_with_ballpark_link(self):
        html = _strip_html_comments(_read_page("home"))
        self.assertIn("product-band", html)
        self.assertIn('href="https://ballpark.build"', html)

    def test_home_has_estimate_image(self):
        html = _strip_html_comments(_read_page("home"))
        self.assertIn('src="/assets/ballpark-estimate.png"', html)

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


class MixedSignalTests(unittest.TestCase):
    """Home and Selected work must not carry Best Notes, venues, real
    estate, or 48-hour STR claims."""

    MIXED_TOKENS = (
        "Best Notes",
        "The Wilds",
        "Laural Mill",
        "Off Leash Investments",
        "48 hours",
        "short-term rental",
    )

    def test_home_carries_no_mixed_signal_tokens(self):
        html = _strip_html_comments(_read_page("home"))
        normalized = _normalized_text(html)
        for token in self.MIXED_TOKENS:
            with self.subTest(token=token):
                self.assertNotIn(
                    _normalized_text(token),
                    normalized,
                    "home must not carry mixed-signal token %r" % token,
                )

    def test_work_carries_no_mixed_signal_tokens(self):
        html = _strip_html_comments(_read_page("work"))
        normalized = _normalized_text(html)
        for token in self.MIXED_TOKENS:
            with self.subTest(token=token):
                self.assertNotIn(
                    _normalized_text(token),
                    normalized,
                    "work must not carry mixed-signal token %r" % token,
                )

    def test_resume_keeps_operating_history_only_in_subordinate_section(self):
        html = _strip_html_comments(_read_page("resume"))
        self.assertIn("Operating history", html)
        self.assertIn("resume-section-subordinate", html)


class ResumeTests(unittest.TestCase):
    """/career/ renders the recruiter-first Resume."""

    REQUIRED_SECTIONS = (
        "Summary",
        "Ballpark bridge",
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

    def test_resume_carries_target_role_language(self):
        html = _strip_html_comments(_read_page("resume"))
        for phrase in (
            "AI product",
            "solutions",
            "enablement",
            "forward-deployed",
            "construction tech",
            "field-service software",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(
                    phrase,
                    html,
                    "resume must carry target-role phrase %r" % phrase,
                )

    def test_resume_preserves_truthful_titles_dates_metrics(self):
        html = _read_page("resume")
        for token in (
            "$150 million",
            "team of six",
            "$3 million",
            "3,000 doors",
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

    def test_ballpark_case_has_estimate_image(self):
        html = _read_page("work")
        self.assertIn('src="/assets/ballpark-estimate.png"', html)

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
    """/media/ retains the seven incumbent URLs and stays out of the
    primary nav."""

    def test_media_title_and_metadata(self):
        html = _read_page("media")
        self.assertIn("<title>Earlier media | Nick Giulioni</title>", html)
        self.assertIn(
            '<meta property="og:title" content="Earlier media | Nick Giulioni">', html
        )

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


class ResumePdfTests(unittest.TestCase):
    """The downloadable resume PDF is generated, two pages, and contains
    the required tokens."""

    REQUIRED_PDF_TOKENS = (
        "resume",
        "nick@giulioni.com",
        "linkedin.com/in/nickgiulioni",
        "ballpark",
    )

    @staticmethod
    def _pdf_path():
        return _path("assets/nick-giulioni-resume.pdf")

    def test_pdf_exists(self):
        self.assertTrue(
            os.path.isfile(self._pdf_path()),
            "resume PDF must be committed at assets/nick-giulioni-resume.pdf",
        )

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
