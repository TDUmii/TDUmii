"""Render the GitHub-native edition of Umi's build lab. All claims use public data."""
from pathlib import Path
from datetime import date
from html import escape
import base64
import json

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
BG, PANEL, INK, MUTED, LINE = '#0e1720', '#17242d', '#edf2e9', '#b0bec7', '#35464f'
MINT, GOLD, BLUE = '#b8efaa', '#efc780', '#8cbdd1'


def text(x, y, content, size=18, color=INK, weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}">{escape(str(content))}</text>'


def rect(x, y, w, h, fill=PANEL, radius=12, stroke=None):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}"' + (f' stroke="{stroke}"' if stroke else '') + '/>'


def shell(w, h, body, title):
    font = base64.b64encode((ASSETS / 'sora-latin.woff2').read_bytes()).decode()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title, quote=True)}"><title>{escape(title)}</title><style>@font-face{{font-family:Sora;src:url(data:font/woff2;base64,{font});font-weight:400 800}}text{{font-family:Sora,Arial,sans-serif}}.pulse{{animation:pulse 3s ease-in-out infinite}}.flow{{stroke-dasharray:6 12;animation:flow 3s linear infinite}}@keyframes pulse{{0%,100%{{opacity:.4}}50%{{opacity:1}}}}@keyframes flow{{to{{stroke-dashoffset:-72}}}}@media(prefers-reduced-motion:reduce){{.pulse,.flow{{animation:none}}.moving{{display:none}}}}</style>{rect(0,0,w,h,BG)}{body}</svg>'''


def pill(x, y, value, color=MINT, width=None):
    w = width or len(value) * 8 + 26
    return rect(x, y, w, 28, '#26363e', 5) + text(x + 12, y + 19, value, 12, color, 500)


def write(name, w, h, body, title):
    (ASSETS / name).write_text(shell(w, h, body, title), encoding='utf-8')


def render(data):
    gif = base64.b64encode((ASSETS / 'nyan-cat.gif').read_bytes()).decode()
    hero = text(34, 72, "Umi's build lab.", 49, INK, 700)
    hero += text(37, 113, 'Windows tools. AI bridges. Small obsessions.', 20, MUTED)
    hero += text(37, 151, 'I build things that make a desktop more useful.', 16, MUTED)
    hero += pill(36, 185, 'Windows') + pill(139, 185, 'Local-first') + pill(270, 185, 'Public repos')
    hero += rect(615, 22, 361, 209, PANEL, 12)
    hero += '<path d="M637 47h5m309 0h5m-319 158h5m309 0h5" stroke="#8cbdd1" stroke-width="3" class="pulse"/>'
    hero += f'<image x="630" y="49" width="329" height="130" href="data:image/gif;base64,{gif}" style="image-rendering:pixelated"/>'
    hero += text(644, 211, 'NYAN CAT / FLIGHT DECK', 11, BLUE, 500)
    hero += '<path d="M36 247h928" stroke="#35464f"/>'
    hero += text(36, 280, f"{data['public_repos']} public repos", 15, MINT, 600)
    hero += text(249, 280, f"{data['stars']} stars", 15, GOLD, 600)
    hero += text(404, 280, f"{len(data['languages'])} languages", 15, BLUE, 600)
    hero += text(638, 280, '@TDUmii', 15, MUTED)
    write('profile-hero.svg', 1000, 310, hero, "Umi's build lab: Windows tools, AI bridges and automation, with the original Nyan Cat")

    bridge = text(28, 44, 'UmiBridge', 27, INK, 650) + text(28, 75, 'AI meets your Windows desktop.', 16, MINT)
    bridge += text(28, 112, 'MCP tools, files, terminals and a local dashboard.', 13, MUTED)
    bridge += rect(29, 150, 115, 57, '#23363b', 8) + text(45, 184, 'ChatGPT', 16)
    bridge += rect(196, 143, 133, 70, '#344937', 8) + text(210, 184, 'UmiBridge', 16, MINT, 600)
    bridge += rect(382, 150, 88, 57, '#23363b', 8) + text(397, 184, 'PC', 18)
    bridge += '<path d="M144 178h52m133 0h53" stroke="#b8efaa" stroke-width="2" class="flow"/>'
    bridge += '<circle r="4" fill="#efc780" class="moving"><animateMotion dur="4s" repeatCount="indefinite" path="M145 178H382"/></circle>'
    bridge += pill(28, 242, 'MCP') + pill(102, 242, 'Windows') + pill(209, 242, 'Desktop tools')
    bridge += text(28, 306, 'Explore the repository', 13, MINT, 600)
    write('project-bridge.svg', 500, 334, bridge, 'UmiBridge: ChatGPT to Windows over MCP, with a local dashboard and desktop tools')

    quiet = text(28, 44, 'QuietShare', 27, INK, 650) + text(28, 75, 'Your notes stay on your side.', 16, BLUE)
    quiet += text(28, 112, 'Documents, presenter notes and offline transcripts.', 13, MUTED)
    quiet += rect(30, 141, 175, 94, '#253744', 8) + rect(41, 152, 153, 62, '#17242d', 4)
    quiet += text(55, 176, 'Presenter', 14, BLUE, 500) + '<path d="M56 191h97m-97 9h74" stroke="#607d8e" stroke-width="3"/>'
    quiet += rect(300, 141, 167, 94, '#253744', 8) + rect(311, 152, 145, 62, '#17242d', 4)
    quiet += text(331, 183, 'Audience', 14, INK, 500)
    quiet += '<path d="M205 182h95" stroke="#8cbdd1" stroke-width="2" class="flow"/>'
    quiet += pill(28, 249, 'Presentation', BLUE) + pill(174, 249, 'Offline Whisper', BLUE)
    quiet += text(28, 306, 'Explore the repository', 13, BLUE, 600)
    write('project-quietshare.svg', 500, 334, quiet, 'QuietShare: presentation companion with documents, notes and optional offline transcription')

    studio = text(28, 44, 'Background Automation Studio', 25, INK, 650)
    studio += text(28, 77, 'Turn repetitive work into a workflow.', 16, GOLD)
    studio += text(28, 112, 'Record, arrange and replay Windows actions.', 13, MUTED)
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
    write('calendar.svg', 1000, 170, '<g transform="translate(0,-64)">' + cells + '</g>', 'Real public GitHub calendar; every cell has a date and contribution count')
    activity = text(28, 43, 'Built one day at a time.', 25, INK, 600)
    activity += text(750, 42, f"{data['contribution_total']} contributions", 15, MINT, 500)
    activity += cells + '<path d="M28 215h944" stroke="#35464f"/>'
    for i, (value, desc) in enumerate([(data['active_days'], 'active days'), (data['recent_contributions'], 'in the last 30 days'), (data['best_day'], 'most in one day')]):
        x = 30 + i * 318
        activity += text(x, 250, value, 25, MINT, 600) + text(x + 72, 248, desc, 12, MUTED)
    activity += text(29, 284, f"Public GitHub snapshot · {data['date_label']}", 11, MUTED)
    write('activity.svg', 1000, 304, activity, 'Real public GitHub calendar and dated activity summary')

    readme = f'''<a href="https://tdumii.github.io/TDUmii/"><img src="assets/profile-hero.svg" alt="Umi's build lab. Windows tools, AI bridges and automation. Explore the full site." width="100%" /></a>

### Things I build

<table><tr><td width="50%"><a href="https://github.com/TDUmii/umi-bridge"><img src="assets/project-bridge.svg" alt="UmiBridge: AI meets your Windows desktop, with MCP tools and a local dashboard." width="100%" /></a></td><td width="50%"><a href="https://github.com/TDUmii/QuietShare"><img src="assets/project-quietshare.svg" alt="QuietShare: documents, presenter notes and optional offline transcription." width="100%" /></a></td></tr><tr><td width="50%"><a href="https://github.com/TDUmii/BackgroundAutomationStudio"><img src="assets/project-automation.svg" alt="Background Automation Studio: record, edit and replay Windows workflows." width="100%" /></a></td><td width="50%"><img src="assets/toolkit.svg" alt="Primary programming languages by public repository count, not a skill score." width="100%" /></td></tr></table>

![Umi's real public GitHub activity](assets/activity.svg)

<p align="center"><a href="https://tdumii.github.io/TDUmii/">Explore the build lab</a> · <a href="https://github.com/TDUmii?tab=repositories">All repositories</a></p>

<sub>Public data · {data['date_label']}. Nyan Cat via <a href="https://giphy.com/gifs/cat-pixel-art-nyan-7lsw8RenVcjCM">GIPHY</a>.</sub>
'''
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')


if __name__ == '__main__':
    render(json.loads((ASSETS / 'profile-data.json').read_text()))
