"""Render the GitHub-native edition of Umi's build lab. All claims use public data."""
from pathlib import Path
from datetime import date
from html import escape
import base64
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
BG, PANEL, INK, MUTED, LINE = '#0d1523', '#17242d', '#f0eee4', '#a9b8cc', '#2c3b4e'
MINT, GOLD, BLUE = '#b8efaa', '#efc780', '#8cbdd1'


def text(x, y, content, size=18, color=INK, weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(str(content))}</text>'


def rect(x, y, w, h, fill=PANEL, radius=12, stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"' + (f' stroke="{stroke}"' if stroke else '') + '/>'


def shell(w, h, body, title):
    font = base64.b64encode((ASSETS / 'sora-latin.woff2').read_bytes()).decode()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title, quote=True)}"><title>{escape(title)}</title><style>@font-face{{font-family:Sora;src:url(data:font/woff2;base64,{font});font-weight:400 800}}text{{font-family:Sora,Arial,sans-serif}}.nyan-still{{display:none}}.pulse{{animation:pulse 3s ease-in-out infinite}}.flow{{stroke-dasharray:6 12;animation:flow 3s linear infinite}}@keyframes pulse{{0%,100%{{opacity:.4}}50%{{opacity:1}}}}@keyframes flow{{to{{stroke-dashoffset:-72}}}}@media(prefers-reduced-motion:reduce){{.pulse,.flow{{animation:none}}.moving,.nyan-live{{display:none}}.nyan-still{{display:inline}}}}</style>{rect(0,0,w,h,BG)}{body}</svg>'''


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


def render(data):
    gif = base64.b64encode((ASSETS / 'nyan-cat.gif').read_bytes()).decode()
    poster = base64.b64encode((ASSETS / 'nyan-cat-still.png').read_bytes()).decode()
    def nyan(x, y, width, height):
        frame = f'x="{x}" y="{y}" width="{width}" height="{height}" style="image-rendering:pixelated"'
        return f'<image class="nyan-live" {frame} href="data:image/gif;base64,{gif}"/><image class="nyan-still" {frame} href="data:image/png;base64,{poster}"/>'
    def pixel(name, x, y, width, height):
        live = base64.b64encode((ASSETS / (name + '.gif')).read_bytes()).decode()
        still = base64.b64encode((ASSETS / (name + '-still.png')).read_bytes()).decode()
        frame = f'x="{x}" y="{y}" width="{width}" height="{height}" style="image-rendering:pixelated"'
        return f'<image class="nyan-live" {frame} href="data:image/gif;base64,{live}"/><image class="nyan-still" {frame} href="data:image/png;base64,{still}"/>'
    hero = text(34, 97, "Hi, I'm Umi.", 58, INK, 700)
    hero += text(37, 145, 'Windows tools. AI bridges.', 22, MUTED)
    hero += text(37, 178, 'Small obsessions.', 22, MUTED)
    hero += nyan(595, 90, 365, 145)
    hero += pixel('pixel-planet', 861, 7, 95, 95)
    hero += pixel('pixel-robot', 500, 176, 56, 56)
    hero += '<path d="M578 45h3m-1-1v3m183 171h3m-1-1v3M958 159h3m-1-1v3" stroke="#8cbdd1" stroke-width="1.5"/>'
    hero += '<path d="M36 247h928" stroke="#35464f"/>'
    hero += text(36, 280, f"{data['public_repos']} public repos", 15, MINT, 600)
    hero += text(249, 280, f"{data['stars']} stars", 15, GOLD, 600)
    hero += text(404, 280, f"{len(data['languages'])} languages", 15, BLUE, 600)
    hero += text(638, 280, f"{data['contribution_total']} contributions", 15, MUTED)
    write('profile-hero.svg', 1000, 310, hero, "Umi's build lab: Windows tools, AI bridges and automation, with the original Nyan Cat")

    bridge = text(28, 44, 'UmiBridge', 27, INK, 650) + text(28, 86, 'MCP tools for your Windows desktop.', 16, MINT)
    bridge += '<g id="connection-layer" fill="none" stroke="#6e9c80" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M149 178H190m-5-4 5 4-5 4M334 178H377m-5-4 5 4-5 4"/></g>'
    bridge += '<g id="connection-packets" class="moving"><circle id="bridge-packet-in" r="2.5" fill="#b8efaa"><animateMotion dur="2.4s" repeatCount="indefinite" path="M151 178H183"/></circle><circle id="bridge-packet-out" r="2.5" fill="#b8efaa"><animateMotion dur="2.4s" repeatCount="indefinite" path="M337 178H370"/></circle></g>'
    bridge += rect(29, 150, 115, 57, '#23363b', 8) + text(45, 184, 'ChatGPT', 16)
    bridge += rect(196, 143, 133, 70, '#344937', 8) + text(210, 184, 'UmiBridge', 16, MINT, 600)
    bridge += rect(382, 150, 88, 57, '#23363b', 8) + text(397, 184, 'PC', 18)
    bridge += pill(28, 242, 'MCP') + pill(102, 242, 'Windows') + pill(209, 242, 'Desktop tools')
    bridge += text(28, 306, 'Explore the repository', 13, MINT, 600)
    write('project-bridge.svg', 500, 334, bridge, 'UmiBridge: ChatGPT to Windows over MCP, with a local dashboard and desktop tools')

    quiet = text(28, 44, 'QuietShare', 27, INK, 650) + text(28, 86, 'Presentations, notes and offline transcripts.', 15, BLUE)
    quiet += rect(30, 141, 175, 94, '#253744', 8) + rect(41, 152, 153, 62, '#17242d', 4)
    quiet += text(55, 176, 'Presenter', 14, BLUE, 500) + '<path d="M56 191h97m-97 9h74" stroke="#607d8e" stroke-width="3"/>'
    quiet += rect(300, 141, 167, 94, '#253744', 8) + rect(311, 152, 145, 62, '#17242d', 4)
    quiet += text(331, 183, 'Audience', 14, INK, 500)
    quiet += '<path d="M205 182h95" stroke="#8cbdd1" stroke-width="2" class="flow"/>'
    quiet += pill(28, 249, 'Presentation', BLUE) + pill(174, 249, 'Offline Whisper', BLUE)
    quiet += text(28, 306, 'Explore the repository', 13, BLUE, 600)
    write('project-quietshare.svg', 500, 334, quiet, 'QuietShare: presentation companion with documents, notes and optional offline transcription')

    studio = text(28, 44, 'Background Automation Studio', 25, INK, 650)
    studio += text(28, 86, 'Record and replay Windows workflows.', 16, GOLD)
    studio += '<path d="M54 170H449" stroke="#4d5146" stroke-width="2"/>'
    for i, (name, color) in enumerate([('Record', GOLD), ('Edit', BLUE), ('Replay', MINT)]):
        x = 30 + i * 151
        studio += rect(x, 143, 130, 63, '#2a3034', 8) + text(x + 19, 181, name, 17, color, 600)
    studio += '<path d="M45 222h403" stroke="#efc780" stroke-width="2" class="flow"/>'
    studio += pill(28, 249, 'Recorder', GOLD) + pill(141, 249, 'Timeline', GOLD) + pill(251, 249, 'Windows', GOLD)
    studio += text(28, 306, 'Explore the repository', 13, GOLD, 600)
    write('project-automation.svg', 500, 334, studio, 'Background Automation Studio: Windows action recording, visual workflow editing and replay')

    counts = sorted(data['language_counts'].items(), key=lambda item: -item[1])
    count_total = sum(n for _, n in counts)
    colors = ['#b8efaa', '#8cbdd1', '#efc780', '#cfb4e7', '#a1c2bc', '#dcad89']
    tools = text(28, 43, 'The toolkit', 25, INK, 600)
    tools += text(28, 73, 'Primary language per public repository', 12, MUTED)
    offset = 28
    for i, (name, count) in enumerate(counts):
        width = 435 * count / count_total
        tools += rect(offset, 96, width - 3, 13, colors[i % len(colors)], 3)
        offset += width
        y = 145 + i * 25
        tools += rect(29, y - 9, 7, 7, colors[i % len(colors)], 2)
        tools += text(48, y, name, 13) + text(429, y, str(count), 13, MUTED)
    write('toolkit.svg', 500, 334, tools, 'Programming languages by public repository count; not a proficiency ranking')

    days = data['contributions']
    start = date.fromisoformat(days[0]['date'])
    cells, months = '', set()
    palette = ['#20313a', '#3b5b53', '#5d866b', '#89b985', '#b8efaa']
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
    activity += text(750, 42, f"{data['contribution_total']} contributions", 15, MINT, 500)
    activity += cells + sweep + '<path d="M28 215h944" stroke="#35464f"/>'
    for i, (value, desc) in enumerate([(data['active_days'], 'active days'), (data['recent_contributions'], 'in the last 30 days'), (data['best_day'], 'most in one day')]):
        x = 30 + i * 318
        activity += text(x, 250, value, 25, MINT, 600) + text(x + 72, 248, desc, 12, MUTED)
    activity += text(29, 284, f"Public GitHub snapshot · {data['date_label']}", 11, MUTED)
    write('activity.svg', 1000, 304, activity, 'Real public GitHub calendar and dated activity summary')

    # GitHub's two-column mobile table displays each 250px asset at ~140 CSS px.
    # Large, shorter labels are intentional; desktop assets remain unchanged.
    mobile_hero = text(26, 64, "Hi, I'm Umi.", 46, INK, 700)
    mobile_hero += text(28, 94, 'Windows tools. AI bridges.', 23, MUTED)
    mobile_hero += pixel('pixel-planet', 407, 10, 76, 76)
    mobile_hero += pixel('pixel-robot', 398, 279, 48, 48)
    mobile_hero += nyan(45, 135, 410, 163)
    mobile_hero += text(28, 363, f"{data['public_repos']} public repos", 23, MINT, 600)
    mobile_hero += text(300, 363, f"{data['stars']} stars", 23, GOLD, 600)
    mobile_hero += text(28, 411, f"{len(data['languages'])} languages", 23, BLUE, 600)
    mobile_hero += text(245, 411, f"{data['contribution_total']} contributions", 19, MUTED)
    write('profile-hero-mobile.svg', 500, 444, mobile_hero, "Umi's build lab: Windows tools and AI bridges, with the original animated Nyan Cat")

    mb = text(17, 40, 'UmiBridge', 27, INK, 650)
    mb += text(17, 84, 'AI meets your', 22, MINT) + text(17, 116, 'Windows PC.', 22, MINT)
    mb += rect(17, 153, 216, 113, '#21382a', 9)
    mb += text(37, 192, 'ChatGPT', 24) + '<path d="M123 204v22m-6-6 6 6 6-6" stroke="#b8efaa" stroke-width="2" fill="none"/>'
    mb += text(55, 253, 'MCP tools', 23, MINT, 500)
    mb += text(17, 317, 'Open project', 21, MINT, 600)
    write('project-bridge-mobile.svg', 250, 350, mb, 'UmiBridge: connect AI to Windows with MCP tools. Open repository.')

    mq = text(17, 40, 'QuietShare', 26, INK, 650)
    mq += text(17, 84, 'Presentations.', 22, BLUE) + text(17, 116, 'Notes. Offline.', 22, BLUE)
    mq += rect(17, 153, 216, 113, '#253744', 9)
    mq += text(32, 187, 'Your notes', 24, BLUE, 500) + '<path d="M33 205h182m-182 16h153m-153 16h169" stroke="#63869a" stroke-width="5"/>'
    mq += text(17, 317, 'Open project', 21, BLUE, 600)
    write('project-quietshare-mobile.svg', 250, 350, mq, 'QuietShare: presentations, notes and optional offline transcription. Open repository.')

    ma = text(17, 40, 'Automation', 26, INK, 650) + text(17, 75, 'Studio', 26, INK, 650)
    ma += text(17, 127, 'Windows', 24, GOLD) + text(17, 160, 'workflows.', 24, GOLD)
    ma += rect(17, 197, 216, 69, '#34352b', 9)
    ma += text(30, 240, 'Record → Replay', 21, GOLD, 500)
    ma += text(17, 317, 'Open project', 21, GOLD, 600)
    write('project-automation-mobile.svg', 250, 350, ma, 'Background Automation Studio: record and replay Windows workflows. Open repository.')

    mt = text(17, 39, 'The toolkit', 26, INK, 600) + text(17, 73, 'Public repo count', 18, MUTED)
    for i, (name, count) in enumerate(counts):
        y = 115 + i * 35
        mt += text(17, y, name, 24, colors[i % len(colors)], 500) + text(212, y, count, 24, MUTED)
    write('toolkit-mobile.svg', 250, 350, mt, 'Primary programming language by public repository count, not a proficiency rating')

    # Wide native rows keep the repository names and purpose readable on GitHub.
    for slug, name, short_name, description, mobile_lines, color in [
        ('bridge', 'UmiBridge', 'UmiBridge', 'Connect ChatGPT to Windows with MCP tools and a local dashboard.', ['ChatGPT meets Windows.', 'MCP tools. A local dashboard.'], MINT),
        ('quietshare', 'QuietShare', 'QuietShare', 'Documents, presenter notes and optional offline transcription.', ['Documents. Presenter notes.', 'Optional offline transcription.'], BLUE),
        ('automation', 'Background Automation Studio', 'Background Automation Studio', 'Record Windows actions, edit a timeline and replay a workflow.', ['Record Windows actions.', 'Edit a timeline. Replay a workflow.'], GOLD),
    ]:
        row = '<path d="M28 1h944" stroke="#35464f"/>'
        row += text(30, 57, name, 29, INK, 650)
        row += text(30, 96, description, 18, MUTED)
        row += text(30, 133, 'Open repository', 14, color, 600)
        row += f'<path d="M930 63l21-21m-21 0h21v21" fill="none" stroke="{color}" stroke-width="2"/>'
        write('project-row-' + slug + '.svg', 1000, 160, row, name + ': ' + description + ' Open repository.')
        mobile_row = '<path d="M22 1h456" stroke="#35464f"/>'
        if slug == 'automation':
            mobile_row += text(23, 42, 'Background Automation', 26, INK, 650) + text(23, 76, 'Studio', 26, INK, 650)
            baseline = 113
        else:
            mobile_row += text(23, 49, short_name, 30, INK, 650)
            baseline = 91
        mobile_row += text(23, baseline, mobile_lines[0], 22, MUTED) + text(23, baseline + 32, mobile_lines[1], 22, MUTED)
        mobile_row += text(23, baseline + 73, 'Open repository', 20, color, 600)
        mobile_row += f'<path d="M440 53l17-17m-17 0h17v17" fill="none" stroke="{color}" stroke-width="2"/>'
        write('project-row-' + slug + '-mobile.svg', 500, baseline + 99, mobile_row, name + ': ' + description + ' Open repository.')

    compact_tools = text(29, 37, 'Toolkit', 20, INK, 600)
    compact_tools += text(29, 69, 'Primary languages across public repositories', 13, MUTED)
    compact_tools += text(29, 106, '   /   '.join(f'{name} {count}' for name, count in counts), 17, MINT, 500)
    write('toolkit-compact.svg', 1000, 133, compact_tools, 'Primary language by repository count: ' + ', '.join(f'{name} {count}' for name, count in counts))
    compact_mobile = text(23, 39, 'Toolkit', 27, INK, 600) + text(23, 72, 'Primary language per public repository', 18, MUTED)
    for i, (name, count) in enumerate(counts):
        x, y = 23 + (i % 2) * 240, 116 + (i // 2) * 37
        compact_mobile += text(x, y, f'{name} {count}', 22, colors[i % len(colors)], 500)
    write('toolkit-compact-mobile.svg', 500, 135 + ((len(counts) - 1) // 2) * 37, compact_mobile, 'Primary programming language by public repository count')

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
    mc += text(23, 259, f"{data['contribution_total']} contributions", 27, MINT, 600)
    mc += pixel('pixel-flame', 454, 239, 15, 20)
    mc += text(23, 291, f"{data['active_days']} active days · full-year summary", 20, MUTED)
    mc += text(23, 325, data['date_label'], 17, MUTED)
    write('activity-mobile.svg', 500, 348, mc, 'Latest 26 weeks of real public contributions, with a full-year contribution and active-day total')

    # Native README links inherit GitHub's blue link styling. Keep the closing
    # navigation in the same visual family as the profile artwork instead.
    def footer_tile(name, label, primary):
        fill, ink = (MINT, '#18291c') if primary else (PANEL, INK)
        desktop = rect(0, 0, 500, 58, fill, 8)
        desktop += text(23, 37, label, 20, ink, 600)
        desktop += f'<path d="M450 37l16-16m-16 0h16v16" fill="none" stroke="{ink}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        write(name + '.svg', 500, 58, desktop, label)
        mobile = rect(0, 0, 250, 76, fill, 9)
        mobile_label = 'Build lab' if primary else 'Repositories'
        mobile += text(16, 46, mobile_label, 22, ink, 600)
        mobile += f'<path d="M211 46l15-15m-15 0h15v15" fill="none" stroke="{ink}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        write(name + '-mobile.svg', 250, 76, mobile, label)

    footer_tile('footer-lab', 'Explore the lab', True)
    footer_tile('footer-code', 'All repositories', False)
    credit = '<path d="M20 1h960" stroke="#35464f"/>'
    credit += text(23, 36, 'Nyan Cat via GIPHY', 15, BLUE)
    credit += '<path d="M206 34l11-11m-11 0h11v11" fill="none" stroke="#8cbdd1" stroke-width="1.5"/>'
    credit += text(657, 36, 'Public snapshot · ' + data['date_label'], 13, MUTED)
    write('footer-credit.svg', 1000, 58, credit, 'Nyan Cat artwork via GIPHY. Public GitHub snapshot: ' + data['date_label'])
    mobile_credit = '<path d="M20 1h460" stroke="#35464f"/>'
    mobile_credit += text(22, 37, 'Nyan Cat via GIPHY', 21, BLUE)
    mobile_credit += '<path d="M281 35l13-13m-13 0h13v13" fill="none" stroke="#8cbdd1" stroke-width="2"/>'
    mobile_credit += text(22, 74, 'Public snapshot · ' + data['date_label'], 19, MUTED)
    write('footer-credit-mobile.svg', 500, 97, mobile_credit, 'Nyan Cat artwork via GIPHY. Public GitHub snapshot: ' + data['date_label'])

    readme = f'''<a href="https://tdumii.github.io/TDUmii/"><img src="assets/profile-hero.svg" alt="Hi, I'm Umi. Windows tools. AI bridges. Small obsessions. Explore the full site." width="100%" /></a>

### Things I build

<a href="https://github.com/TDUmii/umi-bridge"><img src="assets/project-row-bridge.svg" alt="UmiBridge: connect ChatGPT to Windows with MCP tools and a local dashboard. Open repository." width="100%" /></a>

<a href="https://github.com/TDUmii/QuietShare"><img src="assets/project-row-quietshare.svg" alt="QuietShare: documents, presenter notes and optional offline transcription. Open repository." width="100%" /></a>

<a href="https://github.com/TDUmii/BackgroundAutomationStudio"><img src="assets/project-row-automation.svg" alt="Background Automation Studio: record Windows actions, edit a timeline and replay a workflow. Open repository." width="100%" /></a>

<img src="assets/toolkit-compact.svg" alt="Primary programming languages by public repository count, not a skill score." width="100%" />

![Umi's real public GitHub activity](assets/activity.svg)

<p align="center"><a href="https://tdumii.github.io/TDUmii/"><picture><source media="(max-width: 600px)" srcset="assets/footer-lab-mobile.svg" /><img src="assets/footer-lab.svg" alt="Explore Umi's build lab website" width="49%" /></picture></a> <a href="https://github.com/TDUmii?tab=repositories"><picture><source media="(max-width: 600px)" srcset="assets/footer-code-mobile.svg" /><img src="assets/footer-code.svg" alt="Browse all of Umi's public repositories" width="49%" /></picture></a></p>

<a href="https://giphy.com/gifs/cat-pixel-art-nyan-7lsw8RenVcjCM"><img src="assets/footer-credit.svg" alt="Original Nyan Cat artwork via GIPHY. Public snapshot: {data['date_label']}." width="100%" /></a>
'''
    def responsive(match):
        name, alt = match[1], match[2]
        mobile = name.removesuffix('.svg') + '-mobile.svg'
        return '<picture><source media="(max-width: 600px)" srcset="assets/' + mobile + '" /><img src="assets/' + name + '" alt="' + alt + '" width="100%" /></picture>'
    readme = re.sub(r'<img src="assets/([^"]+\.svg)" alt="([^"]*)" width="100%" />', responsive, readme)
    readme = readme.replace("![Umi's real public GitHub activity](assets/activity.svg)", '<picture><source media="(max-width: 600px)" srcset="assets/activity-mobile.svg" /><img src="assets/activity.svg" alt="Real public GitHub activity; recent 26 weeks shown on mobile with full-year totals" width="100%" /></picture>')
    # github.com/.../raw redirects drop query strings, defeating cache versions.
    # Link directly to the raw host so each content hash remains in the request.
    readme = re.sub(r'(src|srcset)="assets/([^"?]+)"', lambda match: match[1] + '="https://raw.githubusercontent.com/TDUmii/TDUmii/main/assets/' + match[2] + '?v=' + hashlib.sha256((ASSETS / match[2]).read_bytes()).hexdigest()[:10] + '"', readme)
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')


if __name__ == '__main__':
    render(json.loads((ASSETS / 'profile-data.json').read_text()))
