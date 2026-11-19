#!/usr/bin/env python3
"""Regenerate committed static pages after editing site.json or page copy."""
from pathlib import Path
from html import escape as e
import json
ROOT=Path(__file__).resolve().parents[1]
S=json.loads((ROOT/'site.json').read_text())
STAT='<span class="stat-properties">'+e(S['properties_touched'])+' properties touched</span>'
POD=e(S['podcast_line'])
TEL='<a href="'+S['phone_tel']+'">'+S['phone_display']+'</a>'
NAV=[('/sell/','Sell'),('/buy/','Buy'),('/areas/','Areas'),('/about/','About')]

def header(path):
    def link(href,label):
        a='<a href="'+href+'"'+(' aria-current="page"' if path.startswith(href) else '')+'>'+label+'</a>'
        if href!='/areas/': return a
        menu=''.join('<a href="/areas/'+slug+'/"'+(' aria-current="page"' if path=='/areas/'+slug+'/' else '')+'>'+city+'</a>' for slug,city,_ in ALL_AREAS)
        return '<div class="nav-areas">'+a+'<div class="nav-menu">'+menu+'</div></div>'
    links=''.join(link(href,label) for href,label in NAV)
    return ('<a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="site-header-inner">'
        '<p class="site-name"><a href="/"><span class="site-name__name">Nick Giulioni</span><span class="site-name__place">Carmel · Westfield · Fishers</span></a></p>'
        '<nav class="site-nav" aria-label="Primary">'+links+'</nav>'
        '<div class="site-actions"><a class="header-phone" href="'+S['phone_tel']+'">'+S['phone_display']+'</a>'
        '<a class="contact-link" href="/contact/"'+(' aria-current="page"' if path=='/contact/' else '')+'>Request a consult</a></div></div></header>')

FOOTER=('<footer class="site-footer"><div class="footer-top">'
    '<div class="footer-brand"><p class="footer-name">Nick Giulioni</p><p class="footer-tag">Buyer and seller representation in Carmel, Westfield and Fishers, Indiana, plus north Indianapolis, Noblesville and Zionsville.</p></div>'
    '<nav class="footer-nav" aria-label="Footer"><p class="footer-heading">Explore</p><a href="/sell/">Sell</a><a href="/buy/">Buy</a><a href="/areas/">Areas</a><a href="/about/">About</a><a href="/podcast/">Podcast</a><a href="/contact/">Contact</a></nav>'
    '<nav class="footer-areas" aria-label="Area guides"><p class="footer-heading">Area guides</p>'+''.join('<a href="/areas/'+slug+'/">'+city+'</a>' for slug,city in [('carmel','Carmel'),('westfield','Westfield'),('fishers','Fishers'),('north-indianapolis','North Indianapolis'),('noblesville','Noblesville'),('zionsville','Zionsville')])+'</nav>'
    '<div class="footer-contact"><p class="footer-heading">Contact</p><a href="'+S['phone_tel']+'">'+S['phone_display']+'</a><a href="mailto:'+S['email']+'">'+S['email']+'</a></div>'
    '</div><div class="footer-legal">'
    '<p class="disclosure">Nick Giulioni is an Indiana real estate broker affiliated with T&amp;H Realty Services, <span class="nowrap">760 E. 52nd St</span>, <span class="nowrap">Indianapolis, IN 46205</span>, <span class="nowrap">317-255-7767</span>.</p>'
    '<p class="housing"><img src="/assets/equal-housing.svg" width="28" height="28" alt="Equal Housing Opportunity"> Equal Housing Opportunity.</p>'
    '</div><div class="footer-base"><div class="footer-links"><a href="/privacy/">Privacy</a><a href="https://www.linkedin.com/in/nickgiulioni">LinkedIn</a></div>'
    '<p class="copyright">© 2026 Nick Giulioni</p></div></footer>')

def form(source,review=False):
    fields=''
    for name,label,kind,auto,limit in [('name','Name','text','name',100),('email','Email','email','email',254),('phone','Phone','tel','tel',40),('location','Property address' if review else 'City or address (optional)','text','street-address',300)]:
        required=' required' if name!='location' or review else ''
        fields+=f'<label for="{source}-{name}">{label}<input id="{source}-{name}" name="{name}" type="{kind}" autocomplete="{auto}" maxlength="{limit}"{required}></label>'
    intents='<input type="hidden" name="intent" value="Sell or rent review">' if review else '<fieldset class="intent-choices"><legend>What can I help with?</legend>'+''.join(f'<label class="choice"><input type="radio" name="intent" value="{v}" required> {v}</label>' for v in ['Buy','Sell','Both','Sell or rent review','Not sure'])+'</fieldset>'
    submit='Request my sell-or-rent review' if review else 'Request a consult'
    return f'<form method="post" action="/api/consult" class="consult-form"><input type="hidden" name="source" value="{source}"><div class="form-grid">{fields}</div>{intents}<label for="{source}-message">Message (optional)<textarea id="{source}-message" name="message" rows="4" maxlength="2000"></textarea></label><label class="honeypot" aria-hidden="true">Company website<input name="company_website" type="text" tabindex="-1" autocomplete="off"></label><label class="choice consent"><input type="checkbox" name="consent" value="yes" required> <span>I agree that Nick Giulioni may contact me by call, email, or text about this request. Message and data rates may apply. Reply STOP to opt out. See the <a href="/privacy/">privacy policy</a>.</span></label><button class="btn btn-primary" type="submit">{submit}</button></form>'

def slot(source):
    return ('<section id="sell-or-rent" class="sell-or-rent"><div class="sell-or-rent__intro"><p class="section-label">A decision before a listing</p><h2>Sell it or rent it?</h2>'
        '<ol class="steps"><li><span>Tell me the address.</span></li><li><span>I compare what it could sell for with what it could rent for.</span></li><li><span>I send it to you myself.</span></li></ol>'
        '<p class="sell-or-rent__caveat">This is not an instant appraisal.</p></div>'
        '<div class="sell-or-rent__embed">'+form(source,True)+'</div></section>')

def section(title,text,cls='editorial'): return '<section class="'+cls+'"><h2>'+title+'</h2><p>'+text+'</p></section>'

def cta(label='Request a consult'):
    return ('<section class="closing-cta"><div class="closing-cta__inner"><p class="closing-title">Let’s talk through <em>your next move</em></p>'
        '<div class="closing-actions"><a class="btn btn-primary btn-large" href="/contact/">'+label+'</a>'
        '<p class="closing-note">Or call '+TEL+'.<span class="closing-promise">I respond personally, usually the same day.</span>'+'</p><p class="signoff"><span>Talk soon,</span>Nick</p></div></div></section>')

# Schematic line maps of places named in the copy. Decorative and not to scale; the
# same places are named in the adjacent text, so each drawing is hidden from assistive tech.
MAP_NOTE='<p class="map-caption">Schematic, not to scale</p>'
MAPS={
'carmel':('<svg class="map map--carmel" viewBox="0 0 480 300" aria-hidden="true" focusable="false">'
    '<rect class="map-ground" width="480" height="300"/>'
    '<path class="map-road map-road--minor" d="M0 62H480M0 238H480"/>'
    '<rect class="map-district" x="150" y="124" width="166" height="52" rx="3"/>'
    '<path class="map-road" d="M0 150H480M330 0V300"/>'
    '<path class="map-trail" d="M206 0C204 70 212 120 208 170S200 250 204 300"/>'
    '<circle class="map-roundabout" cx="330" cy="62" r="13"/><circle class="map-roundabout" cx="330" cy="150" r="15"/><circle class="map-roundabout" cx="330" cy="238" r="13"/>'
    '<circle class="map-point" cx="208" cy="166" r="5"/>'
    '<text class="map-label map-label--trail" x="192" y="28" text-anchor="end">Monon</text><text class="map-label map-label--trail" x="192" y="50" text-anchor="end">Greenway</text>'
    '<text class="map-label map-label--place" x="24" y="96">Arts &amp; Design</text><text class="map-label map-label--place" x="24" y="118">District</text>'
    '<text class="map-label" x="24" y="200">Main St</text>'
    '<text class="map-label" x="346" y="98">Range</text><text class="map-label" x="346" y="120">Line Rd</text>'
    '<text class="map-label map-label--muted" x="352" y="282">roundabouts</text></svg>'),
'westfield':('<svg class="map map--westfield" viewBox="0 0 480 300" aria-hidden="true" focusable="false">'
    '<rect class="map-ground" width="480" height="300"/>'
    '<path class="map-road map-road--minor" d="M0 286H480"/>'
    '<rect class="map-park" x="34" y="62" width="272" height="206" rx="4"/>'
    +''.join(f'<rect class="map-field" x="{52+c*62}" y="{82+r*60}" width="50" height="42" rx="2"/><path class="map-field-line" d="M{77+c*62} {82+r*60}v42"/><circle class="map-field-line" cx="{77+c*62}" cy="{103+r*60}" r="7"/>' for r in range(2) for c in range(4))
    +''.join(f'<path class="map-diamond" d="M{52+c*62} 250v-42a42 42 0 0 1 42 42z"/>' for c in range(4))+
    '<path class="map-trail" d="M366 0C362 80 370 150 364 210S358 270 362 300"/>'
    '<text class="map-label map-label--place" x="34" y="44">Grand Park</text>'
    '<text class="map-label map-label--trail" x="382" y="150">Monon</text><text class="map-label map-label--trail" x="382" y="172">Trail</text></svg>'),
'fishers':('<svg class="map map--fishers" viewBox="0 0 480 300" aria-hidden="true" focusable="false">'
    '<rect class="map-ground" width="480" height="300"/>'
    '<path class="map-road map-road--minor" d="M0 84H480M0 252H480"/>'
    '<path class="map-river" d="M60 0C108 70 30 130 64 196S110 260 94 300"/>'
    '<path class="map-highway" d="M380 300L480 110"/>'
    +''.join(f'<rect class="map-block" x="{x}" y="{y}" width="26" height="22" rx="2"/>' for x in [190,220,264,294] for y in [112,142,172])+
    '<path class="map-trail" d="M252 0V300"/>'
    '<rect class="map-district" x="336" y="154" width="70" height="44" rx="3"/>'
    '<text class="map-label map-label--river" x="102" y="150">White</text><text class="map-label map-label--river" x="102" y="172">River</text>'
    '<text class="map-label map-label--trail" x="266" y="34">Nickel Plate</text><text class="map-label map-label--trail" x="266" y="56">Trail</text>'
    '<text class="map-label" x="244" y="230" text-anchor="end">Downtown</text>'
    '<text class="map-label map-label--place" x="336" y="120">Fishers</text><text class="map-label map-label--place" x="336" y="142">District</text>'
    '<text class="map-label map-label--muted" x="420" y="282">I-69</text></svg>'),
}
MAPS['north-indianapolis']=('<svg class="map map--north-indianapolis" viewBox="0 0 480 300" aria-hidden="true" focusable="false">'
    '<rect class="map-ground" width="480" height="300"/>'
    '<path class="map-road map-road--minor" d="M0 58H480M0 176H480"/>'
    '<path class="map-road" d="M60 0V300"/>'
    '<path class="map-river" d="M0 128C90 112 170 150 250 132S400 96 480 104"/>'
    '<path class="map-river map-river--canal" d="M300 176C262 198 236 230 222 300"/>'
    '<path class="map-trail" d="M318 300C314 220 322 160 316 100S318 30 322 0"/>'
    '<circle class="map-point" cx="317" cy="176" r="5"/><circle class="map-point" cx="320" cy="58" r="5"/>'
    '<text class="map-label" x="74" y="48">86th St</text>'
    '<text class="map-label map-label--place" x="336" y="44">Nora</text>'
    '<text class="map-label map-label--river" x="74" y="100">White River</text>'
    '<text class="map-label" transform="translate(48 292) rotate(-90)">Meridian St</text>'
    '<text class="map-label map-label--place" x="334" y="206">Broad</text><text class="map-label map-label--place" x="334" y="228">Ripple</text>'
    '<text class="map-label map-label--river" x="212" y="274" text-anchor="end">Canal</text>'
    '<text class="map-label map-label--place" x="76" y="212">Meridian-</text><text class="map-label map-label--place" x="76" y="234">Kessler</text>'
    '<text class="map-label map-label--trail" x="334" y="262">Monon</text><text class="map-label map-label--trail" x="334" y="284">Trail</text></svg>')
MAPS['noblesville']=('<svg class="map map--noblesville" viewBox="0 0 480 300" aria-hidden="true" focusable="false">'
    '<rect class="map-ground" width="480" height="300"/>'
    '<path class="map-road map-road--minor" d="M0 60H480M0 270H480M420 0V300"/>'
    '<path class="map-river" d="M150 0C130 80 172 150 140 220S120 280 130 300"/>'
    +''.join(f'<rect class="map-block" x="{x}" y="{y}" width="34" height="30" rx="2"/>' for x in [220,262,304] for y in [100,140,180] if not (x==262 and y==140))+
    '<rect class="map-district" x="262" y="140" width="34" height="30" rx="2"/><circle class="map-point" cx="279" cy="155" r="5"/>'
    '<text class="map-label" x="220" y="90">Downtown</text>'
    '<text class="map-label map-label--place" x="220" y="236">Courthouse</text><text class="map-label map-label--place" x="220" y="258">square</text>'
    '<text class="map-label map-label--river" x="34" y="140">White</text><text class="map-label map-label--river" x="34" y="162">River</text></svg>')
MAPS['zionsville']=('<svg class="map map--zionsville" viewBox="0 0 480 300" aria-hidden="true" focusable="false">'
    '<rect class="map-ground" width="480" height="300"/>'
    '<path class="map-road map-road--minor" d="M0 270H480M0 118H140M330 118H480"/>'
    '<path class="map-trail map-trail--thin" d="M64 300C92 236 60 170 84 110S70 30 96 0"/>'
    +''.join(f'<rect class="map-block" x="{x}" y="{y}" width="30" height="26" rx="2"/>' for x in [168,232] for y in [62,96,130,164,198])+
    '<path class="map-brick" d="M215 40V250"/>'
    '<rect class="map-park" x="300" y="150" width="78" height="60" rx="3"/>'
    '<text class="map-label map-label--place" x="215" y="28" text-anchor="middle">Brick Main Street</text>'
    '<text class="map-label" x="300" y="96">The Village</text>'
    '<text class="map-label map-label--trail" x="300" y="236">Lincoln Park</text>'
    '<text class="map-label map-label--muted" x="104" y="232">trail</text></svg>')
COUNTY=('<svg class="map map--county" viewBox="0 0 480 360" role="img" aria-label="Schematic map, not to scale: Westfield sits north of Carmel along the Monon, and Fishers lies east of Carmel across the White River.">'
    '<rect class="map-ground" width="480" height="360"/>'
    '<rect class="map-town" x="34" y="24" width="252" height="138" rx="4"/>'
    '<rect class="map-town" x="34" y="176" width="196" height="160" rx="4"/>'
    '<rect class="map-town" x="276" y="176" width="172" height="160" rx="4"/>'
    '<path class="map-river" d="M352 0C330 70 300 120 262 168S246 280 254 360"/>'
    '<path class="map-trail" d="M150 360C148 250 154 160 150 0"/>'
    '<path class="map-trail map-trail--thin" d="M330 228V336"/>'
    '<circle class="map-point" cx="104" cy="112" r="5"/><circle class="map-point" cx="151" cy="262" r="5"/><circle class="map-point" cx="420" cy="300" r="5"/>'
    '<text class="map-town-name" x="52" y="62">Westfield</text><text class="map-town-name" x="52" y="214">Carmel</text><text class="map-town-name" x="294" y="214">Fishers</text>'
    '<text class="map-label" x="114" y="130">Grand Park</text>'
    '<text class="map-label" x="62" y="290">Arts &amp; Design</text><text class="map-label" x="62" y="312">District</text>'
    '<text class="map-label" x="410" y="306" text-anchor="end">Fishers</text><text class="map-label" x="410" y="328" text-anchor="end">District</text>'
    '<text class="map-label map-label--trail" x="160" y="154">Monon</text>'
    '<text class="map-label map-label--trail" x="340" y="254">Nickel</text><text class="map-label map-label--trail" x="340" y="276">Plate</text>'
    '<text class="map-label map-label--river" x="324" y="40">White River</text></svg>')

AREAS=[('carmel','Carmel','Start here if established neighborhoods and time on the Monon are on your list.'),('westfield','Westfield','Compare new-build plans with existing homes, and put Grand Park on your map.'),('fishers','Fishers','Compare downtown routines with life closer to Fishers District.')]
# Added after the three primary towns, which always stay first.
MORE_AREAS=[('north-indianapolis','North Indianapolis','Meridian-Kessler, Broad Ripple and Nora: older homes, the Monon Trail and the Central Canal.'),('noblesville','Noblesville','Start at the courthouse square, then compare streets near the White River with newer neighborhoods.'),('zionsville','Zionsville','The Village’s brick Main Street, nearby parks and trails, and a range of home ages.')]
ALL_AREAS=AREAS+MORE_AREAS
def towns(level='h2',items=None):
    return '<div class="town-ledger">'+''.join(f'<article class="town town--{slug}"><div class="town-map">{MAPS[slug]}{MAP_NOTE}</div><div class="town-body"><{level} class="town-name"><a href="/areas/{slug}/">{city}</a></{level}><p>{desc}</p><p class="town-more" aria-hidden="true">Read the {city} guide <span>→</span></p></div></article>' for slug,city,desc in (items or AREAS))+'</div>'

def more_towns():
    return ('<div class="more-towns"><p class="more-towns__label">More area guides</p><ul>'+''.join(f'<li><a href="/areas/{slug}/"><span class="more-towns__name">{city}</span><span class="more-towns__desc">{desc}</span><span class="more-towns__more" aria-hidden="true">Read the guide <span>→</span></span></a></li>' for slug,city,desc in MORE_AREAS)+'</ul></div>')

def area_switch(current):
    return '<nav class="area-switch" aria-label="Area guides">'+''.join('<a href="/areas/'+slug+'/"'+(' aria-current="page"' if slug==current else '')+'>'+city+'</a>' for slug,city,_ in ALL_AREAS)+'</nav>'

def picture(sizes,cls='portrait',priority=False,caption=''):
    widths=[160,200,320,348,400,636]
    webp=', '.join(f'/assets/portrait-nick-{w}.webp {w}w' for w in widths)
    jpg=', '.join(f'/assets/portrait-nick-{w}.jpg {w}w' for w in widths)
    pri=' fetchpriority="high"' if priority else ' loading="lazy" decoding="async"'
    cap=f'<figcaption>{caption}</figcaption>' if caption else ''
    return f'<figure class="{cls}"><picture><source type="image/webp" srcset="{webp}" sizes="{sizes}"><img src="/assets/portrait-nick-400.jpg" srcset="{jpg}" sizes="{sizes}" width="636" height="954"{pri} alt="Nick Giulioni seated and looking out a window."></picture>{cap}</figure>'

# Work gallery: renders only when site.json "work_gallery" lists approved, metadata-stripped photos.
# Each entry: {"id": "<file id>", "place": "...", "detail": "...", "alt": "..."}. Files live at
# /assets/work/<id>-<800|1200|1600>.<avif|webp|jpg> (the number is the long edge). Order in the list is display order.
# "work_gallery_credit" is an optional photo credit line; blank renders nothing.
WORK_SIZES=[800,1200,1600]
def jpeg_size(path):
    data=path.read_bytes(); i=2
    while i<len(data):
        if data[i]!=0xFF: i+=1; continue
        marker=data[i+1]; length=int.from_bytes(data[i+2:i+4],'big')
        if marker in (0xC0,0xC1,0xC2): return int.from_bytes(data[i+7:i+9],'big'),int.from_bytes(data[i+5:i+7],'big')
        i+=2+length
    raise ValueError(path)

def work_item(item,index):
    files=[(ROOT/'assets/work'/f'{item["id"]}-{n}.jpg',n) for n in WORK_SIZES]
    files=[(f,n) for f,n in files if f.exists()]
    dims=[(jpeg_size(f),n) for f,n in files]
    (w,h),largest=dims[-1]
    shape='portrait' if h>w else 'landscape'
    srcset=lambda ext: ', '.join(f'/assets/work/{item["id"]}-{n}.{ext} {dw}w' for (dw,_),n in dims)
    if index==0: sizes='(max-width: 700px) 80vw, (max-width: 1100px) calc(100vw - 2.5rem), 790px'
    elif shape=='portrait': sizes='(max-width: 700px) 36vw, (max-width: 1100px) 21vw, 390px'
    else: sizes='(max-width: 700px) 80vw, (max-width: 1100px) 50vw, 390px'
    pic=(f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}"><source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
        f'<img src="/assets/work/{item["id"]}-{dims[0][1]}.jpg" srcset="{srcset("jpg")}" sizes="{sizes}" width="{w}" height="{h}" alt="{e(item["alt"])}" loading="lazy" decoding="async"></picture>')
    cap='<figcaption><span class="work-detail">'+e(item['detail'])+'</span><span class="work-place">'+e(item['place'])+'</span></figcaption>'
    cls='work-item work-item--'+shape+(' work-item--feature' if index==0 else '')
    return f'<li class="{cls}"><figure>{pic}{cap}</figure></li>'

def gallery():
    items=S.get('work_gallery') or []
    if not items: return ''
    credit=S.get('work_gallery_credit','').strip()
    cells=''.join(work_item(item,i) for i,item in enumerate(items))
    return ('<section class="work-gallery" aria-labelledby="work-gallery-title"><div class="work-head"><p class="section-label">Investing and renovation</p><h2 id="work-gallery-title">Properties I’ve worked on</h2>'
        '<p>From my investing and renovation experience, in Indianapolis and the Bloomington area.</p></div>'
        '<p class="work-count" aria-hidden="true">'+str(len(items))+' photos <span>· swipe for more</span></p><ul class="work-grid" tabindex="0" aria-label="Property photos">'+cells+'</ul>'
        +(f'<p class="work-credit">Photos: {e(credit)}</p>' if credit else '')+'</section>')

# Photo slots (all optional, all driven by site.json; an empty slot renders nothing or falls back):
#   "hero_photo":   null | {"id","alt"}                                    -> /assets/nick/<id>-<size>.<ext>  (home hero; falls back to the existing portrait)
#   "about_photos": [] | up to three {"id","alt","caption"?,"credit"?}       -> /assets/nick/<id>-<size>.<ext>  (About page)
#   "area_photos":  {"<area-slug>": null | {"id","alt","caption","credit","license"?,"license_url"?,"source_url"?}} -> /assets/areas/<id>-<size>.<ext>
# <size> is the long edge in pixels (any of 800, 1200, 1600, 2400 that exist); each size needs .avif, .webp and .jpg.
SLOT_SIZES=[800,1200,1600,2400]
NICK_DIR='nick'; AREA_DIR='areas'
def photo(folder,item,sizes,cls,priority=False,with_caption=True):
    found=[n for n in SLOT_SIZES if (ROOT/'assets'/folder/f'{item["id"]}-{n}.jpg').exists()]
    if not found: raise FileNotFoundError(f'assets/{folder}/{item["id"]}-<size>.jpg')
    for n in found:
        for ext in ['avif','webp']:
            if not (ROOT/'assets'/folder/f'{item["id"]}-{n}.{ext}').exists(): raise FileNotFoundError(f'assets/{folder}/{item["id"]}-{n}.{ext}')
    dims=[(jpeg_size(ROOT/'assets'/folder/f'{item["id"]}-{n}.jpg'),n) for n in found]
    (w,h),_=dims[-1]
    srcset=lambda ext: ', '.join(f'/assets/{folder}/{item["id"]}-{n}.{ext} {dw}w' for (dw,_),n in dims)
    load=' fetchpriority="high"' if priority else ' loading="lazy" decoding="async"'
    pic=(f'<picture><source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}"><source type="image/webp" srcset="{srcset("webp")}" sizes="{sizes}">'
        f'<img src="/assets/{folder}/{item["id"]}-{dims[0][1]}.jpg" srcset="{srcset("jpg")}" sizes="{sizes}" width="{w}" height="{h}" alt="{e(item["alt"])}"{load}></picture>')
    cap=''
    if with_caption and (item.get('caption') or item.get('credit')):
        credit=''
        if item.get('credit'):
            who=e(item['credit'])
            if item.get('source_url'): who=f'<a href="{e(item["source_url"])}">{who}</a>'
            lic=e(item.get('license','')) if item.get('license') else ''
            if lic and item.get('license_url'): lic=f'<a href="{e(item["license_url"])}">{lic}</a>'
            credit='<span class="photo-credit">Photo: '+who+(f' · {lic}' if lic else '')+'</span>'
        cap='<figcaption>'+(f'<span class="photo-caption">{e(item["caption"])}</span>' if item.get('caption') else '')+credit+'</figcaption>'
    return f'<figure class="{cls}">{pic}{cap}</figure>'

def hero_figure():
    item=S.get('hero_photo')
    if item: return photo(NICK_DIR,item,HERO_SIZES,'portrait hero-portrait',priority=True,with_caption=False)
    return picture(HERO_SIZES,'portrait hero-portrait',True)

def about_photos():
    items=(S.get('about_photos') or [])[:3]
    if not items: return ''
    figures=[]
    for index,item in enumerate(items):
        wide=len(items)==1 or (len(items)==3 and index==2)
        sizes='(max-width: 900px) calc(100vw - 2.5rem), 760px' if wide else '(max-width: 700px) calc((100vw - 3.75rem) / 2), 370px'
        if len(items)==3:
            sizes='(max-width: 1296px) calc(100vw - clamp(2.5rem, 8vw, 6rem)), 1200px' if wide else '(max-width: 1296px) calc((100vw - clamp(2.5rem, 8vw, 6rem) - 1.25rem) / 2), 590px'
        elif len(items)==2:
            sizes='(max-width: 700px) calc(100vw - 2.5rem), 560px'
        cls='about-photo'
        if len(items)==3 and index==2: cls+=' about-photo--wide'
        if item['id']=='about-family-01': cls+=' about-photo--family'
        figures.append(photo(NICK_DIR,item,sizes,cls))
    return '<section class="about-photos about-photos--'+str(len(items))+'">'+''.join(figures)+'</section>'

def area_photo(slug):
    item=(S.get('area_photos') or {}).get(slug)
    if not item: return ''
    if not item.get('credit'): raise ValueError('area_photos.'+slug+' needs a credit')
    return '<section class="town-photo">'+photo(AREA_DIR,item,'(max-width: 1240px) calc(100vw - 2.5rem), 1200px','town-photo__figure')+'</section>'

def guide(groups):
    out=''
    for title,items in groups:
        body=''
        for h,text,source in items:
            body+='<div class="guide-item"><h3>'+h+'</h3><p>'+text+'</p>'+(f'<p class="source">{source}</p>' if source else '')+'</div>'
        out+='<section class="guide-group"><h2>'+title+'</h2><div class="guide-items">'+body+'</div></section>'
    return out

def guide_cta(city):
    others=[(slug,c) for slug,c,_ in ALL_AREAS if c!=city]
    return ('<aside class="guide-cta"><div class="guide-cta__text"><p class="guide-cta__title">Comparing '+city+' with nearby areas?</p><p>Read the other guides, then bring your shortlist to a consult.</p></div>'
        '<div class="guide-cta__actions">'+''.join(f'<a class="guide-cta__link" href="/areas/{slug}/">{c} <span aria-hidden="true">→</span></a>' for slug,c in others)+'</div></aside>')

def page(path,title,description,h1,body,card='home',noindex=False,hero=False,kicker='Central Indiana real estate',deck='',actions='',extra='',art='',variant=''):
    url='https://giulioni.com'+path
    head=f'<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>{e(title)}</title><meta name="description" content="{e(description)}">'
    if not noindex: head+=f'<link rel="canonical" href="{url}">'
    for prefix,key in [('property','og:title'),('property','og:description'),('property','og:url'),('property','og:type'),('property','og:image'),('property','og:image:width'),('property','og:image:height'),('property','og:image:alt'),('name','twitter:card'),('name','twitter:title'),('name','twitter:description'),('name','twitter:image'),('name','twitter:image:alt')]:
        value={'og:title':title,'og:description':description,'og:url':url,'og:type':'website','og:image':'https://giulioni.com/assets/og-'+card+'.png','og:image:width':'1200','og:image:height':'630','og:image:alt':'Nick Giulioni, Indiana real estate broker','twitter:card':'summary_large_image','twitter:title':title,'twitter:description':description,'twitter:image':'https://giulioni.com/assets/og-'+card+'.png','twitter:image:alt':'Nick Giulioni, Indiana real estate broker'}[key]
        head+=f'<meta {prefix}="{key}" content="{e(value)}">'
    head+='<meta name="theme-color" content="#1c3a2d"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="icon" href="/favicon.ico" sizes="any"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="stylesheet" href="/styles.css">'
    for font in ['instrument-serif-latin-normal','instrument-sans-latin-wght']: head+=f'<link rel="preload" href="/assets/fonts/{font}.woff2" as="font" type="font/woff2" crossorigin>'
    if noindex: head+='<meta name="robots" content="noindex">'
    if path in ['/', '/about/']:
        schema={'@context':'https://schema.org','@type':'RealEstateAgent','name':'Nick Giulioni','url':'https://giulioni.com/','email':S['email'],'telephone':'+1-463-223-9952','image':'https://giulioni.com/assets/portrait-nick-636.jpg','areaServed':[{'@type':'City','name':x+', Indiana'} for x in ['Carmel','Westfield','Fishers','Indianapolis','Noblesville','Zionsville']],'worksFor':{'@type':'RealEstateAgent','name':'T&H Realty Services','telephone':'317-255-7767','address':{'@type':'PostalAddress','streetAddress':'760 E. 52nd St','addressLocality':'Indianapolis','addressRegion':'IN','postalCode':'46205'}}}
        head+='<script type="application/ld+json">'+json.dumps(schema)+'</script>'
    heading=''
    if not hero:
        cls='page-header'+(' page-header--'+variant if variant else '')
        inner='<div class="page-header__text"><p class="page-kicker">'+kicker+'</p><h1 class="page-title">'+e(h1)+'</h1>'+(f'<p class="page-deck">{deck}</p>' if deck else '')+(f'<div class="hero-actions">{actions}</div>' if actions else '')+extra+'</div>'
        heading='<header class="'+cls+'">'+inner+art+'</header>'
    slug=('home' if path=='/' else path.strip('/').replace('/','-').replace('.html',''))
    dest=ROOT/('404.html' if path=='/404.html' else path.lstrip('/')+'index.html'); dest.parent.mkdir(parents=True,exist_ok=True)
    main=(heading+body).replace('new-build','<span class="nowrap">new-build</span>')
    dest.write_text('<!doctype html>\n<html lang="en"><head>'+head+'</head><body class="page-'+slug+'">'+header(path)+'<main id="main" class="page-main">'+main+'</main>'+FOOTER+'</body></html>\n')

MEDIA='<article class="media-entry">\n      <div class="media-meta"><h2 class="show-name">Roots Realty Co.</h2></div>\n      <div class="entry-detail">\n        <p class="episode-title"><a href="https://www.rootsrealty.co/podcast/nick-giulioni-real-estate">You WON\'T BELIEVE Nick Giulioni\'s Journey from Tech to Real Estate</a></p>\n        <p>Nick talks about moving from technology into Indiana real estate and building operating businesses.</p>\n      </div>\n    </article>\n<article class="media-entry">\n      <div class="media-meta"><h2 class="show-name">The Leverage Podcast</h2></div>\n      <div class="entry-detail">\n        <p class="episode-title"><a href="https://www.youtube.com/watch?v=_A2HrOjWe50">The Leverage Podcast - Nick Giulioni</a></p>\n        <p>Nick talks about his work, investments, and operating background.</p>\n      </div>\n    </article>\n<article class="media-entry">\n      <div class="media-meta"><h2 class="show-name">The Intrigue Podcast (formerly The Circle Investor Meetup &amp; Podcast)</h2></div>\n      <div class="entry-detail">\n        <p class="episode-title"><a href="https://www.youtube.com/watch?v=dv72SopKqeM">Episode 1 - Nick Giulioni: How To Go From Side Hustle To Real Business</a></p>\n        <p>Nick talks through the shift from a side hustle into an operating business.</p>\n      </div>\n    </article>\n<article class="media-entry">\n      <div class="media-meta"><h2 class="show-name">Going Long with Billy Keels</h2></div>\n      <div class="entry-detail">\n        <p class="episode-title"><a href="https://www.youtube.com/watch?v=B3gRQMjCng0">Convert I.T. Skills Into Long Distance Real Estate Investing Success - Nick Giulioni</a></p>\n        <p>Nick talks about applying an I.T. background to long-distance real-estate investing.</p>\n      </div>\n    </article>\n<article class="media-entry">\n      <div class="media-meta"><h2 class="show-name">Simple Quarters</h2></div>\n      <div class="entry-detail">\n        <p class="episode-title"><a href="https://www.simplequarters.com/podcasts/finding-deals-in-todays-real-estate-market">Finding Deals In Today\'s Real Estate Market</a></p>\n        <p>Nick and Brett Snodgrass discuss finding deals, seller conversations, due diligence, and building a team.</p>\n      </div>\n    </article>\n<article class="media-entry">\n      <div class="media-meta"><h2 class="show-name">Hacking Real Estate Podcast</h2></div>\n      <div class="entry-detail">\n        <p class="episode-title"><a href="https://www.hackingrealestatepodcast.com/episodes/104-nick-giulioni">Episode 4 Nick Giulioni</a></p>\n        <p>Nick talks about moving from tech work into real estate, remote operations, and wedding venues.</p>\n      </div>\n    </article>'

HERO_SIZES='(max-width: 900px) calc(100vw - 2.5rem), (max-width: 1280px) 36vw, 460px'
CALL_LINK='<p class="hero-call">Or call '+TEL+'</p>'
FACTS=('<section class="facts" aria-label="At a glance"><div class="facts-grid"><ul class="facts-list">'
    '<li class="fact"><span class="fact-figure">'+e(S['properties_touched'])+'</span><span class="fact-label">properties touched</span><span class="fact-note">From my investing and renovation experience.</span></li>'
    '<li class="fact"><span class="fact-figure">Since 2017</span><span class="fact-label">investing in Central Indiana</span></li>'
    '<li class="fact"><span class="fact-figure">Carmel</span><span class="fact-label">where I live</span></li></ul>'
    '<div class="fact fact--podcast"><p class="fact-kicker">Podcast</p><p class="fact-quote">'+POD+'</p><a href="/podcast/">Podcast and earlier media</a></div></div></section>')
HOME=('<section class="home-hero"><div class="hero-grid">'
    '<div class="hero-content"><p class="page-kicker">Indiana real estate broker<span class="kicker-sep"> · </span><span class="kicker-firm">T&amp;H Realty Services</span></p>'
    '<h1 class="hero-lede">Your next move in <em>Carmel, Westfield and Fishers</em></h1>'
    '<p class="hero-targeting">I’m Nick Giulioni, an agent who has been on the other side. Buy or sell with an investor who knows what a house needs.</p>'
    '<div class="hero-actions"><a class="btn btn-primary btn-large" href="/contact/">Request a consult</a><p class="hero-call">Or call '+TEL+'</p></div>'
    '</div>'+hero_figure()+'</div></section>'
    +FACTS+
    '<section class="approach"><div class="approach-head"><p class="section-label">The approach</p><h2>A practical eye for <em>your next home</em></h2></div>'
    '<p class="approach-lead">My background is in tech sales. I have been investing in Central Indiana since 2017. Years running renovation and new-build work taught me to look past finishes and ask what a property needs. I live in Carmel. Now I represent buyers and sellers in Carmel, Westfield, and Fishers, bringing that experience to the conversation.</p>'
    '<div class="paths"><a class="path" href="/sell/"><span class="path-kicker">Selling</span><span class="path-title">Thinking about selling?</span><span class="path-text">Start with your timing, the condition of the home, and what you want to do next.</span><span class="path-arrow" aria-hidden="true">→</span></a>'
    '<a class="path" href="/buy/"><span class="path-kicker">Buying</span><span class="path-title">Start with the right town</span><span class="path-text">Compare towns, home condition and new-build choices before narrowing the home list.</span><span class="path-arrow" aria-hidden="true">→</span></a></div></section>'
    +gallery()+
    '<section class="towns"><div class="towns-head"><div><p class="section-label">Area guides</p><h2>Find the town that fits <em>your day</em></h2></div><div class="towns-head__aside"><p>Choose the daily routine first. Then choose the home.</p><a class="text-link" href="/areas/">See every area guide</a></div></div>'+towns('h3')+more_towns()+'</section>'
    +slot('sell-or-rent-home')+cta())

AREA_ACTIONS='<a class="btn btn-primary btn-large" href="/contact/">Request a consult</a>'+CALL_LINK
def area_page(slug,city,title,description,deck,groups,h1=None,county='Hamilton County'):
    page('/areas/'+slug+'/',title,description,h1 or 'Living in '+city+', Indiana',area_photo(slug)+guide(groups)+guide_cta(city)+cta(),card='areas',kicker='Area guide · '+county+', Indiana',deck=deck,actions=AREA_ACTIONS,extra=area_switch(slug),art='<div class="page-header__art">'+MAPS[slug]+MAP_NOTE+'</div>',variant='area')

def build():
    page('/', 'Nick Giulioni | Carmel, Westfield and Fishers real estate broker', 'Buyer and seller help in Carmel, Westfield and Fishers from an investor with renovation experience and T&H Realty Services broker.', '', HOME, hero=True)
    page('/sell/', 'Selling a home in Carmel, Westfield or Fishers | Nick Giulioni', 'A personal seller consult, preparation advice and a sell-versus-rent review for your Carmel, Westfield or Fishers home.', 'Thinking about selling in Carmel, Westfield, or Fishers?',
     section('A listing consult starts with listening','We talk through your goals, walk the property, and identify the questions that need answering before a listing.','lede-block')
     +'<section class="pair"><div class="pair-item"><h2>Selling is one option</h2><p>Keeping a property means weighing rent, expenses, repair reserves, and the time you want to put into it. Selling means weighing preparation, timing, and what you would do with the proceeds. The numbers I share are not an appraisal.</p></div>'
     '<div class="pair-item"><h2>Fix what matters</h2><p>Years running renovation and new-build work help me ask useful questions about condition. We can separate work worth pricing before a listing from changes a buyer may prefer to make. An older home and a new build deserve different preparation conversations.</p></div></section>'
     +'<section class="process-panel"><h2>A clear process, with me directly</h2><div class="process-body"><p>I am newly licensed as a broker. I bring '+STAT+' from my investing and renovation experience, and I live in Carmel. We agree on priorities, review the pricing rationale together, and set a communication plan before moving forward.</p>'
     '<p class="mgmt-referral">If you would rather keep the property and have it managed, I can introduce you to <a href="https://threaltyinc.com/">T&amp;H</a>.</p></div></section>'+slot('sell-or-rent-sell')+cta('Request a seller consult'),
     card='sell', kicker='Indiana real estate broker<span class="kicker-sep"> · </span><span class="kicker-firm">T&amp;H Realty Services</span>', deck='Start with your timing, the condition of the home, and what you want to do next.', actions='<a class="btn btn-primary btn-large" href="/contact/">Request a seller consult</a><p class="hero-call">Or call '+TEL+'</p><a class="hero-link hero-link--quiet" href="#sell-or-rent">Ask about sell or rent</a>', art=picture('(max-width: 900px) 88px, 300px','portrait header-portrait'), variant='portrait')
    page('/buy/', 'Buying a home in Carmel, Westfield or Fishers | Nick Giulioni', 'Compare towns, home condition and new-build choices with a personal Hamilton County buyer consult from Nick Giulioni.', 'Buying in Hamilton County? Start with the right town.', section('Choose your everyday routine','Start with where you need to be, what you want nearby, and how much house you want to look after. Compare <a href="/areas/carmel/">Carmel</a>, <a href="/areas/westfield/">Westfield</a>, and <a href="/areas/fishers/">Fishers</a>, or look at <a href="/areas/north-indianapolis/">north Indianapolis</a>, <a href="/areas/noblesville/">Noblesville</a> and <a href="/areas/zionsville/">Zionsville</a>, before narrowing the home list.','lede-block')+'<section class="pair"><div class="pair-item"><h2>Look beyond the finishes</h2><p>For an existing home, we can talk through condition, likely projects, and what to ask an inspector. For a new build, we can compare the base plan with options, timing, and the finished cost. My renovation background helps frame the questions; specialist inspections still matter.</p></div><div class="pair-item"><h2>What a buyer consult covers</h2><p>We discuss your budget, timing, location, and tolerance for projects. Then we agree on the next steps, including financing conversations and a plan for seeing homes. Live listing search comes later. For now, tell me what you are looking for.</p></div></section>'+cta('Request a buyer consult'),card='buy',kicker='Buying · Hamilton County',deck='Choose the everyday routine first. Then look beyond the finishes.',art='<div class="page-header__art">'+COUNTY+'</div>',variant='area')
    page('/areas/', 'Carmel, Westfield, Fishers and nearby: where to live | Nick Giulioni', 'A practical starting point for choosing between Carmel, Westfield and Fishers, plus north Indianapolis, Noblesville and Zionsville.', 'Carmel, Westfield, Fishers and nearby', '<section class="towns towns--index">'+towns(items=ALL_AREAS)+'</section>'+cta(),card='areas',kicker='Area guides · Central Indiana',deck='Choose the daily routine first. Then choose the home. Carmel, Westfield and Fishers come first, with guides for north Indianapolis, Noblesville and Zionsville below.',art='<div class="page-header__art">'+COUNTY+'</div>',variant='area')

    CARMEL_SRC='<a href="https://www.carmel.in.gov/our-city/resident/arts-design-district">'
    area_page('carmel','Carmel','Living in Carmel, Indiana: real estate guide | Nick Giulioni', 'Living in Carmel, Indiana: compare the Arts and Design District, home choices and renovation tradeoffs with a local broker.',
     'Compare the Arts and Design District, home choices and renovation tradeoffs with a broker who lives in Carmel.',[
     ('Start with your routine',[
      ('Is Carmel the right fit?','Start your Carmel search with the routine you want. If you picture coffee, galleries, and a walk through the Arts and Design District, spend time there before choosing a home. If privacy and a large yard matter more than being near that activity, look beyond the district and compare the actual lots.',''),
      ('Make the drive part of your search','Before you narrow a Carmel home search to one neighborhood, drive from it to work and your regular errands. Try your normal departure time and your evening return. A home near a favorite destination still needs to work for the rest of your week.','')]),
     ('The Arts and Design District and the Monon',[
      ('A condo near the district, or a house to renovate?','The city describes apartments and condos around the Arts and Design District. That can be a useful starting point if you want less outdoor upkeep. For any existing house you consider, weigh the floor plan and condition against the cost of changing them. If you prefer a new build, ask which finishes and site work are included rather than comparing the advertised starting price alone.','Source: '+CARMEL_SRC+'City of Carmel district guide</a><span class="source-date">Checked November 18, 2026</span>'),
      ('Walk the route you would use','The Monon Greenway runs through the district, according to the city. Walk the route from a home you are considering to the places you would use, including crossings and the trip back. Being in Carmel is different from being a comfortable walk from the district.','Source: '+CARMEL_SRC+'Carmel Arts and Design District guide</a><span class="source-date">Checked November 18, 2026</span>')]),
     ('Before you commit',[
      ('Confirm the school boundary','For a Carmel address, consult Carmel Clay Schools’ official site and confirm the applicable district and enrollment requirements before making a decision.','Source: <a href="https://www.ccs.k12.in.us/">Carmel Clay Schools</a><span class="source-date">Checked November 18, 2026</span>'),
      ('Budget for the house behind the finishes','An updated kitchen does not answer questions about an older home’s systems or prior alterations. I can help you separate the cosmetic wish list from work that needs an inspection or a contractor’s estimate. For a new home, we can review the specification alongside your move-in budget.','')])])
    area_page('westfield','Westfield','Living in Westfield, Indiana: Grand Park and new builds | Nick Giulioni', 'Compare new-build and existing homes in Westfield, Indiana, with Grand Park, your commute and the full project cost in mind.',
     'Compare new-build and existing homes with Grand Park, your commute and the full project cost in mind.',[
     ('Start with your week',[
      ('Start with how you would use Westfield','Put Westfield on your list if choosing a floor plan and comparing a builder’s proposal with an existing home appeals to you. If Grand Park is part of your week, include it in your location search. If you need a home on a firm near-term date, keep completed homes in the comparison instead of relying on a proposed completion date.',''),
      ('Test the routes that matter to you','Make separate trips from a possible Westfield address to work, errands, and any regular sports commitments. Drive them when you would normally go. If a house suits your budget but the trip does not suit your schedule, broaden the search before you compromise on the routine.','')]),
     ('New build or existing home',[
      ('Compare the finished cost, not just the base plan','For a new build, request a written breakdown of the lot, options, allowances, and work due after closing. For an existing home, price the immediate repairs and any changes you would want. Bring both totals to the same conversation so a lower starting number does not hide a larger project.',''),
      ('Plan for timing as well as repairs','With a builder, ask how selections, walkthroughs, and changes to the delivery schedule are handled. With an existing Westfield home, decide which projects must happen before you move in and which can wait. I help turn those questions into a practical list for the consult.','')]),
     ('Places to check first',[
      ('Grand Park, downtown, and time outside','Use <a href="https://grandpark.org/">Grand Park’s official site</a> to check the campus and event information for your visit. Then spend time downtown and use the <a href="https://www.westfieldin.gov/">City of Westfield’s parks and trail information</a> to plan a route you would use away from the campus. Treat these as separate stops when comparing locations.','<span class="source-date">Sources checked November 18, 2026</span>'),
      ('Verify enrollment for the property','Check the address and current enrollment process with Westfield Washington Schools; use the district’s own information rather than assuming an assignment from a listing.','Source: <a href="https://www.wws.k12.in.us/">Westfield Washington Schools</a><span class="source-date">Checked November 18, 2026</span>')])])
    area_page('fishers','Fishers','Living in Fishers, Indiana: Fishers District and downtown | Nick Giulioni', 'Compare Fishers District and downtown Fishers, then weigh home condition, travel routes and your everyday routine before buying.',
     'Compare Fishers District and downtown Fishers, then weigh home condition, travel routes and your everyday routine.',[
     ('Start with your routine',[
      ('Which version of your day are you buying?','If Fishers District is where you expect to spend an evening, visit it before touring nearby homes. If downtown Fishers and the Nickel Plate Trail draw you in, begin there instead. If walking from home is essential, skip properties until you have checked the actual route rather than treating a Fishers mailing address as a promise.',''),
      ('Try both the daily drive and the evening trip','Route your workday from each Fishers neighborhood on the shortlist, then try the trip to your preferred evening stop. Check where you would park or cross on foot. Keep those trips in your comparison even when two homes look similar on paper.','')]),
     ('The house itself',[
      ('Choose a layout for the way you live','In a Fishers home search, compare the spaces you will use every day: entry, kitchen, workspace, and outdoor area. For an existing house, ask whether a proposed change is a simple finish update or a layout project. For a new home, compare the selected plan and lot with the final specification, not only the model you toured.',''),
      ('Separate location from project scope','Liking the neighborhood does not settle what a house needs. We can list the work you see, the questions for an inspector, and the improvements you might defer. If the home is being built, ask how the warranty and unfinished items will be handled after handover.','')]),
     ('Downtown, the District, and the trail',[
      ('Downtown Fishers, Fishers District, and the trail','Visit downtown Fishers and Fishers District as distinct destinations. The city’s Nickel Plate Trail guide describes connections between neighborhoods, commercial areas, and the downtown Nickel Plate District. Use the route to plan a walk, then check how a particular home connects to it.','Source: <a href="https://fishersin.gov/nickel-plate-trail/">City of Fishers trail guide</a><span class="source-date">Checked November 18, 2026</span>'),
      ('Look up the assigned district','For a home in Fishers, start with Hamilton Southeastern’s official district site and verify the property’s district boundary and enrollment details directly.','Source: <a href="https://www.hseschools.org/">Hamilton Southeastern Schools</a><span class="source-date">Checked November 18, 2026</span>')])])


    area_page('north-indianapolis','North Indianapolis','Living in North Indianapolis: Meridian-Kessler, Broad Ripple and Nora | Nick Giulioni', 'Compare Meridian-Kessler, Broad Ripple and Nora on the north side of Indianapolis: older homes, the Monon Trail and everyday routes, with a local broker.',
     'Meridian-Kessler, Broad Ripple and Nora each have their own rhythm. Compare the streets, the older homes and the routes you would use before you narrow the list.',[
     ('Three neighborhoods, three routines',[
      ('Meridian-Kessler','Meridian-Kessler is known for tree-lined streets and older homes in a range of styles. If established architecture draws you, walk a few blocks instead of judging from listing photos, and note how each street connects to the shops and errands you would actually use.',''),
      ('Broad Ripple','Broad Ripple Village sits along the Monon Trail and the Central Canal, with shops and restaurants close together. Visit at the times you would really be there, including an evening and a weekend morning.',''),
  ('Nora','Nora, farther north around 86th Street, mixes established neighborhoods with nearby shopping. Drive the routes you would use most, at the hours you would use them, before you compare individual homes.','')]),
     ('An older home deserves a closer look',[
      ('Look behind the character','An older home may have been updated more than once. Ask what was changed, when, and whether the work was permitted, and keep the inspection focused on systems as well as finishes. I can help you sort cosmetic projects from work that needs a contractor’s estimate.',''),
      ('Plan for the house you will live with','Compare the floor plan, storage, parking and outdoor space with how you live now. A charming front porch does not settle whether the layout works, so we can list what you would change and roughly how large each project is before you make an offer.','')]),
     ('Before you commit',[
      ('Walk the trail and drive the routes','The Monon Trail runs north and south through this part of the city. If trail access matters, walk from the home to the nearest entrance, then drive your commute at the hours you would normally travel. Keep both trips in the comparison.',''),
      ('Confirm the school district for the address','Addresses on the north side can fall in different school districts, including Indianapolis Public Schools and the Metropolitan School District of Washington Township. Look up the specific address with the district before making a decision.','Sources:<span class="source-list"><a href="https://www.myips.org/">Indianapolis Public Schools</a><a href="https://www.msdwt.k12.in.us/">MSD of Washington Township</a></span><span class="source-date">Checked November 19, 2026</span>')])],
     h1='Living in North Indianapolis',county='Marion County')
    area_page('noblesville','Noblesville','Living in Noblesville, Indiana: downtown square and the White River | Nick Giulioni', 'Compare downtown Noblesville, the White River and newer and older homes, then weigh condition, routes and your routine with a local broker.',
     'Start with the courthouse square and the White River, then compare established streets near downtown with newer neighborhoods farther out.',[
     ('Start with your routine',[
      ('Downtown or farther out?','Downtown Noblesville centers on the historic courthouse square, with shops and restaurants a short walk apart. If that walkable core is part of your week, focus on streets close to it. If you want more room or a newer house, compare neighborhoods farther out and drive the trip back in.',''),
      ('Test the drives that matter','Noblesville sits north of Fishers and northeast of Carmel, so the drive to work and errands can shape the search. Try your routes at the hours you would normally travel, including any regular trips south, before you narrow the list.','')]),
     ('The house itself',[
      ('Older streets near downtown','Homes near the center of town are often older. Ask about the roof, wiring, plumbing and foundation, and plan an inspection that looks past the finishes. I can help you weigh which projects you would take on and which would change your offer.',''),
      ('Newer neighborhoods and new builds','For a newer home or a new build, compare the lot, the included features and the work that remains. Get the full cost in writing so a lower starting price does not hide a larger total.','')]),
     ('Before you commit',[
      ('Time along the White River','The White River runs through Noblesville near downtown. If time outside near the river matters to you, visit the parks and paths you would use and check how a particular home connects to them.',''),
      ('Confirm the school district','For a Noblesville address, check the district boundary and enrollment details directly with Noblesville Schools, and with the neighboring district if the address sits near a boundary.','Source: <a href="https://www.noblesvilleschools.org/">Noblesville Schools</a><span class="source-date">Checked November 19, 2026</span>')])])
    area_page('zionsville','Zionsville','Living in Zionsville, Indiana: the Village and brick Main Street | Nick Giulioni', 'Compare the Village and its brick Main Street, nearby parks and trails, and home choices around Zionsville, then weigh condition and routes with a local broker.',
     'Start in the Village along the brick Main Street, then compare the streets nearby with neighborhoods farther from town.',[
     ('Start with your routine',[
      ('The Village and Main Street','Zionsville’s Village centers on a brick Main Street lined with shops and restaurants. If walking into the Village matters to you, check the actual route from each home, including crossings and the trip back.','Source: <a href="https://www.zionsville-in.gov/">Town of Zionsville</a><span class="source-date">Checked November 19, 2026</span>'),
      ('Make the drive part of the search','Zionsville sits west of Carmel, northwest of Indianapolis. Drive from a possible address to work and your regular errands at the times you usually go, and keep those trips in the comparison.','')]),
     ('The house itself',[
      ('Established homes','For an older home, ask about the roof, mechanical systems and any additions, and plan an inspection that looks behind the finishes. We can separate cosmetic updates from work that needs a contractor’s estimate.',''),
      ('Lots, layouts and new construction','Lot sizes and layouts vary around Zionsville. Compare the spaces you would use every day and, for a new build, get the base plan, options and remaining work in writing before you compare totals.','')]),
     ('Before you commit',[
      ('Parks, trails and time outside','The town lists its parks and trails on its own site. Map the park or trail you would actually use and see how a particular home connects to it.','Source: <a href="https://www.zionsville-in.gov/">Town of Zionsville</a><span class="source-date">Checked November 19, 2026</span>'),
      ('Confirm the school district','For a Zionsville address, verify the district boundary and enrollment details directly with Zionsville Community Schools before making a decision.','Source: <a href="https://www.zcs.k12.in.us/">Zionsville Community Schools</a><span class="source-date">Checked November 19, 2026</span>')])],
     county='Boone County')
    page('/about/', 'About Nick Giulioni | Indiana real estate broker, T&H Realty Services', 'Meet Nick Giulioni, a Carmel-based Indiana broker with investing and renovation experience serving buyers and sellers.', 'An agent with an investor’s eye',section('Who I help','I help buyers and sellers in Carmel, Westfield, and Fishers think through their next move, including homes that need work and owners deciding whether to sell or keep a property.','lede-block')+about_photos()+section('From tech sales to Indiana homes','My background is in tech sales leadership. I have been investing in Central Indiana since 2017, with '+STAT+'. Years running renovation and new-build work taught me to ask what sits behind a finish and what a project might require. I live in Carmel and am newly licensed as an Indiana real estate broker.')+section('The podcast',POD+' <a href="https://indyreiwiththrealty.podbean.com/">Listen to the show</a>.')+section('My brokerage','I am affiliated with T&amp;H Realty Services.')+section('Careful numbers','I build and use Central Indiana market data through <a href="https://ballpark.build">Ballpark</a> to support careful numbers and better questions about a property. Estimates are a starting point for a conversation, not an appraisal.')+gallery()+cta(),card='about',kicker='About · Carmel, Indiana',art=picture('(max-width: 900px) 88px, 300px','portrait header-portrait'),variant='portrait')
    CONTACT_CARD=('<aside class="contact-aside" aria-label="Contact Nick directly"><div class="contact-id">'+picture('(max-width: 900px) 56px, 88px','portrait contact-portrait')+'<div><p class="contact-aside__name">Nick Giulioni</p><p class="contact-aside__role">Indiana real estate broker, <span class="nowrap">T&amp;H Realty Services</span></p></div></div><div class="contact-line"><a class="contact-call" href="'+S['phone_tel']+'">Call '+S['phone_display']+'</a><a class="contact-email" href="mailto:'+S['email']+'"><span class="contact-email__label">Email</span><span class="contact-email__addr">'+S['email']+'</span></a></div><p class="contact-aside__note">I respond personally, <span class="nowrap">usually the same day.</span></p></aside>')
    page('/contact/', 'Request a consult | Nick Giulioni', 'Request a buyer, seller or sell-versus-rent consult with Nick Giulioni in Central Indiana.', 'Request a consult', '<section class="contact-layout"><div class="contact-form-card">'+form('contact')+'</div></section>', kicker='Buyer, seller or sell-versus-rent', deck='Tell me what you are considering. We can work out the next step together.', art=CONTACT_CARD, variant='contact')
    page('/contact/thanks/', 'Thank you | Nick Giulioni', 'Your consult request has been received.', 'Thanks. I will reply personally, usually the same day.', '<section class="plain"><p><a href="/">Back home</a></p></section>',noindex=True,variant='band')
    page('/contact/error/', 'Request not sent | Nick Giulioni', 'Contact Nick directly if your consult request could not be sent.', 'That did not go through', '<section class="plain"><p>Please email <a href="mailto:'+S['email']+'">'+S['email']+'</a> or call <a href="'+S['phone_tel']+'">'+S['phone_display']+'</a>.</p><p><a href="/">Back home</a></p></section>',noindex=True,variant='band')
    page('/privacy/', 'Privacy | Nick Giulioni', 'How Nick Giulioni uses and protects information submitted through the consult form.', 'Privacy', section('Your request','Effective November 18, 2026. The form collects your name, email, phone, city or address, intent, message, and consent, along with the page source and receipt time. I use this information to reply to your consult request. The email notification is the stored record for now.')+section('Contact and consent','Your consent covers calls, emails, and texts from Nick about your request. Message and data rates may apply. Reply STOP to opt out of texts. Consent is only for responding to this request; it does not enroll you in a campaign. You can also contact me directly by email or phone.')+section('Processing and deletion','Vercel provides hosting for the site and processes submissions. Resend processes the email notification, and the Quo text service processes the text notification. Your data is not sold or shared for marketing. To request deletion, email <a href="mailto:'+S['email']+'">'+S['email']+'</a>.'),kicker='Privacy policy',variant='band')
    page('/podcast/', 'Podcast and earlier media | Nick Giulioni', 'The Indy Real Estate Investing Podcast and earlier real estate conversations with Nick Giulioni.', 'Podcast', '<section class="media-section"><h2>Earlier media</h2><div class="media-entries">'+MEDIA+'</div></section>'+cta(),card='podcast',kicker='On the mic',deck=POD,actions='<a class="btn btn-secondary" href="https://indyreiwiththrealty.podbean.com/">Listen to the show</a>',variant='band')
    page('/404.html', 'Page not found | Nick Giulioni', 'Find your way back to Nick Giulioni’s Central Indiana real estate site.', 'This page has moved', '<section class="plain"><p>Try <a href="/">home</a>, <a href="/sell/">selling</a>, <a href="/buy/">buying</a>, or <a href="/contact/">request a consult</a>.</p></section>',noindex=True,variant='band')

if __name__=='__main__':
    build()
