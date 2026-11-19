"""Static site contracts, shared copy, accessibility structure and asset hygiene."""
import json
import re
import struct
import unittest
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
AREA_SLUGS = ['carmel', 'westfield', 'fishers', 'north-indianapolis', 'noblesville', 'zionsville']
PATHS = ['/', '/sell/', '/buy/', '/areas/'] + ['/areas/'+s+'/' for s in AREA_SLUGS] + ['/about/', '/contact/', '/podcast/', '/privacy/']
EXTRA = ['/contact/thanks/', '/contact/error/', '/404.html']

def file_for(url):
    return ROOT / ('404.html' if url == '/404.html' else url.lstrip('/') + 'index.html')

class Markup(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
    def attrs(self, tag): return [a for t,a in self.tags if t == tag]

class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pages = {u: file_for(u).read_text() for u in PATHS + EXTRA}
        cls.site = json.loads((ROOT/'site.json').read_text())
        cls.config = json.loads((ROOT/'vercel.json').read_text())

    def test_pages_and_head(self):
        titles, descriptions = [], []
        for url, text in self.pages.items():
            with self.subTest(url=url):
                m = Markup(text)
                self.assertEqual(len(m.attrs('h1')), 1)
                title = re.search(r'<title>(.*?)</title>',text).group(1)
                titles.append(title)
                metas = {a.get('name',a.get('property')): a.get('content') for a in m.attrs('meta')}
                descriptions.append(metas['description'])
                for tag in ['og:title','og:description','og:url','og:image','twitter:card','twitter:title','twitter:description','twitter:image']: self.assertTrue(metas.get(tag))
                self.assertTrue(metas['og:image'].startswith('https://giulioni.com/assets/'))
                canonicals=[a for a in m.attrs('link') if a.get('rel')=='canonical']
                self.assertEqual(canonicals,[] if url in EXTRA else [{'rel':'canonical','href':'https://giulioni.com'+url}])
                self.assertIn('viewport-fit=cover',metas['viewport'])
                self.assertEqual(len([a for a in m.attrs('link') if a.get('as')=='font']),2)
                if url in EXTRA: self.assertEqual(metas['robots'],'noindex')
        self.assertEqual(len(titles),len(set(titles)))
        self.assertEqual(len(descriptions),len(set(descriptions)))

    def test_shared_footer_contact_and_copy(self):
        footers = []
        for url,text in self.pages.items():
            with self.subTest(url=url):
                m=Markup(text)
                footers.append(re.search(r'<footer class="site-footer">.*?</footer>',text,re.S).group())
                self.assertLess(text.index('</main>'),text.index('<footer'))
                self.assertIn('class="disclosure"',text)
                self.assertIn('760 E. 52nd St',text)
                self.assertIn('317-255-7767',text)
                self.assertIn('T&amp;H Realty Services',text)
                self.assertIn({'src':'/assets/equal-housing.svg','width':'28','height':'28','alt':'Equal Housing Opportunity'},m.attrs('img'))
                self.assertEqual({a['href'] for a in m.attrs('a') if a.get('href','').startswith('tel:')},{self.site['phone_tel']})
                self.assertIn('mailto:'+self.site['email'],text)
                stats = re.findall(r'class="stat-properties">(.*?)</span>',text)
                for value in stats: self.assertEqual(value,self.site['properties_touched']+' properties touched')
                for number in re.findall(r'\b\d+\+ properties touched',text): self.assertEqual(number,self.site['properties_touched']+' properties touched')
                plain = re.sub('<[^>]*>',' ',text)
                plain = plain.replace(self.site['podcast_line'].replace('&','&amp;'),'')
                self.assertNotRegex(plain,r'(?i)\bhosts?\b')
                self.assertNotIn('®',text)
        self.assertEqual(len(set(footers)),1)

    def test_forms(self):
        total=0
        for url,text in self.pages.items():
            for form in re.findall(r'<form\b.*?</form>',text,re.S):
                total+=1
                m=Markup(form)
                self.assertEqual(m.attrs('form')[0]['method'],'post')
                self.assertEqual(m.attrs('form')[0]['action'],'/api/consult')
                fields={a.get('name'):a for tag,a in m.tags if tag in ['input','textarea']}
                for field in ['name','email','phone','consent']: self.assertIn('required',fields[field])
                self.assertNotIn('checked',fields['consent'])
                self.assertEqual(fields['company_website']['tabindex'],'-1')
                self.assertEqual(fields['company_website']['autocomplete'],'off')
                self.assertIn('href="/privacy/"',form)
                if url != '/contact/':
                    self.assertIn('required',fields['location'])
                    self.assertEqual(fields['intent']['value'],'Sell or rent review')
        self.assertEqual(total,3)
        for url in ['/','/sell/']:
            slot=re.search(r'<section id="sell-or-rent".*?</section>',self.pages[url],re.S).group()
            self.assertIn('class="sell-or-rent__embed"><form',slot)

    def test_scoped_links(self):
        for url,text in self.pages.items():
            self.assertEqual(text.count('class="mgmt-referral"'),int(url=='/sell/'))
            self.assertEqual(text.count('https://threaltyinc.com/'),int(url=='/sell/'))
            self.assertEqual(text.count('https://ballpark.build'),int(url=='/about/'))
        self.assertEqual(len(Markup(self.pages['/podcast/']).attrs('article')),6)

    def test_removed_paths_and_redirects(self):
        paths=['career','work','media','docs','assets/nick-giulioni-resume.pdf','tools/regen_resume_pdf.sh','assets/og-career.png','assets/og-work.png','assets/og-media.png']
        for path in paths: self.assertFalse((ROOT/path).exists(),path)
        redirects={r['source']:r for r in self.config['redirects']}
        for old,new in [('career','about'),('work','about'),('media','podcast')]:
            for suffix in ['','/']:
                self.assertEqual(redirects['/'+old+suffix]['destination'],'/'+new+'/')
                self.assertTrue(redirects['/'+old+suffix]['permanent'])
        self.assertEqual(redirects['/assets/nick-giulioni-resume.pdf']['destination'],'/about/')
        self.assertEqual(redirects['/(.*)']['has'][0]['value'],'www.giulioni.com')
        self.assertTrue(self.config['trailingSlash'])

    def test_markup_and_references(self):
        for url,text in self.pages.items():
            with self.subTest(url=url):
                m=Markup(text)
                ids=[a['id'] for _,a in m.tags if 'id' in a]
                self.assertEqual(len(ids),len(set(ids)))
                self.assertFalse(m.attrs('iframe'))
                for a in m.attrs('script'): self.assertEqual(a.get('type'),'application/ld+json')
                for tag,a in m.tags:
                    self.assertFalse(any(k.startswith('on') or k=='style' for k in a))
                    for key in ['href','src']:
                        value=a.get(key,'')
                        if value.startswith('/') and not value.startswith('/api/'):
                            path=value.split('#')[0]
                            target=file_for(path) if path.endswith('/') else ROOT/path.lstrip('/')
                            self.assertTrue(target.exists(),value)
                    for label in ['for']:
                        if label in a: self.assertIn(a[label],ids)
                for a in m.attrs('img'):
                    for key in ['width','height','alt']: self.assertTrue(a.get(key))
        for url in ['/','/about/']:
            blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',self.pages[url])
            self.assertEqual(len(blocks),1)
            schema=json.loads(blocks[0]); self.assertEqual(schema['@type'],'RealEstateAgent')
            self.assertEqual([a['name'] for a in schema['areaServed']][:3],['Carmel, Indiana','Westfield, Indiana','Fishers, Indiana'])
        self.assertIn('fetchpriority="high"',self.pages['/'])
        self.assertIn('<picture>',self.pages['/'])

    def test_headers_and_deploy_exclusions(self):
        headers={h['key']:h['value'] for h in self.config['headers'][0]['headers']}
        self.assertEqual(headers['Content-Security-Policy'],"default-src 'self'; img-src 'self'; style-src 'self'; font-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'; frame-src 'none'; object-src 'none'; upgrade-insecure-requests")
        for key in ['X-Content-Type-Options','Referrer-Policy','Permissions-Policy']: self.assertTrue(headers[key])
        self.assertNotIn('git',self.config)
        for path in ['/contact/thanks/','/contact/error/','/api/(.*)']:
            self.assertIn({'source':path,'headers':[{'key':'X-Robots-Tag','value':'noindex'}]},self.config['headers'])
        excluded=(ROOT/'.vercelignore').read_text().splitlines()
        for value in ['/tests','/tools','/docs','/.git','/.vercel','/site.json']: self.assertIn(value,excluded)
        self.assertNotIn('/api',excluded)

    def test_sitemap_robots_css_fonts(self):
        tree=ET.parse(ROOT/'sitemap.xml')
        self.assertEqual({e.text for e in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')},{'https://giulioni.com'+u for u in PATHS})
        self.assertIn('Disallow: /api/',(ROOT/'robots.txt').read_text())
        css=(ROOT/'styles.css').read_text()
        self.assertIn(':focus-visible',css)
        self.assertIn('min-height:44px',css)
        for font in re.findall(r'url\("(/assets/fonts/[^\"]+)"\)',css): self.assertTrue((ROOT/font.lstrip('/')).exists())

    def test_area_paragraphs_are_distinct(self):
        seen=set()
        for city in AREA_SLUGS:
            text=self.pages['/areas/'+city+'/'].split('<section class="closing-cta">')[0]
            self.assertEqual(text.count('<section class="guide-group">'),3)
            paragraphs=re.findall(r'<div class="guide-item"><h3>.*?</h3><p>(.*?)</p>',text)
            self.assertGreaterEqual(len(paragraphs),6)
            for paragraph in paragraphs:
                self.assertNotIn(paragraph,seen)
                seen.add(paragraph)

    def test_sell_or_rent_steps_wrap_their_text(self):
        # Each step is a two-column grid (counter + text); a bare inline element would become its own grid cell.
        for url in ['/','/sell/']:
            steps=re.search(r'<ol class="steps">(.*?)</ol>',self.pages[url],re.S).group(1)
            items=re.findall(r'<li>(.*?)</li>',steps)
            self.assertEqual(len(items),3)
            for item in items: self.assertRegex(item,r'^<span>.*</span>$')

    def test_area_guides_keep_primary_towns_first(self):
        primary=['carmel','westfield','fishers']
        def order(fragment):
            found=re.findall(r'href="/areas/([a-z-]+)/"',fragment)
            seen=[]
            for slug in found:
                if slug not in seen: seen.append(slug)
            return seen
        for url,text in self.pages.items():
            with self.subTest(url=url):
                footer=re.search(r'<nav class="footer-areas".*?</nav>',text,re.S).group()
                self.assertEqual(order(footer),AREA_SLUGS)
                menu=re.search(r'<div class="nav-menu">.*?</div>',text,re.S).group()
                self.assertEqual(order(menu),AREA_SLUGS)
        self.assertEqual(order(re.search(r'<div class="town-ledger">.*?</section>',self.pages['/areas/'],re.S).group())[:6],AREA_SLUGS)
        self.assertNotIn('Coming later',self.pages['/areas/'])
        for slug in AREA_SLUGS:
            text=self.pages['/areas/'+slug+'/']
            self.assertEqual(order(re.search(r'<nav class="area-switch".*?</nav>',text,re.S).group()),AREA_SLUGS)
            self.assertIn('<title>',text)

    def test_photo_slots_collapse_and_render(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('render_site',ROOT/'tools/render_site.py')
        rs=importlib.util.module_from_spec(spec); spec.loader.exec_module(rs)
        self.assertEqual(set(self.site['area_photos']),set(AREA_SLUGS))
        if not self.site.get('hero_photo'): self.assertIn('/assets/portrait-nick-',re.search(r'<section class="home-hero">.*?</section>',self.pages['/'],re.S).group())
        if not self.site.get('about_photos'): self.assertNotIn('about-photos',self.pages['/about/'])
        for slug in AREA_SLUGS:
            if not self.site['area_photos'][slug]: self.assertNotIn('town-photo',self.pages['/areas/'+slug+'/'])
        sample={'id':'1602-w-76th-pl-exterior','alt':'Sample alt','caption':'Sample caption','credit':'Sample Credit','license':'CC BY 4.0','license_url':'https://creativecommons.org/licenses/by/4.0/','source_url':'https://example.org/photo'}
        html=rs.photo('work',sample,'100vw','town-photo__figure')
        for needle in ['type="image/avif"','type="image/webp"','.jpg 1600w','alt="Sample alt"','Sample caption','Photo: <a href="https://example.org/photo">Sample Credit</a>','CC BY 4.0</a>','loading="lazy"']:
            self.assertIn(needle,html)
        rs.NICK_DIR=rs.AREA_DIR='work'
        self.assertIn('fetchpriority="high"',rs.photo('work',sample,'100vw','x',priority=True))
        rs.S=dict(rs.S,area_photos={'carmel':sample},about_photos=[sample,sample,sample],hero_photo={'id':'1602-w-76th-pl-exterior','alt':'Hero alt'})
        self.assertIn('class="town-photo"',rs.area_photo('carmel'))
        self.assertEqual(rs.area_photo('westfield'),'')
        with self.assertRaises(ValueError): rs.S=dict(rs.S,area_photos={'carmel':dict(sample,credit='')}); rs.area_photo('carmel')
        self.assertEqual(rs.about_photos().count('<figure'),3)
        self.assertIn('about-photo--wide',rs.about_photos())
        self.assertIn('alt="Hero alt"',rs.hero_figure())
        with self.assertRaises(FileNotFoundError): rs.photo('work',{'id':'missing-file','alt':'x'},'100vw','x')

    def test_nick_photo_slots_preserve_family_frame(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('render_site',ROOT/'tools/render_site.py')
        rs=importlib.util.module_from_spec(spec); spec.loader.exec_module(rs)
        expected={
            'hero-01':[(533,800),(800,1200),(1067,1600)],
            'about-nick-diane-01':[(640,800),(960,1200),(1280,1600)],
            'about-family-01':[(640,800),(960,1200),(1280,1600)],
            'about-solo-02':[(800,534),(1200,800),(1600,1067)],
        }
        for id,dimensions in expected.items():
            for n,dim in zip([800,1200,1600],dimensions):
                self.assertEqual(rs.jpeg_size(ROOT/f'assets/nick/{id}-{n}.jpg'),dim)
                for ext in ['avif','webp','jpg']:
                    self.assertTrue((ROOT/f'assets/nick/{id}-{n}.{ext}').is_file())
        about=self.pages['/about/']
        section=re.search(r'<section class="about-photos.*?</section>',about).group()
        self.assertEqual(section.count('<figure'),3)
        self.assertEqual([a['alt'] for a in Markup(section).attrs('img')],[p['alt'] for p in self.site['about_photos']])
        family=re.search(r'<figure class="about-photo about-photo--family">.*?</figure>',section).group()
        self.assertIn('width="1280" height="1600"',family)
        self.assertIn('Photo: Ashlyn Peters Photography',family)
        self.assertNotIn('hero-portrait',family)
        self.assertNotIn('style=',family)
        css=(ROOT/'styles.css').read_text()
        rule=re.search(r'\.about-photo--family img\s*{([^}]+)}',css).group(1)
        self.assertIn('aspect-ratio: 4 / 5',rule)
        self.assertIn('object-fit: contain',rule)
        for selectors,decl in re.findall(r'([^{}]+){([^{}]*)}',css):
            if 'object-position' in decl:
                self.assertNotRegex(selectors,r'about-photo|(?:^|,)\s*(?:img|picture|figure)\b')

    def test_work_gallery_slot(self):
        items=self.site['work_gallery']
        self.assertIsInstance(items,list)
        credit=self.site.get('work_gallery_credit','')
        for url,text in self.pages.items():
            with self.subTest(url=url):
                if not items or url not in ['/','/about/']:
                    self.assertNotIn('work-gallery',text)
                else:
                    self.assertEqual(text.count('<li class="work-item'),len(items))
                    self.assertEqual('class="work-credit"' in text,bool(credit.strip()))
                    for item in items: self.assertIn('alt="'+item['alt']+'"',text)
        ids=[item['id'] for item in items]
        self.assertEqual(len(ids),len(set(ids)))
        for item in items:
            for key in ['id','place','detail','alt']: self.assertTrue(item.get(key),key)
            for ext in ['avif','webp','jpg']:
                self.assertTrue(list((ROOT/'assets/work').glob(item['id']+'-*.'+ext)),item['id']+' '+ext)

    def test_image_metadata_and_cards(self):
        for path in (ROOT/'assets').rglob('*'):
            if not path.is_file(): continue
            data=path.read_bytes()
            if path.suffix=='.png':
                offset=8
                while offset<len(data):
                    size=struct.unpack('>I',data[offset:offset+4])[0]; kind=data[offset+4:offset+8]
                    self.assertNotIn(kind,[b'eXIf',b'tEXt',b'zTXt',b'iTXt'],path.name)
                    offset+=12+size
            elif path.suffix=='.avif':
                self.assertNotIn(b'Exif',data,path.name)
                self.assertNotIn(b'<x:xmpmeta',data,path.name)
                for box in re.findall(rb'colr(....)',data): self.assertNotIn(box,[b'prof',b'rICC'],path.name)
            elif path.suffix=='.webp':
                for chunk in [b'EXIF',b'XMP ',b'ICCP']: self.assertNotIn(chunk,data,path.name)
            elif path.suffix in ['.jpg','.jpeg']:
                for marker in [b'Exif\x00\x00',b'http://ns.adobe.com/',b'ICC_PROFILE']: self.assertNotIn(marker,data,path.name)
        for card in ['home','sell','buy','areas','about','podcast']:
            data=(ROOT/f'assets/og-{card}.png').read_bytes()
            self.assertEqual(struct.unpack('>II',data[16:24]),(1200,630))

if __name__=='__main__': unittest.main()
