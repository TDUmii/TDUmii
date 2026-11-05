"""Refresh public GitHub metadata and render portable profile assets. No dependencies."""
from pathlib import Path
from urllib.request import Request, urlopen
from html.parser import HTMLParser
from datetime import date, datetime, timezone, timedelta
import argparse
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
    selected = ['umi-bridge', 'QuietShare', 'BackgroundAutomationStudio']
    counts = {name: sum(repo['language'] == name for repo in repos if not repo['fork']) for name in languages}
    active = [day for day in days if day['count'] > 0]
    recent = [day for day in days if date.fromisoformat(day['date']) >= today - timedelta(days=29)]
    data = {'login': USER, 'date': today.isoformat(), 'date_label': label(today), 'public_repos': profile['public_repos'], 'stars': sum(repo['stargazers_count'] for repo in repos), 'languages': languages, 'language_counts': counts, 'active_days': len(active), 'recent_contributions': sum(day['count'] for day in recent), 'best_day': max(day['count'] for day in days), 'contribution_total': sum(day['count'] for day in days), 'contributions': days, 'projects': [{k: repo[k] for k in ['name', 'html_url', 'language', 'description', 'stargazers_count', 'updated_at']} for name in selected for repo in repos if repo['name'] == name], 'sources': [f'https://api.github.com/users/{USER}', f'https://api.github.com/users/{USER}/repos', f'https://github.com/users/{USER}/contributions']}
    from render_profile import render
    render(data)
    (ASSETS / 'profile-data.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    (ASSETS / 'profile-data.js').write_text('window.UMI_PROFILE=' + json.dumps(data) + ';', encoding='utf-8')
    print(json.dumps({'user': USER, 'repos': data['public_repos'], 'contributions': data['contribution_total'], 'calendar_days': len(days), 'date': today.isoformat()}))


if __name__ == '__main__':
    main()
