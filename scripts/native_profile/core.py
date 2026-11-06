"""Render the GitHub-native edition of Umi's build lab. All claims use public data."""
from pathlib import Path
from datetime import date
from html import escape
import base64
import hashlib
import json
import re
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'assets'
BG, PANEL, INK, MUTED, LINE = '#f0ebe1', '#f0ebe1', '#0c1927', '#394638', '#0c1927'
MINT, GOLD, BLUE = '#aaf3ab', '#fdbc44', '#8cbdd1'


def text(x, y, content, size=18, color=INK, weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(str(content))}</text>'


def rect(x, y, w, h, fill=PANEL, radius=12, stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"' + (f' stroke="{stroke}"' if stroke else '') + '/>'


def shell(w, h, body, title):
    font = base64.b64encode((ASSETS / 'sora-latin.woff2').read_bytes()).decode()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title, quote=True)}"><title>{escape(title)}</title><style>@font-face{{font-family:Sora;src:url(data:font/woff2;base64,{font});font-weight:400 800}}text{{font-family:Sora,Arial,sans-serif}}.nyan-still{{display:none}}.art{{animation:bob 5s ease-in-out infinite}}@keyframes bob{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-3px)}}}}.pulse{{animation:pulse 3s ease-in-out infinite}}.flow{{stroke-dasharray:6 12;animation:flow 3s linear infinite}}@keyframes pulse{{0%,100%{{opacity:.4}}50%{{opacity:1}}}}@keyframes flow{{to{{stroke-dashoffset:-72}}}}@media(prefers-reduced-motion:reduce){{.pulse,.flow,.art{{animation:none}}.moving,.nyan-live{{display:none}}.nyan-still{{display:inline}}}}</style>{rect(0,0,w,h,BG)}{body}</svg>'''


def pill(x, y, value, color=MINT, width=None):
    w = width or len(value) * 8 + 26
    return rect(x, y, w, 28, '#26363e', 5) + text(x + 12, y + 19, value, 12, color, 500)


def write(name, w, h, body, title):
    (ASSETS / name).write_text(shell(w, h, body, title), encoding='utf-8')


def commit_orbit(days, start, x0, y0, dx, dy, width, cell=12, height=11):
    """Decorative sweep, clipped strictly to the real calendar's active cells."""
    marks = []
    for day in days:
        if day['count'] <= 0:
            continue
        column, row = divmod((date.fromisoformat(day['date']) - start).days, 7)
        marks.append(rect(round(x0 + column * dx, 2), round(y0 + row * dy, 2), cell, height, '#fff', 2))
    grid_h = dy * 6 + height
    return f'''<defs><mask id="orbit-active" maskUnits="userSpaceOnUse" maskContentUnits="userSpaceOnUse" x="{x0}" y="{y0}" width="{width}" height="{grid_h}">{''.join(marks)}</mask><linearGradient id="orbit-light"><stop offset="0" stop-color="{MINT}" stop-opacity="0"/><stop offset=".72" stop-color="{MINT}" stop-opacity=".16"/><stop offset="1" stop-color="{GOLD}" stop-opacity=".42"/></linearGradient></defs><style>@media(prefers-reduced-motion:reduce){{.orbit-motion{{display:none}}}}</style><g class="orbit-motion" aria-hidden="true" pointer-events="none"><g mask="url(#orbit-active)"><rect x="-125" y="{y0}" width="145" height="{grid_h}" fill="url(#orbit-light)"><animateTransform attributeName="transform" type="translate" values="{x0 - 35} 0;{x0 + width + 130} 0" dur="9s" begin="-6.4s" repeatCount="indefinite"/></rect></g><g transform="translate({x0} {y0 - 8})"><animateTransform attributeName="transform" type="translate" values="{x0 - 35} {y0 - 8};{x0 + width + 130} {y0 - 8}" dur="9s" begin="-6.4s" repeatCount="indefinite"/><path d="M-1-4h2v3h3v2H1v3h-2V1h-3v-2h3z" fill="{GOLD}"/>{''.join(rect(-10-i*10, -1, max(2, 6-i*.6), 2, MINT, 0)[:-2] + f' opacity="{.6-i*.07}"/>' for i in range(6))}</g></g>'''


def image_asset(name, x, y, w, h, moving=False):
    if moving and name.startswith('c1-') and name.endswith('-art.png'):
        # Inline the complete rig, not an SVG-as-image indirection: GitHub keeps
        # its native SMIL motion and the inner reduced-motion static fallback.
        motion = ASSETS / name.replace('-art.png', '-motion.svg')
        tree = ET.parse(motion).getroot()
        tree.attrib.update(x=str(x), y=str(y), width=str(w), height=str(h), preserveAspectRatio='xMidYMid meet')
        ET.register_namespace('', 'http://www.w3.org/2000/svg')
        ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
        return ET.tostring(tree, encoding='unicode')
    payload = base64.b64encode((ASSETS / name).read_bytes()).decode()
    mime = 'image/gif' if name.endswith('.gif') else 'image/png'
    return f'<image class="{("art" if moving else "")}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:{mime};base64,{payload}"/>'


def arrow(x, y, ink=INK, size=26):
    return f'<path d="M{x} {y}h{size}m-{size * .4}-{size * .4} {size * .4} {size * .4}-{size * .4} {size * .4}" fill="none" stroke="{ink}" stroke-width="2.5"/>'



def pixel(name, x, y, w, h):
    """Original animated pixels with a static reduced-motion fallback."""
    live = image_asset(name + '.gif', x, y, w, h).replace('class=""', 'class="nyan-live"')
    still = image_asset(name + '-still.png', x, y, w, h).replace('class=""', 'class="nyan-still"')
    return live + still
