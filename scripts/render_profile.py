"""Render the GitHub-native edition of Umi's build lab. All claims use public data."""
from pathlib import Path
from datetime import date
from html import escape
import base64
import hashlib
import json
import re
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
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


def render(data):
    def pixel(name, x, y, w, h):
        live = image_asset(name + '.gif', x, y, w, h).replace('class=""', 'class="nyan-live"')
        still = image_asset(name + '-still.png', x, y, w, h).replace('class=""', 'class="nyan-still"')
        return live + still

    for mobile in (False, True):
        w, h = (500, 224) if mobile else (1000, 178)
        hero = text(20, 57, 'umi', 53, INK, 800) + text(119, 57, '.', 53, '#68ba60', 800)
        hero += pixel('nyan-cat', 155, 5, 205, 81.5)
        hero += f'<path d="M18 83H{w-18}" stroke="{INK}" stroke-width="2"/>'
        if mobile:
            hero += text(20, 143, 'Things I', 53, INK, 800) + text(20, 201, 'build.', 53, INK, 800)
            hero += pixel('pixel-planet', 348, 108, 125, 100)
        else:
            hero += text(23, 150, 'Things I build', 67, INK, 800) + text(522, 150, '.', 67, '#68ba60', 800)
            hero += pixel('pixel-planet', 860, 87, 110, 84)
            hero += text(800, 52, '@TDUmii', 18, INK, 600)
        write('profile-hero' + ('-mobile' if mobile else '') + '.svg', w, h, hero, 'Umi. Things I build. Original Nyan Cat and pixel planet.')

    # Separate linked poster images preserve native GitHub links. A dedicated
    # compact viewBox keeps both top cells legible on small GitHub screens.
    for mobile in (False, True):
        w, h = (250, 330) if mobile else (500, 340)
        for slug, lines, descriptions, art in [
            ('bridge', ['Umi', 'Bridge'], ['ChatGPT meets', 'Windows.'], 'c1-bridge-art.png'),
            ('quietshare', ['Quiet', 'Share'], ['Presentations, notes,', 'optional offline', 'transcription.'], 'c1-quiet-art.png'),
        ]:
            if slug == 'bridge':
                shape = f'<path d="M0 0H{w-30}v18h20v38h10V{h}H0Z" fill="{MINT}"/>'
            else:
                shape = f'<path d="M1 15h34L44 1H{w-1}V{h-1}H1Z" fill="{BG}" stroke="{INK}" stroke-width="2"/>'
            x, title_size = (14, 43) if mobile else (23, 76)
            y, leading = (58, 46) if mobile else (88, 78)
            for i, line in enumerate(lines):
                shape += text(x, y+i*leading, line, title_size, INK, 800)
            dy, ds, dl = (141, 20, 25) if mobile else (206, 21, 27)
            for i, line in enumerate(descriptions):
                shape += text(x, dy+i*dl, line, ds, INK, 500)
            shape += arrow(x+2, 211 if mobile else 286)
            ax, ay, aw, ah = (55, 214, 190, 114) if mobile else (196, 178, 302, 160)
            if not mobile and slug == 'quietshare':
                ax, aw = 258, 240
            shape += image_asset(art, ax, ay, aw, ah, True)
            write('project-row-' + slug + ('-mobile' if mobile else '') + '.svg', w, h, shape, ('UmiBridge. ChatGPT meets Windows.' if slug == 'bridge' else 'QuietShare. Presentations, notes, optional offline transcription.') + ' Open repository.')

        aw, ah = (500, 310) if mobile else (1000, 200)
        studio = rect(0, 0, aw, ah, INK, 0)
        size, line_h, first_y = (38, 40, 48) if mobile else (49, 50, 55)
        for i, line in enumerate(['Background', 'Automation', 'Studio']):
            studio += text(22, first_y + i*line_h, line, size, BG, 800)
        studio += text(22 if mobile else 448, 175 if mobile else 82, 'Record. Edit. Replay.', 20 if mobile else 24, BG, 500)
        studio += arrow(24 if mobile else 450, 212 if mobile else 118, BG)
        studio += f'<path d="M{100 if mobile else 390} {ah}l20-24h{aw-120 if mobile else aw-410}v24z" fill="{GOLD}"/>'
        studio += image_asset('c1-automation-art.png', 260 if mobile else 700, 110 if mobile else 10, 237 if mobile else 295, 196 if mobile else 184, True)
        write('project-row-automation' + ('-mobile' if mobile else '') + '.svg', aw, ah, studio, 'Background Automation Studio. Record, edit and replay Windows workflows. Open repository.')

    days = data['contributions']
    start = date.fromisoformat(days[0]['date'])
    cells, months = '', set()
    palette = ['#dedfd2', '#8cab7a', '#5e874f', '#355f35', '#153e27']
    for day in days:
        current = date.fromisoformat(day['date'])
        column, row = divmod((current-start).days, 7)
        x, y = 32 + column * 17.8, 101 + row * 14.2
        cells += f'<rect x="{x:.1f}" y="{y:.1f}" width="12" height="11" rx="2" fill="{palette[day["level"]]}"><title>{current.isoformat()}: {day["count"]} contributions</title></rect>'
        month = (current.year, current.month)
        if month not in months:
            cells += text(x, 84, current.strftime('%b'), 11, MUTED)
            months.add(month)
    sweep = commit_orbit(days, start, 32, 101, 17.8, 14.2, 943)
    calendar_body = '<g transform="translate(0,-64)">' + cells + sweep + '</g>'
    write('calendar.svg', 1000, 170, calendar_body, 'Real public GitHub calendar; a decorative comet highlights only active dates')
    write('calendar-static.svg', 1000, 170, '<g transform="translate(0,-64)">' + cells + '</g>', 'Real public GitHub calendar, static reduced-motion edition')
    activity = text(28, 43, 'Commit orbit', 25, INK, 600)
    activity += pixel('pixel-flame', 934, 247, 15, 20)
    activity += text(750, 42, f"{data['contribution_total']} contributions", 15, INK, 500)
    activity += cells + sweep + '<path d="M28 215h944" stroke="#35464f"/>'
    for i, (value, desc) in enumerate([(data['active_days'], 'active days'), (data['recent_contributions'], 'in the last 30 days'), (data['best_day'], 'most in one day')]):
        x = 30 + i * 318
        activity += text(x, 250, value, 25, INK, 600) + text(x + 72, 248, desc, 12, MUTED)
    activity += text(29, 284, f"Public GitHub snapshot / {data['date_label']}", 11, MUTED)
    write('activity.svg', 1000, 304, activity, 'Real public GitHub calendar and dated activity summary')

    recent_days = days[-182:]
    recent_start = date.fromisoformat(recent_days[0]['date'])
    mc = text(22, 41, 'Commit orbit', 27, INK, 600) + text(23, 76, 'Latest 26 weeks', 20, MUTED)
    month_seen = set()
    for day in recent_days:
        current = date.fromisoformat(day['date'])
        column, row = divmod((current - recent_start).days, 7)
        x, y = 26 + column * 17.3, 114 + row * 15.5
        mc += f'<rect x="{x:.1f}" y="{y:.1f}" width="12" height="12" rx="2" fill="{palette[day["level"]]}"><title>{current.isoformat()}: {day["count"]} contributions</title></rect>'
        if (current.year, current.month) not in month_seen:
            mc += text(x, 101, current.strftime('%b'), 12, MUTED)
            month_seen.add((current.year, current.month))
    mc += commit_orbit(recent_days, recent_start, 26, 114, 17.3, 15.5, 445, 12, 12)
    mc += text(23, 259, f"{data['contribution_total']} contributions", 27, INK, 600)
    mc += pixel('pixel-flame', 454, 239, 15, 20)
    mc += text(23, 291, f"{data['active_days']} active days / full-year summary", 20, MUTED)
    mc += text(23, 325, data['date_label'], 17, MUTED)
    write('activity-mobile.svg', 500, 348, mc, 'Latest 26 weeks of real public contributions, with a full-year contribution and active-day total')

    counts = sorted(data['language_counts'].items(), key=lambda item: -item[1])
    tools = text(24, 36, 'Toolkit', 22, INK, 700)
    tools += text(24, 69, ' / '.join(f'{name} {count}' for name, count in counts), 18, INK, 500)
    tools += text(24, 96, 'Primary language per public repository', 12, MUTED)
    write('toolkit-compact.svg', 1000, 116, tools, 'Primary language per public repository, not a proficiency score')
    mt = text(22, 37, 'Toolkit', 27, INK, 700)
    for i, (name, count) in enumerate(counts):
        mt += text(22 + (i % 2)*240, 77+(i//2)*34, f'{name} {count}', 22, INK, 500)
    mt += text(22, 183, 'Primary language per public repository', 16, MUTED)
    write('toolkit-compact-mobile.svg', 500, 205, mt, 'Primary language per public repository, not a proficiency score')
    for slug, label in [('lab', 'Explore the lab'), ('code', 'All repositories')]:
        for mobile in (False, True):
            w, h = (250, 94) if mobile else (500, 56)
            fill = MINT if slug == 'lab' else BG
            body = rect(1, 1, w-2, h-2, fill, 0, INK)
            body += text(17, 56 if mobile else 35, 'Build lab' if mobile and slug == 'lab' else ('Repositories' if mobile else label), 23 if mobile else 21, INK, 600)
            body += arrow(w-39, 49 if mobile else 28, size=20)
            write('footer-'+slug+('-mobile' if mobile else '')+'.svg', w, h, body, label)
    for mobile in (False, True):
        w, h = (500, 90) if mobile else (1000, 56)
        credit = text(22, 33, 'Nyan Cat via GIPHY', 19 if mobile else 15, INK)
        credit += text(22 if mobile else 625, 70 if mobile else 33, 'Public snapshot / '+data['date_label'], 17 if mobile else 14, MUTED)
        credit += pixel('pixel-robot', w-55, 2, 42, 42)
        write('footer-credit'+('-mobile' if mobile else '')+'.svg', w, h, credit, 'Original Nyan Cat via GIPHY. Public snapshot: '+data['date_label'])

    def picture(name, alt, width='100%'):
        def url(filename):
            version = hashlib.sha256((ASSETS / filename).read_bytes()).hexdigest()[:10]
            return f'https://raw.githubusercontent.com/TDUmii/TDUmii/main/assets/{filename}?v={version}'
        return f'<picture><source media="(max-width: 600px)" srcset="{url(name+"-mobile.svg")}" /><img src="{url(name+".svg")}" alt="{escape(alt, quote=True)}" width="{width}" /></picture>'
    def link(url, name, alt):
        return f'<a href="{url}">{picture(name, alt)}</a>'
    readme = link('https://tdumii.github.io/TDUmii/', 'profile-hero', 'Umi. Things I build.') + '\n\n'
    readme += '<table><tr><td width="50%" valign="top">' + link('https://github.com/TDUmii/umi-bridge', 'project-row-bridge', 'UmiBridge: ChatGPT meets Windows. Open repository.') + '</td><td width="50%" valign="top">' + link('https://github.com/TDUmii/QuietShare', 'project-row-quietshare', 'QuietShare: presentations, notes, optional offline transcription. Open repository.') + '</td></tr></table>\n\n'
    readme += link('https://github.com/TDUmii/BackgroundAutomationStudio', 'project-row-automation', 'Background Automation Studio: record, edit and replay Windows workflows. Open repository.') + '\n\n'
    readme += picture('activity', 'Real public GitHub activity. Latest 26 weeks on mobile; dated full-year totals.') + '\n\n' + picture('toolkit-compact', 'Primary languages by public repository count.') + '\n\n'
    readme += '<table><tr><td width="50%">'+link('https://tdumii.github.io/TDUmii/', 'footer-lab', 'Explore the lab')+'</td><td width="50%">'+link('https://github.com/TDUmii?tab=repositories', 'footer-code', 'Browse repositories')+'</td></tr></table>\n\n'
    readme += link('https://giphy.com/gifs/cat-pixel-art-nyan-7lsw8RenVcjCM', 'footer-credit', 'Original Nyan Cat via GIPHY. Public snapshot '+data['date_label']) + '\n'
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')


if __name__ == '__main__':
    render(json.loads((ASSETS / 'profile-data.json').read_text()))
