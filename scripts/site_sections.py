"""Static companion-page sections built from the same public snapshot."""
from html import escape

MARKS = {'umi-bridge': 'bridge', 'QuietShare': 'quietshare',
         'BackgroundAutomationStudio': 'automation'}


def latest_shipped(data):
    releases = data.get('latest_releases', [])
    if not releases:
        return ''
    rows = []
    for release in releases:
        kind = MARKS[release['repo']]
        label = escape(release['name']+' '+release['version']+' release', quote=True)
        improvement = '<p class="release-highlight">'+escape(release['highlight'])+'</p>' if release.get('highlight') else ''
        rows.append(f'''<a class="release-row" href="{escape(release['html_url'], quote=True)}" aria-label="{label}">
<img class="release-mark" src="assets/mark-{kind}.svg" width="32" height="32" alt="">
<span class="release-name">{escape(release['name'])}</span>
<span class="release-meta"><span class="release-version">{escape(release['version'])}</span>
<time datetime="{escape(release['published_at'], quote=True)}">{escape(release['date_label'])}</time></span>
{improvement}<svg class="icon release-arrow" aria-hidden="true"><use href="#arrow"/></svg></a>''')
    return '<section class="release-section" aria-labelledby="release-heading"><h2 id="release-heading">Latest shipped</h2><div class="release-ledger">'+''.join(rows)+'</div></section>'
