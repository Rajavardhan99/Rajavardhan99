#!/usr/bin/env python3
"""
Render the profile README's cards as animated SVGs into cards/.

Design: "Night Shift Atelier" - obsidian cards, bone-white type, one brass accent with
steel-blue and ember-rose as supporting colours. Instrument Serif for display, Geist for
text, Geist Mono for small caps-style labels.

Every card is a standalone SVG shown through <img>, so it only uses what GitHub allows
there: inline CSS animations, SMIL, and fonts embedded as data URIs. No JavaScript, no
external requests. Fonts are subset WOFFs in fonts/ (SIL OFL).

Live numbers come from data/contributions.json (written by fetch_contributions.py).
Everything else (credentials, projects, toolkit) is edited in the CONTENT block below.

    python scripts/render_readme_cards.py            # animated cards
    STATIC=1 python scripts/render_readme_cards.py   # every animation at its end state
"""
import base64
import datetime
import json
import math
import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data", "contributions.json")
OUT = os.path.join(ROOT, "cards")
FONTS = os.path.join(ROOT, "fonts")

# ============================ CONTENT (edit me) ================================
NAME_FIRST, NAME_LAST = "Rajavardhan", "Arigela"
EYEBROW = "B.TECH CSE  \u00b7  GENERATIVE AI & ML"
TAGLINE = [
    "Third-year engineering student building full-stack products",
    "and learning how machines learn. Java, React, Spring Boot, AWS.",
]
FOOTLINE = "NANDYAL, INDIA  \u00b7  KL UNIVERSITY  \u00b7  2024-2028"
COORDS = "15.48 N  78.48 E"

STACK = [
    "JAVA", "SPRING BOOT", "REACT", "JAVASCRIPT", "C", "PYTHON", "MYSQL", "POSTGRESQL",
    "AWS EC2", "AWS S3", "AWS VPC", "REST APIS", "GIT", "LINUX", "NLP", "NUMPY", "PANDAS", "POWER BI",
]

LINK_ART_LIVE = "https://art-gallery-new-seven.vercel.app/login"
LINK_ART_REPO = "https://github.com/MajhiMohit/fsd_16_project"
LINK_SMART_REPO = "https://github.com/SAIRAJA-2K7/fed-end-hackathon"
LINK_AWS = "https://cp.certmetrics.com/amazon/en/public/verify/credential/05e6154b61474683b5a5a20ee1f6306e"
LINK_LINKEDIN = "https://www.linkedin.com/in/arvardhan3/"

# label, accent, count-up value, final text, decimals, word, blurb
TILES = [
    ("BUILD", "brass", 25, "25-27%", 0, "faster",
     "Frontend and app-level tuning on the Art Gallery platform, measured at roughly 25 to 27 percent."),
    ("STUDY", "steel", 8.41, "8.41", 2, "/ 10",
     "GPA in B.Tech CSE (Generative AI & ML) at KL University, class of 2028."),
    ("CREDENTIALS", "rose", 6, "6", 0, "certificates",
     "AWS Certified Cloud Practitioner, plus five Palo Alto cybersecurity fundamentals certificates."),
]

PROJECTS = [
    dict(name="Art Gallery Management Platform", accent="brass", tag="LIVE DEMO", url=LINK_ART_LIVE,
         desc="Role-based gallery for admins, artists, visitors and curators, with OTP sign-in and REST APIs.",
         stack="React  \u00b7  Spring Boot  \u00b7  Node  \u00b7  SQL"),
    dict(name="Smart City Management", accent="steel", tag="GITHUB", url=LINK_SMART_REPO,
         desc="Responsive Admin and Citizen portals for utilities, emergency services and city dashboards.",
         stack="React  \u00b7  JavaScript  \u00b7  CSS"),
    dict(name="DayForge", accent="rose", tag="IN PROGRESS", url="https://github.com/Rajavardhan99",
         desc="A personal productivity app built around a calm daily workflow and a refined visual design.",
         stack="React  \u00b7  Vite  \u00b7  Tailwind"),
]

TOOLKIT = [
    ("LANGUAGES", ["Java", "C", "JavaScript", "Python (learning)"]),
    ("WEB", ["React", "HTML & CSS", "REST APIs", "Tailwind"]),
    ("BACKEND & DATA", ["Spring Boot", "Node.js", "MySQL", "PostgreSQL"]),
    ("CLOUD & TOOLS", ["AWS (EC2, S3, VPC)", "Git & Linux", "Power BI", "VS Code"]),
    ("EXPLORING", ["Generative AI & ML", "NLP", "NumPy & Pandas", "Cybersecurity"]),
]

# ================================ tokens ======================================
OBS = "#0c0d11"       # card background
OBS2 = "#13151b"      # raised surface
LINE = "#252832"      # hairlines
BONE = "#ece6d8"      # main text
BONE_SOFT = "#bdb8ab"
MUTED = "#8a8d98"
BRASS = "#d8a853"
BRASS_HI = "#f2cf8a"
STEEL = "#7aa2d6"
ROSE = "#d9695f"
ACCENT = {"brass": (BRASS, BRASS_HI), "steel": (STEEL, "#b4cdee"), "rose": (ROSE, "#f0a199")}
W = 880
GAP = 12
COL_W = W / 3 - 8     # three cards per row with two 12px gaps

SERIF = "'Instrument Serif', Georgia, serif"
SANS = "Geist, system-ui, -apple-system, sans-serif"
MONO = "'Geist Mono', ui-monospace, SFMono-Regular, Menlo, monospace"
MONO_ADV = 0.6  # Geist Mono advance, em

FONT_FILES = {
    "serif": ("Instrument Serif", "normal", 400, "serif-400.woff"),
    "serif-i": ("Instrument Serif", "italic", 400, "serif-italic.woff"),
    "sans": ("Geist", "normal", 400, "geist-400.woff"),
    "sans-b": ("Geist", "normal", 600, "geist-600.woff"),
    "mono": ("Geist Mono", "normal", 400, "geistmono-400.woff"),
}

BASE_CSS = """
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fade{from{opacity:0}to{opacity:1}}
@keyframes growx{from{transform:scaleX(0)}to{transform:scaleX(1)}}
@keyframes pop{0%{opacity:0;transform:scale(.2)}70%{opacity:1;transform:scale(1.2)}100%{opacity:1;transform:none}}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}
@keyframes nudge{0%,100%{transform:none}50%{transform:translate(3px,-3px)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes cardin{0%{opacity:0;transform:translateY(46px) scale(.94)}60%{opacity:1;transform:translateY(-2px)}80%{transform:translateY(1px)}100%{opacity:1;transform:none}}
@keyframes ringout{0%{opacity:.6;transform:scale(1)}100%{opacity:0;transform:scale(2.3)}}
@keyframes sheen{0%{transform:translateX(-300px) skewX(-18deg)}25%,100%{transform:translateX(460px) skewX(-18deg)}}
@keyframes marq{to{transform:translateX(var(--mq))}}
@keyframes sweep{0%{transform:translateX(-160px)}40%,100%{transform:translateX(900px)}}
.r{opacity:0;transform-box:fill-box;animation:rise .9s cubic-bezier(.2,.7,.2,1) both}
.f{opacity:0;animation:fade 1s ease-out both}
.gx{transform-box:fill-box;transform-origin:left center;transform:scaleX(0);animation:growx 1.1s cubic-bezier(.2,.7,.2,1) both}
.p{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s ease-out both}
.live{animation:pulse 1.8s ease-in-out infinite}
.nu{transform-box:fill-box;animation:nudge 2s ease-in-out infinite}
.ci{opacity:0;transform-box:fill-box;transform-origin:50% 80%;animation:cardin 1.15s cubic-bezier(.2,.8,.2,1) both}
.sp{transform-box:view-box;animation:spin linear infinite}
.rg{opacity:0;transform-box:fill-box;transform-origin:center;animation:ringout 2.6s ease-out infinite}
.sh{animation:sheen 6s ease-in-out infinite}
.mq{animation:marq 60s linear infinite}
.sw{animation:sweep 9s ease-in-out infinite}
.dr{stroke-dasharray:1;stroke-dashoffset:1;animation:draw 2.2s cubic-bezier(.4,.1,.2,1) both}
@media (prefers-reduced-motion: reduce){
  .r,.f,.gx,.p,.live,.nu,.ci,.sp,.mq{animation:none!important;opacity:1!important;transform:none!important}
  .dr{animation:none!important;stroke-dashoffset:0!important}
  .sh,.rg,.sw{display:none}
}
"""
STATIC_CSS = (".r,.f,.gx,.p,.live,.nu,.ci,.sp,.mq{animation:none!important;opacity:1!important;transform:none!important}"
              ".dr{animation:none!important;stroke-dashoffset:0!important}.sh,.rg,.sw{display:none}")


# ================================ helpers =====================================
def font_face(keys):
    out = []
    for k in keys:
        fam, style, weight, fn = FONT_FILES[k]
        b64 = base64.b64encode(open(os.path.join(FONTS, fn), "rb").read()).decode()
        out.append(f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{weight};"
                   f"src:url(data:font/woff;base64,{b64}) format('woff')}}")
    return "".join(out)


def svg(w, h, body, fonts, label, extra_css="", left=0, right=0, bottom=GAP):
    """Card of w x h drawn at x=left in a transparent canvas, padded so rows tile exactly."""
    if left:
        body = f'<g transform="translate({left:.3f} 0)">{body}</g>'
    w, h = w + left + right, h + bottom
    css = font_face(fonts) + BASE_CSS + extra_css
    if os.environ.get("STATIC"):
        css += STATIC_CSS
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title>'
            f"<style>{css}</style>{body}</svg>")


def write(name, content):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w") as f:
        f.write(content)
    print(f"wrote cards/{name} ({len(content) // 1024} KB)")


def d(s):
    return f'style="animation-delay:{s:.2f}s"'


def wrap(text, n):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > n:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line] if line else lines


def text_lines(x, y, lines, lh, attrs):
    return "".join(f'<text x="{x}" y="{y + i * lh}" {attrs}>{escape(l)}</text>' for i, l in enumerate(lines))


def card_bg(w, h, rx=16, fill=OBS):
    return (f'<rect width="{w:.3f}" height="{h}" rx="{rx}" fill="{fill}"/>'
            f'<rect x=".5" y=".5" width="{w - 1:.3f}" height="{h - 1}" rx="{rx - .5}" fill="none" stroke="{LINE}"/>')


def grid_defs(pid="grid", step=40, op=.035):
    return (f'<pattern id="{pid}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<path d="M{step} 0H0V{step}" fill="none" stroke="{BONE}" stroke-opacity="{op}"/></pattern>')


def count_up(val, final, dec, word, x, y, attrs, begin, dur=1.2, frames=20):
    """Number counts up with SMIL <set> frames (the only way to change text inside <img>)."""
    tail = f' <tspan font-style="italic" font-size="22" fill="{BONE_SOFT}">{escape(word)}</tspan>'
    suffix = "%" if final.endswith("%") else ""
    if os.environ.get("STATIC"):
        return f'<text x="{x}" y="{y}" {attrs}>{escape(final)}{tail}</text>'
    out = []
    for i in range(frames + 1):
        e = 1 - (1 - i / frames) ** 3
        txt = final if i == frames else f"{val * e:.{dec}f}{suffix}"
        on = begin + dur * i / frames
        off = "" if i == frames else f'<set attributeName="opacity" to="0" begin="{begin + dur * (i + 1) / frames:.3f}s"/>'
        out.append(f'<text x="{x}" y="{y}" {attrs} opacity="0">{escape(txt)}{tail}'
                   f'<set attributeName="opacity" to="1" begin="{on:.3f}s"/>{off}</text>')
    return "".join(out)


# ============================== 1 - hero ======================================
def hero():
    h = 440
    cx, cy = 690, 220
    spin = lambda dur, rev=False: (f'style="transform-origin:{cx}px {cy}px;animation-duration:{dur}s;'
                                   f'animation-direction:{"reverse" if rev else "normal"}"')
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{BONE}" stroke-opacity=".09"/>'
                    for r in (64, 104, 144, 180))

    def comet(r, dash, color, dur, rev=False, wdt=2):
        circ = 2 * math.pi * r
        ang = dash / r  # head of the dash, clockwise from 3 o'clock
        px, py = cx + r * math.cos(ang), cy + r * math.sin(ang)
        return (f'<g class="sp" {spin(dur, rev)}>'
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{wdt}" stroke-linecap="round" '
                f'stroke-dasharray="{dash} {circ - dash:.1f}" stroke-opacity=".85"/>'
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="4.5" fill="{color}"/>'
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="9" fill="{color}" fill-opacity=".18"/></g>')

    orbit = f"""
<line x1="{cx - 196}" y1="{cy}" x2="{cx + 196}" y2="{cy}" stroke="{BONE}" stroke-opacity=".07"/>
<line x1="{cx}" y1="{cy - 196}" x2="{cx}" y2="{cy + 196}" stroke="{BONE}" stroke-opacity=".07"/>
{rings}
<g class="sp" {spin(120)}><circle cx="{cx}" cy="{cy}" r="124" fill="none" stroke="{BRASS}" stroke-opacity=".55" stroke-dasharray="1 8.77"/></g>
<g class="sp" {spin(160, True)}><circle cx="{cx}" cy="{cy}" r="162" fill="none" stroke="{BONE}" stroke-opacity=".22" stroke-dasharray="2 9.4"/></g>
{comet(104, 150, BRASS_HI, 15)}
{comet(144, 120, STEEL, 24, True)}
{comet(180, 90, ROSE, 36)}
<circle class="rg" {d(1.2)} cx="{cx}" cy="{cy}" r="40" fill="none" stroke="{BRASS}" stroke-width="1.5"/>
<circle cx="{cx}" cy="{cy}" r="40" fill="{OBS2}" stroke="{BRASS}" stroke-opacity=".7"/>
<text x="{cx}" y="{cy + 13}" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="38" fill="{BRASS_HI}">RA</text>
"""
    body = f"""
<defs>
  {grid_defs()}
  <radialGradient id="glow" cx="{cx}" cy="{cy}" r="330" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="{BRASS}" stop-opacity=".20"/><stop offset="1" stop-color="{BRASS}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="440" y2="0">
    <stop offset="0" stop-color="{BRASS_HI}"/><stop offset=".36" stop-color="{BRASS}"/>
    <stop offset=".5" stop-color="#fff6dc"/><stop offset=".64" stop-color="{BRASS}"/><stop offset="1" stop-color="{BRASS_HI}"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-440 0;440 0;440 0" keyTimes="0;.4;1"
      dur="8s" begin="2s" repeatCount="indefinite"/>
  </linearGradient>
  <clipPath id="c"><rect width="{W}" height="{h}" rx="16"/></clipPath>
</defs>
{card_bg(W, h)}
<g clip-path="url(#c)">
  <rect width="{W}" height="{h}" fill="url(#grid)"/>
  <rect width="{W}" height="{h}" fill="url(#glow)"/>
  <g class="f" {d(.2)}>{orbit}</g>
</g>
<g class="f" {d(0)}>
  <rect class="live" x="44" y="53" width="8" height="8" rx="2" fill="{BRASS}"/>
  <text x="62" y="61" font-family="{MONO}" font-size="12" letter-spacing="1.4" fill="{MUTED}">{escape(EYEBROW)}</text>
</g>
<text class="r" {d(.15)} x="40" y="178" font-family="{SERIF}" font-size="100" letter-spacing="-2" fill="{BONE}">{escape(NAME_FIRST)}</text>
<text class="r" {d(.35)} x="40" y="272" font-family="{SERIF}" font-style="italic" font-size="100" letter-spacing="-2" fill="url(#shine)">{escape(NAME_LAST)}</text>
<g class="r" {d(.6)}>
  {text_lines(44, 322, TAGLINE, 26, f'font-family="{SANS}" font-size="16" fill="{BONE_SOFT}"')}
</g>
<rect class="gx" {d(.9)} x="44" y="372" width="400" height="1" fill="{LINE}"/>
<rect class="gx" {d(.9)} x="44" y="372" width="64" height="1" fill="{BRASS}"/>
<g class="f" {d(1.1)}>
  <text x="44" y="402" font-family="{MONO}" font-size="11.5" letter-spacing="1.2" fill="{MUTED}">{escape(FOOTLINE)}</text>
  <text x="{W - 36}" y="410" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="1.2" fill="{MUTED}" fill-opacity=".8">{escape(COORDS)}</text>
</g>
"""
    write("hero.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                          f"{NAME_FIRST} {NAME_LAST}. B.Tech CSE student, Generative AI and ML, KL University. Full-stack developer."))


# ============================ 2 - stack ticker ================================
def ticker():
    h, size, ls = 56, 12, 1.6
    pad = 26
    items, x = [], 0
    for s in STACK:
        wd = len(s) * (MONO_ADV * size + ls)
        items.append((x, s))
        x += wd + pad * 2 + 8
    strip = x

    def one(offset):
        g = []
        for ix, s in items:
            g.append(f'<text x="{offset + ix:.1f}" y="33" font-family="{MONO}" font-size="{size}" letter-spacing="{ls}" fill="{BONE_SOFT}">{escape(s)}</text>')
            g.append(f'<rect x="{offset + ix + len(s) * (MONO_ADV * size + ls) + pad - 3:.1f}" y="25" width="6" height="6" fill="{BRASS}" transform="rotate(45 {offset + ix + len(s) * (MONO_ADV * size + ls) + pad:.1f} 28)"/>')
        return "".join(g)

    dur = max(30, strip / 38)
    body = f"""
<defs>
  <clipPath id="t"><rect width="{W}" height="{h}" rx="14"/></clipPath>
  <linearGradient id="el" x1="0" x2="1"><stop offset="0" stop-color="{OBS2}"/><stop offset="1" stop-color="{OBS2}" stop-opacity="0"/></linearGradient>
  <linearGradient id="er" x1="1" x2="0"><stop offset="0" stop-color="{OBS2}"/><stop offset="1" stop-color="{OBS2}" stop-opacity="0"/></linearGradient>
</defs>
{card_bg(W, h, 14, OBS2)}
<g clip-path="url(#t)">
  <g class="mq" style="--mq:-{strip:.1f}px;animation-duration:{dur:.0f}s">{one(30)}{one(30 + strip)}</g>
  <rect width="90" height="{h}" fill="url(#el)"/><rect x="{W - 90}" width="90" height="{h}" fill="url(#er)"/>
</g>
"""
    write("stack.svg", svg(W, h, body, ["mono"], "Tech stack: " + ", ".join(s.title() for s in STACK)))


# ============================ 3 - credential tiles ============================
def tile(i, spec, href_label):
    label, acc, val, final, dec, word, blurb = spec
    c, hi = ACCENT[acc]
    delay = 1.7 + i * 0.22
    h = 206
    lines = wrap(blurb, 36)
    blurb_svg = "".join(
        f'<text class="r" {d(delay + .8 + k * .1)} x="24" y="{150 + k * 19}" font-family="{SANS}" font-size="13" fill="{BONE_SOFT}">{escape(l)}</text>'
        for k, l in enumerate(lines))
    body = f"""
<defs>
  <clipPath id="k"><rect width="{COL_W:.3f}" height="{h}" rx="16"/></clipPath>
  <radialGradient id="g" cx="1" cy="1" r=".85"><stop offset="0" stop-color="{c}" stop-opacity=".30"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>
  <linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".10"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
</defs>
<g class="ci" {d(delay)}>
  {card_bg(COL_W, h)}
  <g clip-path="url(#k)">
    <rect width="{COL_W:.3f}" height="{h}" fill="url(#g)"/>
    <rect class="sh" style="animation-delay:{delay + 2 + i:.1f}s" x="0" y="-20" width="110" height="{h + 40}" fill="url(#gl)" transform="translate(-300 0)"/>
  </g>
  <rect class="gx" {d(delay + .35)} x="24" y="52" width="36" height="1.5" fill="{c}"/>
  <text x="24" y="40" font-family="{MONO}" font-size="11.5" letter-spacing="2" fill="{c}">{label}</text>
  <text class="nu" x="{COL_W - 38:.1f}" y="40" font-family="{MONO}" font-size="14" fill="{c}">&#8599;</text>
  {count_up(val, final, dec, word, 22, 118, f'font-family="{SERIF}" font-size="64" fill="{hi}"', delay + .4)}
  {blurb_svg}
</g>
"""
    return svg(COL_W, h, body, ["serif", "serif-i", "sans", "mono"], f"{label}: {final} {word}. {blurb}",
               left=4 * i, right=8 - 4 * i)


def tiles():
    for i, (spec, name) in enumerate(zip(TILES, ("build", "study", "creds"))):
        write(f"tile-{name}.svg", tile(i, spec, name))


# ======================== 4 - section header strips ===========================
def section(slug, title, italic, tag, delay):
    h = 62
    title_w = 13.2 * len(f"{title} {italic}")        # Instrument Serif 32px, ~0.41em per glyph
    tag_w = len(tag) * (MONO_ADV * 11.5 + 1.6)
    x_a, x_b = 28 + title_w + 22, W - 28 - tag_w - 22
    body = f"""
{card_bg(W, h, 14)}
<text class="r" {d(delay)} x="28" y="41" font-family="{SERIF}" font-size="32" fill="{BONE}">{escape(title)} <tspan font-style="italic" fill="{BRASS_HI}">{escape(italic)}</tspan></text>
<rect class="gx" {d(delay + .2)} x="{x_a:.1f}" y="31" width="{x_b - x_a:.1f}" height="1" fill="{LINE}"/>
<rect class="gx" {d(delay + .2)} x="{x_a:.1f}" y="30.5" width="28" height="2" fill="{BRASS}"/>
<text class="f" {d(delay + .3)} x="{W - 28}" y="36" text-anchor="end" font-family="{MONO}" font-size="11.5" letter-spacing="1.6" fill="{MUTED}">{escape(tag)}</text>
"""
    write(f"section-{slug}.svg", svg(W, h, body, ["serif", "serif-i", "mono"], f"{title} {italic}"))


# =========================== 5 - project cards ================================
def project(i, p):
    c, hi = ACCENT[p["accent"]]
    delay = .3 + i * .15
    title_lines = wrap(p["name"], 20)
    desc = wrap(p["desc"], 37)
    n_t = max(len(wrap(q["name"], 20)) for q in PROJECTS)
    n_d = max(len(wrap(q["desc"], 37)) for q in PROJECTS)
    desc_y = 86 + 30 * (n_t - 1) + 34                       # descriptions align across cards
    h = desc_y + 19 * (n_d - 1) + 26 + 52                    # same height for every card
    body = f"""
<defs>
  <clipPath id="k"><rect width="{COL_W:.3f}" height="{h}" rx="16"/></clipPath>
  <radialGradient id="g" cx="0" cy="0" r=".9"><stop offset="0" stop-color="{c}" stop-opacity=".22"/><stop offset="1" stop-color="{c}" stop-opacity="0"/></radialGradient>
</defs>
<g class="r" {d(delay)}>
  {card_bg(COL_W, h)}
  <g clip-path="url(#k)"><rect width="{COL_W:.3f}" height="{h}" fill="url(#g)"/></g>
  <text x="24" y="40" font-family="{MONO}" font-size="11.5" letter-spacing="2" fill="{c}">0{i + 1}</text>
  <text x="{COL_W - 24:.1f}" y="40" text-anchor="end" font-family="{MONO}" font-size="10.5" letter-spacing="1.4" fill="{MUTED}">{escape(p["tag"])} <tspan fill="{c}">&#8599;</tspan></text>
  {text_lines(24, 86, title_lines, 30, f'font-family="{SERIF}" font-size="28" fill="{BONE}"')}
  {text_lines(24, desc_y, desc, 19, f'font-family="{SANS}" font-size="13" fill="{BONE_SOFT}"')}
  <rect x="24" y="{h - 52}" width="{COL_W - 48:.1f}" height="1" fill="{LINE}"/>
  <rect x="24" y="{h - 52}" width="28" height="1" fill="{c}"/>
  <text x="24" y="{h - 26}" font-family="{MONO}" font-size="11" letter-spacing=".6" fill="{MUTED}">{escape(p["stack"])}</text>
</g>
"""
    write(f"project-{i + 1}.svg", svg(COL_W, h, body, ["serif", "sans", "mono"], f'{p["name"]}: {p["desc"]}',
                                      left=4 * i, right=8 - 4 * i))


# ============================== 6 - toolkit ===================================
def toolkit():
    h = 232
    cw = (W - 56) / len(TOOLKIT)
    cols = []
    for i, (title, items) in enumerate(TOOLKIT):
        x = 28 + i * cw
        delay = .3 + i * .12
        its = "".join(
            f'<rect x="{x:.1f}" y="{118 + k * 26 - 4}" width="4" height="4" fill="{BRASS}" transform="rotate(45 {x + 2:.1f} {118 + k * 26 - 2})"/>'
            f'<text x="{x + 14:.1f}" y="{118 + k * 26}" font-family="{SANS}" font-size="13.5" fill="{BONE_SOFT}">{escape(t)}</text>'
            for k, t in enumerate(items))
        div = f'<rect x="{x - 14:.1f}" y="76" width="1" height="124" fill="{LINE}"/>' if i else ""
        cols.append(f'<g class="r" {d(delay)}>{div}'
                    f'<text x="{x:.1f}" y="88" font-family="{MONO}" font-size="11" letter-spacing="1.6" fill="{BRASS}">{escape(title)}</text>{its}</g>')
    body = f"""
<defs>{grid_defs("g2", 32, .03)}<clipPath id="c"><rect width="{W}" height="{h}" rx="16"/></clipPath></defs>
{card_bg(W, h)}
<g clip-path="url(#c)"><rect width="{W}" height="{h}" fill="url(#g2)"/></g>
<text class="r" {d(.1)} x="28" y="48" font-family="{SERIF}" font-size="32" fill="{BONE}">The <tspan font-style="italic" fill="{BRASS_HI}">toolkit</tspan></text>
<text class="f" {d(.2)} x="{W - 28}" y="42" text-anchor="end" font-family="{MONO}" font-size="11.5" letter-spacing="1.6" fill="{MUTED}">WHAT I REACH FOR</text>
{''.join(cols)}
"""
    write("toolkit.svg", svg(W, h, body, ["serif", "serif-i", "sans", "mono"],
                             "Toolkit: " + "; ".join(f"{t}: {', '.join(i)}" for t, i in TOOLKIT)))


# ============================ 7 - contribution graph ==========================
LEVELS = ["#191b22", "#3b2f19", "#6b5428", "#a47f3b", BRASS, "#f6d791"]


def level_for(c):
    return 0 if c == 0 else 1 if c <= 2 else 2 if c <= 5 else 3 if c <= 9 else 4 if c <= 19 else 5


def heatmap(data):
    days = data["days"]
    first = datetime.date.fromisoformat(days[0]["date"])
    lead = (first.weekday() + 1) % 7
    cell, step, gx, gy = 11.5, 14.8, 44, 112
    cells, months, seen = [], [], set()
    for i, day in enumerate(days):
        col, row = divmod(i + lead, 7)
        date = datetime.date.fromisoformat(day["date"])
        if date.day <= 7 and (date.year, date.month) not in seen and row == 0:
            seen.add((date.year, date.month))
            months.append((col, date.strftime("%b")))
        c = day["count"]
        delay = .5 + col * .022 + row * .03
        cells.append(f'<rect class="p" style="animation-delay:{delay:.2f}s" x="{gx + col * step:.1f}" y="{gy + row * step:.1f}" '
                     f'width="{cell}" height="{cell}" rx="2.5" fill="{LEVELS[level_for(c)]}">'
                     f'<title>{day["date"]}: {c} contribution{"s" if c != 1 else ""}</title></rect>')
    ncols = (len(days) + lead + 6) // 7
    right = gx + ncols * step - 3
    labels = "".join(f'<text x="{gx + col * step:.1f}" y="{gy + 7 * step + 18:.1f}" font-family="{MONO}" font-size="10.5" fill="{MUTED}">{m}</text>'
                     for col, m in months if col < ncols - 1)
    lx = right - len(LEVELS) * 14 - 30
    legend = "".join(f'<rect x="{lx + k * 14}" y="64" width="10" height="10" rx="2.5" fill="{c}"/>' for k, c in enumerate(LEVELS))
    h = int(gy + 7 * step + 40)
    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{h}" rx="16"/></clipPath>
  <linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="{BRASS_HI}" stop-opacity="0"/><stop offset=".5" stop-color="{BRASS_HI}" stop-opacity=".16"/><stop offset="1" stop-color="{BRASS_HI}" stop-opacity="0"/></linearGradient>
</defs>
{card_bg(W, h)}
<text class="r" {d(.2)} x="42" y="62" font-family="{SERIF}" font-size="32" fill="{BONE}">Every day, <tspan font-style="italic" fill="{BRASS_HI}">in brass</tspan></text>
<text class="f" {d(.3)} x="{right:.1f}" y="46" text-anchor="end" font-family="{MONO}" font-size="11.5" letter-spacing="1.4" fill="{MUTED}">{data["total_contributions"]:,} CONTRIBUTIONS  \u00b7  REFRESHED DAILY</text>
{''.join(cells)}
<g clip-path="url(#c)"><rect class="sw" style="animation-delay:3s" x="0" y="{gy - 8}" width="160" height="{7 * step + 14:.0f}" fill="url(#sw)" transform="translate(-160 0)"/></g>
<g class="f" {d(1.8)}>{labels}
<text x="{lx - 8}" y="73" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="{MUTED}">less</text>{legend}
<text x="{lx + len(LEVELS) * 14 + 2}" y="73" font-family="{MONO}" font-size="10.5" fill="{MUTED}">more</text></g>
"""
    write("heatmap.svg", svg(W, h, body, ["serif", "serif-i", "mono"],
                             f'Contribution graph: {data["total_contributions"]:,} contributions in the last year'))


# ============================ 8 - monthly line chart ==========================
def smooth(pts):
    """Catmull-Rom to cubic Bezier, control points clamped so the curve never dips below the data."""
    if len(pts) < 2:
        return ""
    path = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, len(pts) - 1)]
        lo, hi_ = min(p1[1], p2[1]), max(p1[1], p2[1])
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, min(max(p1[1] + (p2[1] - p0[1]) / 6, lo), hi_))
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, min(max(p2[1] - (p3[1] - p1[1]) / 6, lo), hi_))
        path += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return path


def activity(data):
    h = 440
    monthly = data["monthly"][-12:]
    peak = max(monthly, key=lambda m: m["total"])
    top = max(peak["total"], 1)
    x0, x1, base, ctop = 68, 812, 290, 152
    n = len(monthly)
    xs = [x0 + i * (x1 - x0) / max(n - 1, 1) for i in range(n)]
    pts = [(xs[i], base - m["total"] / top * (base - ctop)) for i, m in enumerate(monthly)]
    line = smooth(pts)
    area = f"{line} L{pts[-1][0]:.1f} {base} L{pts[0][0]:.1f} {base} Z"
    grid = "".join(
        f'<rect x="{x0 - 8}" y="{base - k * (base - ctop) / 2:.1f}" width="{x1 - x0 + 16}" height="1" fill="{LINE}"/>'
        f'<text x="{x0 - 16}" y="{base - k * (base - ctop) / 2 + 4:.1f}" text-anchor="end" font-family="{MONO}" font-size="10" fill="{MUTED}">{int(top * k / 2)}</text>'
        for k in (0, 1, 2))
    dots, lbls = [], []
    for i, m in enumerate(monthly):
        mon = datetime.date.fromisoformat(m["month"] + "-01").strftime("%b")
        is_peak = m is peak
        lbls.append(f'<text class="f" {d(1.2 + i * .08)} x="{xs[i]:.1f}" y="{base + 22}" text-anchor="middle" font-family="{MONO}" font-size="10.5" fill="{BRASS_HI if is_peak else MUTED}">{mon}</text>')
        dots.append(f'<circle class="p" style="animation-delay:{1.5 + i * .12:.2f}s" cx="{pts[i][0]:.1f}" cy="{pts[i][1]:.1f}" r="{5 if is_peak else 3.2}" '
                    f'fill="{BRASS_HI if is_peak else OBS}" stroke="{BRASS}" stroke-width="1.6"><title>{mon}: {m["total"]:,}</title></circle>')
        if is_peak:
            dots.append(f'<text class="p" {d(3)} x="{pts[i][0]:.1f}" y="{pts[i][1] - 16:.1f}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{BRASS_HI}">{m["total"]:,}</text>')
    cs, ls = data["current_streak"]["length"], data["longest_streak"]["length"]
    stats = [
        (f"{cs}", "days", "current streak"),
        (f"{ls}", "days", "longest streak"),
        (f'{data["active_days"]}', f'/ {len(data["days"])}', "days with a commit"),
        (f'{data["best_day"]["count"]}', "", "on the busiest day"),
    ]
    sx = 44
    side = []
    for i, (big, small, cap) in enumerate(stats):
        x = sx + i * 206
        sm = f' <tspan font-style="italic" font-size="18" fill="{MUTED}">{escape(small)}</tspan>' if small else ""
        side.append(f'<g class="r" {d(2.4 + i * .12)}>'
                    f'<text x="{x}" y="{h - 52}" font-family="{SERIF}" font-size="40" fill="{BONE}">{escape(big)}{sm}</text>'
                    f'<text x="{x}" y="{h - 28}" font-family="{MONO}" font-size="10.5" letter-spacing="1.2" fill="{MUTED}">{escape(cap.upper())}</text></g>')
        if i:
            side.append(f'<rect x="{x - 22}" y="{h - 96}" width="1" height="68" fill="{LINE}"/>')
    body = f"""
<defs>
  <clipPath id="c"><rect width="{W}" height="{h}" rx="16"/></clipPath>
  <linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BRASS}" stop-opacity=".34"/><stop offset="1" stop-color="{BRASS}" stop-opacity="0"/></linearGradient>
  <linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="{BRASS}"/><stop offset="1" stop-color="{BRASS_HI}"/></linearGradient>
</defs>
{card_bg(W, h)}
<text class="f" {d(.1)} x="44" y="52" font-family="{MONO}" font-size="11.5" letter-spacing="1.6" fill="{MUTED}">ACTIVITY  \u00b7  LAST 12 MONTHS</text>
<text class="r" {d(.2)} x="42" y="96" font-family="{SERIF}" font-size="44" fill="{BRASS_HI}">{data["total_contributions"]:,} <tspan font-style="italic" fill="{BONE}">contributions</tspan></text>
{grid}
<path class="f" {d(1.6)} d="{area}" fill="url(#ar)"/>
<path class="dr" {d(1.0)} pathLength="1" d="{line}" fill="none" stroke="url(#ln)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
{''.join(dots)}{''.join(lbls)}
<rect x="44" y="{h - 108}" width="{W - 88}" height="1" fill="{LINE}"/>
{''.join(side)}
"""
    write("activity.svg", svg(W, h, body, ["serif", "serif-i", "mono"],
                              f'{data["total_contributions"]:,} contributions in the last year, {cs}-day current streak'))


# ============================== 9 - footer ====================================
def footer():
    h = 118
    body = f"""
<defs>{grid_defs("g3", 32, .03)}<clipPath id="c"><rect width="{W}" height="{h}" rx="16"/></clipPath></defs>
{card_bg(W, h)}
<g clip-path="url(#c)"><rect width="{W}" height="{h}" fill="url(#g3)"/></g>
<rect class="gx" style="transform-origin:center;animation-delay:.1s" x="{W / 2 - 60}" y="30" width="120" height="1.5" fill="{BRASS}"/>
<text class="r" {d(.3)} x="{W / 2}" y="70" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-size="30" fill="{BONE}">Thanks for stopping by.</text>
<text class="f" {d(.6)} x="{W / 2}" y="98" text-anchor="middle" font-family="{MONO}" font-size="11" letter-spacing="2.4" fill="{MUTED}">ALWAYS BUILDING  \u00b7  ALWAYS LEARNING</text>
"""
    write("footer.svg", svg(W, h, body, ["serif-i", "mono"], "Thanks for stopping by. Always building, always learning.", bottom=0))


if __name__ == "__main__":
    data = json.load(open(DATA))
    if data.get("demo"):
        print("NOTE: data/contributions.json is demo data. The GitHub Action replaces it with your real calendar.")
    hero()
    ticker()
    tiles()
    section("work", "Selected", "work", "01  \u00b7  PROJECTS", .1)
    for i, p in enumerate(PROJECTS):
        project(i, p)
    toolkit()
    section("open", "In the", "open", "02  \u00b7  ACTIVITY", .1)
    heatmap(data)
    activity(data)
    footer()
