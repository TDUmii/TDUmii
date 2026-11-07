"""GitHub-native readme section."""
import hashlib
import re
from html import escape
from .core import ASSETS, ROOT


def render(data, asset_ref='main'):
    if not re.fullmatch(r'main|[0-9a-f]{7,40}', asset_ref):
        raise ValueError('asset_ref must be main or a Git commit SHA')
    def picture(name, alt, width='100%'):
        def url(filename):
            version = hashlib.sha256((ASSETS / filename).read_bytes()).hexdigest()[:10]
            return f'https://raw.githubusercontent.com/TDUmii/TDUmii/{asset_ref}/assets/{filename}?v={version}'
        return f'<picture><source media="(max-width: 600px)" srcset="{url(name+"-mobile.svg")}" /><img src="{url(name+".svg")}" alt="{escape(alt, quote=True)}" width="{width}" /></picture>'
    def link(url, name, alt):
        return f'<a href="{url}">{picture(name, alt)}</a>'
    readme = picture('profile-hero', 'TDUmii. Code, cats and side quests.') + '\n\n'
    readme += '<table><tr><td width="50%" valign="top">' + link('https://github.com/TDUmii/umi-bridge', 'project-row-bridge', 'UmiBridge: ChatGPT meets Windows. Open repository.') + '</td><td width="50%" valign="top">' + link('https://github.com/TDUmii/QuietShare', 'project-row-quietshare', 'QuietShare: presentations, notes, optional offline transcription. Open repository.') + '</td></tr></table>\n\n'
    readme += link('https://github.com/TDUmii/BackgroundAutomationStudio', 'project-row-automation', 'Background Automation Studio: record, edit and replay Windows workflows. Open repository.') + '\n\n'
    if data.get('latest_releases'):
        from .shipped import MARKS
        readme += '<p>' + picture('shipped-heading', 'Latest shipped')
        for release in data['latest_releases']:
            alt = release['name']+' '+release['version']+'. '+release['date_label']+'. '+release.get('highlight', '')+' Open release.'
            readme += '<br />' + link(release['html_url'], 'shipped-'+MARKS[release['repo']], alt)
        readme += '</p>\n\n'
    readme += picture('activity', 'Publicly displayed GitHub contributions. Latest 26 weeks on mobile; dated full-window totals.') + '\n\n'
    readme += picture('insights-rhythm', 'Monthly contributions with partial-month markers, and average contributions per observed weekday.') + '\n\n'
    readme += picture('insights-projects', 'Three featured repository statistics and the share of observed dates with contributions.') + '\n\n'
    readme += picture('toolkit-compact', 'Primary languages by public repository count.') + '\n\n'
    readme += '<table><tr><td width="50%">'+link('https://github.com/TDUmii/TDUmii/blob/main/docs/SOURCE-MAP.md', 'footer-lab', 'Read the code and module guide')+'</td><td width="50%">'+link('https://github.com/TDUmii?tab=repositories', 'footer-code', 'Browse repositories')+'</td></tr></table>\n\n'
    readme += link('https://giphy.com/gifs/cat-pixel-art-nyan-7lsw8RenVcjCM', 'footer-credit', 'Original Nyan Cat via GIPHY. Public snapshot '+data['date_label']) + '\n'
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')
