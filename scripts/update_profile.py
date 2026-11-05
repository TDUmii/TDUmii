"""Refresh public GitHub metadata and render portable profile assets. No dependencies."""
from pathlib import Path
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from html import escape
from datetime import date, datetime, timezone, timedelta
import argparse
import base64
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
USER = 'TDUmii'


def fetch(url):
    req = Request(url, headers={'User-Agent': 'Umi-Public-Profile', 'Accept': 'application/vnd.github+json' if 'api.github.com' in url else 'text/html'})
    with urlopen(req, timeout=30) as response:
        return response.read().decode('utf-8')


class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.days, self.tips = {}, {}
        self.tip, self.buffer = None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'td' and attrs.get('data-date'):
            self.days[attrs['id']] = {'date': attrs['data-date'], 'level': int(attrs['data-level'])}
        if tag == 'tool-tip' and attrs.get('for'):
            self.tip, self.buffer = attrs['for'], []

    def handle_data(self, text):
        if self.tip:
            self.buffer.append(text)

    def handle_endtag(self, tag):
        if tag == 'tool-tip' and self.tip:
            self.tips[self.tip] = ''.join(self.buffer).strip()
            self.tip = None

    def result(self, today):
        result = []
        for key, day in self.days.items():
            text = self.tips[key]
            match = re.match(r'([\d,]+) contributions? on ', text)
            if not match and not text.startswith('No contributions on '):
                raise ValueError('Unrecognized public calendar label')
            if date.fromisoformat(day['date']) <= today:
                result.append({**day, 'count': int(match[1].replace(',', '')) if match else 0})
        result.sort(key=lambda item: item['date'])
        if len(result) < 350 or len({item['date'] for item in result}) != len(result):
            raise ValueError('Incomplete or duplicate public calendar')
        return result


def label(day):
    return f'{day.strftime("%b")} {day.day}, {day.year}'


def render(data):
    font = base64.b64encode((ASSETS / 'space-grotesk-latin.woff2').read_bytes()).decode()
    style = f"@font-face{{font-family:Space Grotesk;src:url(data:font/woff2;base64,{font});font-weight:300 700}}text{{font-family:'Space Grotesk',Arial,sans-serif}}"

    def svg(height, body, title):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-label="{escape(title, quote=True)}"><title>{escape(title)}</title><style>{style}</style><rect width="960" height="{height}" rx="8" fill="#16222c"/>{body}</svg>'

    def text(x, y, value, size=15, color='#a6b5bf', extra=''):
        return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(value))}</text>'

    stats = ''
    for i, (value, name) in enumerate([(data['public_repos'], 'Public repos'), (data['stars'], 'Stars'), (len(data['languages']), 'Languages')]):
        x = 34 + i * 320
        stats += text(x, 63, value, 43, '#ddb274', 'font-weight="600"') + text(x, 98, name)
        if i < 2:
            stats += f'<path d="M{315+i*320} 28v73" stroke="#30414e"/>'
    (ASSETS / 'stats.svg').write_text(svg(130, stats, f"{data['public_repos']} public repositories, {data['stars']} stars, {len(data['languages'])} languages"), encoding='utf-8')
    tools = ''
    for i, name in enumerate(data['languages']):
        x = 24 + i * 152
        tools += f'<rect x="{x}" y="18" width="139" height="36" rx="4" fill="#253744"/>' + text(x + 13, 42, name, 15, '#e9e7df')
    (ASSETS / 'languages.svg').write_text(svg(72, tools, 'Repository languages: ' + ', '.join(data['languages'])), encoding='utf-8')
    days = data['contributions']
    start = date.fromisoformat(days[0]['date'])
    palette = ['#25343f', '#36545b', '#527d78', '#80ac9c', '#ddb274']
    cells, months = '', set()
    for day in days:
        current = date.fromisoformat(day['date'])
        delta = (current - start).days
        column, row = divmod(delta, 7)
        x, y = 40 + column * 16.7, 39 + row * 13.5
        cells += f'<rect x="{x:.1f}" y="{y:.1f}" width="11" height="10" rx="2" fill="{palette[day["level"]]}"><title>{current.isoformat()}: {day["count"]} contributions</title></rect>'
        month = (current.year, current.month)
        if month not in months:
            cells += text(x, 22, current.strftime('%b'), 11)
            months.add(month)
    cells += text(12, 62, 'M', 9) + text(12, 89, 'W', 9) + text(12, 116, 'F', 9)
    cells += text(24, 158, label(start) + ' - ' + label(date.fromisoformat(days[-1]['date'])), 11)
    cells += text(768, 158, f"{data['contribution_total']} contributions", 12, '#80ac9c')
    title = f"{USER}'s public contribution calendar: {data['contribution_total']} contributions, {days[0]['date']} to {days[-1]['date']}"
    (ASSETS / 'activity.svg').write_text(svg(174, cells, title), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', help='Snapshot date in YYYY-MM-DD form')
    args = parser.parse_args()
    today = date.fromisoformat(args.date) if args.date else datetime.now(timezone(timedelta(hours=7))).date()
    profile = json.loads(fetch(f'https://api.github.com/users/{USER}'))
    repos = json.loads(fetch(f'https://api.github.com/users/{USER}/repos?per_page=100&type=owner&sort=updated'))
    if profile['login'] != USER or len(repos) != profile['public_repos'] or any(repo['private'] for repo in repos):
        raise ValueError('Public repository snapshot is incomplete')
    calendar = Calendar()
    calendar.feed(fetch(f'https://github.com/users/{USER}/contributions'))
    days = calendar.result(today)
    languages = list(dict.fromkeys(repo['language'] for repo in repos if not repo['fork'] and repo['language']))
    selected = ['umi-bridge', 'QuietShare', 'aoe-web-browser-vn']
    data = {'login': USER, 'date': today.isoformat(), 'date_label': label(today), 'public_repos': profile['public_repos'], 'stars': sum(repo['stargazers_count'] for repo in repos), 'languages': languages, 'contribution_total': sum(day['count'] for day in days), 'contributions': days, 'projects': [{k: repo[k] for k in ['name', 'html_url', 'language']} for name in selected for repo in repos if repo['name'] == name], 'sources': [f'https://api.github.com/users/{USER}', f'https://api.github.com/users/{USER}/repos', f'https://github.com/users/{USER}/contributions']}
    render(data)
    (ASSETS / 'profile-data.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    (ASSETS / 'profile-data.js').write_text('window.UMI_PROFILE=' + json.dumps(data) + ';', encoding='utf-8')
    readme = f'''<div align="center">
<h1>Hi, I'm Umi.</h1>
<p>Building useful little things.</p>
<a href="https://tdumii.github.io/TDUmii/">Website</a>
<img src="assets/nyan-cat.gif" alt="Nyan Cat flying with a rainbow trail" width="500" />
</div>

![Public GitHub statistics](assets/stats.svg)

### Loadout

![Repository languages: {', '.join(languages)}](assets/languages.svg)

### Activity

![Real public GitHub contribution calendar](assets/activity.svg)

### Selected projects

[UmiBridge](https://github.com/{USER}/umi-bridge) · [QuietShare](https://github.com/{USER}/QuietShare) · [AOE Web VN](https://github.com/{USER}/aoe-web-browser-vn)

<sub>Public GitHub snapshot · {label(today)}. Nyan Cat via [GIPHY](https://giphy.com/gifs/cat-pixel-art-nyan-7lsw8RenVcjCM).</sub>
'''
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')
    print(json.dumps({'user': USER, 'repos': data['public_repos'], 'contributions': data['contribution_total'], 'calendar_days': len(days), 'date': today.isoformat()}))


if __name__ == '__main__':
    main()
