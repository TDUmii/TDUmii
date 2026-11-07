"""Refresh public GitHub metadata and render portable profile assets. No dependencies."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from html.parser import HTMLParser
from datetime import date, datetime, timezone, timedelta
import argparse
import json
import os
import re
import time

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
USER = 'TDUmii'
VIETNAM = timezone(timedelta(hours=7))


def fetch(url):
    api = urlsplit(url).hostname == 'api.github.com'
    headers = {'User-Agent': 'Umi-Public-Profile', 'Accept': 'application/vnd.github+json' if api else 'text/html'}
    # The runner token avoids a shared anonymous API rate limit. Only public
    # endpoints are requested; the HTML calendar never receives this token.
    if api and os.environ.get('GITHUB_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GITHUB_TOKEN']
    req = Request(url, headers=headers)
    for attempt in range(3):
        try:
            with urlopen(req, timeout=20) as response:
                return response.read().decode('utf-8')
        except HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise RuntimeError('Public GitHub source returned HTTP '+str(error.code)) from None
        except (URLError, TimeoutError):
            if attempt == 2:
                raise RuntimeError('Public GitHub source could not be reached') from None
        time.sleep(2*(attempt+1))


def public_repositories(profile, get=fetch):
    repos, page = [], 1
    while True:
        batch = json.loads(get(f'https://api.github.com/users/{USER}/repos?per_page=100&type=owner&sort=full_name&page={page}'))
        if not isinstance(batch, list) or any(repo['private'] for repo in batch):
            raise ValueError('Expected public repositories only')
        repos.extend(batch)
        if len(repos) > profile['public_repos'] or len({repo['id'] for repo in repos}) != len(repos):
            raise ValueError('Public repository snapshot is incomplete or duplicated')
        if len(batch) < 100:
            break
        page += 1
    if profile['login'] != USER or len(repos) != profile['public_repos']:
        raise ValueError('Public repository snapshot is incomplete or duplicated')
    return repos


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
    parser.add_argument('--data-only', action='store_true', help='Refresh public JSON/JS without rendering artwork')
    args = parser.parse_args()
    raw_profile = fetch(f'https://api.github.com/users/{USER}')
    profile = json.loads(raw_profile)
    repos = public_repositories(profile)
    raw_repos = json.dumps(repos, indent=2)
    calendar = Calendar()
    raw_calendar = fetch(f'https://github.com/users/{USER}/contributions')
    review = ROOT / 'output' / 'analytics-review'
    review.mkdir(parents=True, exist_ok=True)
    for name, payload in [('profile-source.json', raw_profile), ('repos-source.json', raw_repos), ('calendar-source.html', raw_calendar)]:
        (review / name).write_text(payload, encoding='utf-8')
    from release_summary import latest_releases
    releases = latest_releases(fetch, review)
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0)
    local_time = fetched_at.astimezone(VIETNAM)
    today = date.fromisoformat(args.date) if args.date else local_time.date()
    calendar.feed(raw_calendar)
    days = calendar.result(today)
    languages = list(dict.fromkeys(repo['language'] for repo in repos if not repo['fork'] and repo['language']))
    selected = ['umi-bridge', 'QuietShare', 'BackgroundAutomationStudio']
    counts = {name: sum(repo['language'] == name for repo in repos if not repo['fork']) for name in languages}
    active = [day for day in days if day['count'] > 0]
    recent = [day for day in days if date.fromisoformat(day['date']) >= today - timedelta(days=29)]
    data = {'login': USER, 'date': today.isoformat(), 'date_label': label(today), 'public_repos': profile['public_repos'], 'stars': sum(repo['stargazers_count'] for repo in repos), 'languages': languages, 'language_counts': counts, 'active_days': len(active), 'recent_contributions': sum(day['count'] for day in recent), 'best_day': max(day['count'] for day in days), 'contribution_total': sum(day['count'] for day in days), 'contributions': days, 'projects': [{k: repo[k] for k in ['name', 'html_url', 'language', 'description', 'stargazers_count', 'updated_at']} for name in selected for repo in repos if repo['name'] == name], 'sources': [f'https://api.github.com/users/{USER}', f'https://api.github.com/users/{USER}/repos', f'https://github.com/users/{USER}/contributions']}
    data['fetched_at'] = fetched_at.isoformat().replace('+00:00', 'Z')
    data['latest_releases'] = releases
    data['sources'].extend(f'https://api.github.com/repos/{USER}/{repo}/releases' for repo in selected)
    data['updated_label'] = label(local_time.date()) + local_time.strftime(' / %H:%M UTC+7')
    for project in data['projects']:
        repo = next(repo for repo in repos if repo['name'] == project['name'])
        project.update({key: repo[key] for key in ('forks_count', 'pushed_at', 'archived')})
    data['repo_summary'] = {'original': sum(not repo['fork'] for repo in repos),
                            'fork': sum(repo['fork'] for repo in repos),
                            'archived': sum(repo['archived'] for repo in repos),
                            'total_forks': sum(repo['forks_count'] for repo in repos)}
    from profile_metrics import analyze
    analyze(data)
    if not args.data_only:
        from render_profile import render
        render(data)
    (ASSETS / 'profile-data.json').write_text(json.dumps(data, indent=2), encoding='utf-8')
    (ASSETS / 'profile-data.js').write_text('window.UMI_PROFILE=' + json.dumps(data) + ';', encoding='utf-8')
    print(json.dumps({'user': USER, 'repos': data['public_repos'], 'contributions': data['contribution_total'], 'calendar_days': len(days), 'date': today.isoformat()}))


if __name__ == '__main__':
    main()
