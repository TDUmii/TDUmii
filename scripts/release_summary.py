"""Small, source-backed summaries of the three showcased public releases."""
from datetime import datetime, timezone
from html import unescape
from urllib.parse import unquote, urlsplit
import json
import re

REPOSITORIES = ('umi-bridge', 'QuietShare', 'BackgroundAutomationStudio')
DISPLAY_NAMES = dict(zip(REPOSITORIES, ('UmiBridge', 'QuietShare', 'Background Automation Studio')))
# Exact source excerpts audited against these public release notes. A changed
# note must still contain the excerpt; otherwise use the conservative extractor.
AUDITED = {
    ('umi-bridge', 'v1.16.0'): (
        'A calendar heatmap shows actual requests by local day.',
        'Calendar heatmap of requests by local day.'),
    ('QuietShare', 'v0.20.0'): (
        'Add on-demand PDF thumbnails, bookmarks and go-to-page.',
        'PDF thumbnails, bookmarks and go-to-page.'),
    ('BackgroundAutomationStudio', 'v2.6.1'): (
        'Avoids unnecessary workflow expansion when the coordinate overlay is disabled.',
        'Avoid extra workflow expansion with overlay off.'),
}


def plain(text):
    text = unescape(text).replace('\\n', '\n')
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'!?\[([^\]]+)\]\([^)]*\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    text = re.sub(r'[`*_]', '', text)
    return ''.join(char for char in text if char in '\n\t' or ord(char) >= 32)


def highlight(repo, tag, body):
    notes = plain(body or '')
    audited = AUDITED.get((repo, tag))
    if audited and audited[0] in ' '.join(notes.split()):
        return audited[1]
    for line in notes.splitlines():
        match = re.match(r'^\s*(?:[-+] |\d+[.)] )(.*)', line)
        if not match:
            continue
        text = ' '.join(match[1].split())
        # Prefer plain English feature/fix statements; skip headings, downloads,
        # validation counts, marketing superlatives and non-English notes.
        if not text.isascii() or not re.match(r'^(?:Adds?|Fix(?:es)?|Prevents?|Avoids?|Supports?|Removes?|Updates?|Exports?|Preserves?)\b', text, re.I):
            continue
        if re.search(r'\b(?:best|amazing|revolutionary|ultimate|perfect|fastest|guaranteed)\b', text, re.I):
            continue
        sentence = re.split(r'(?<=[.!?])\s+', text)[0]
        if len(sentence) > 82:
            sentence = sentence[:79].rsplit(' ', 1)[0] + '...'
        return sentence
    return ''


def summarize(repo, release):
    if repo not in REPOSITORIES:
        raise ValueError('Release repository is not showcased')
    if not isinstance(release, dict) or type(release.get('draft')) is not bool or type(release.get('prerelease')) is not bool:
        raise ValueError('Invalid public release response')
    if release['draft'] or release['prerelease']:
        return None
    tag = release.get('tag_name')
    if not isinstance(tag, str) or not tag or len(tag) > 100 or any(char.isspace() or ord(char) < 32 for char in tag):
        raise ValueError('Invalid release tag')
    url = release.get('html_url', '')
    parts = urlsplit(url)
    if (parts.scheme != 'https' or parts.netloc != 'github.com' or parts.query or parts.fragment
            or unquote(parts.path) != f'/TDUmii/{repo}/releases/tag/{tag}'):
        raise ValueError('Release URL does not match the showcased public repository')
    published = release.get('published_at')
    try:
        timestamp = datetime.fromisoformat(published.replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            raise ValueError('Missing release timezone')
        timestamp = timestamp.astimezone(timezone.utc)
    except (AttributeError, TypeError, ValueError):
        raise ValueError('Invalid release publication timestamp') from None
    body = release.get('body') or ''
    if not isinstance(body, str):
        raise ValueError('Invalid release notes')
    return {'repo': repo, 'name': DISPLAY_NAMES[repo], 'tag': tag, 'version': tag,
            'html_url': url, 'published_at': timestamp.isoformat().replace('+00:00', 'Z'),
            'date_label': f'{timestamp:%b} {timestamp.day}, {timestamp.year}',
            'highlight': highlight(repo, tag, body)}


def latest_releases(get, review=None):
    latest = []
    for repo in REPOSITORIES:
        candidates, page, seen = [], 1, set()
        while True:
            raw = get(f'https://api.github.com/repos/TDUmii/{repo}/releases?per_page=100&page={page}')
            rows = json.loads(raw)
            if not isinstance(rows, list):
                raise ValueError('Expected a public release list')
            if review is not None:
                (review / f'releases-{repo}-{page}.json').write_text(raw, encoding='utf-8')
            for row in rows:
                item = summarize(repo, row)
                if item is not None:
                    if item['tag'] in seen:
                        raise ValueError('Duplicate public release')
                    seen.add(item['tag'])
                    candidates.append(item)
            if len(rows) < 100:
                break
            page += 1
        if candidates:
            latest.append(max(candidates, key=lambda item: item['published_at']))
    return sorted(latest, key=lambda item: item['published_at'], reverse=True)[:3]
