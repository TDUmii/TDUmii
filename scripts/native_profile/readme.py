"""GitHub-native readme section."""
import hashlib
from html import escape
from .core import ASSETS, ROOT


def render(data):
    def picture(name, alt, width='100%'):
        def url(filename):
            version = hashlib.sha256((ASSETS / filename).read_bytes()).hexdigest()[:10]
            return f'https://raw.githubusercontent.com/TDUmii/TDUmii/main/assets/{filename}?v={version}'
        return f'<picture><source media="(max-width: 600px)" srcset="{url(name+"-mobile.svg")}" /><img src="{url(name+".svg")}" alt="{escape(alt, quote=True)}" width="{width}" /></picture>'
    def link(url, name, alt):
        return f'<a href="{url}">{picture(name, alt)}</a>'
    readme = picture('profile-hero', 'TDUmii. Code, cats and side quests.') + '\n\n'
    readme += '<table><tr><td width="50%" valign="top">' + link('https://github.com/TDUmii/umi-bridge', 'project-row-bridge', 'UmiBridge: ChatGPT meets Windows. Open repository.') + '</td><td width="50%" valign="top">' + link('https://github.com/TDUmii/QuietShare', 'project-row-quietshare', 'QuietShare: presentations, notes, optional offline transcription. Open repository.') + '</td></tr></table>\n\n'
    readme += link('https://github.com/TDUmii/BackgroundAutomationStudio', 'project-row-automation', 'Background Automation Studio: record, edit and replay Windows workflows. Open repository.') + '\n\n'
    readme += picture('activity', 'Real public GitHub activity. Latest 26 weeks on mobile; dated full-year totals.') + '\n\n' + picture('toolkit-compact', 'Primary languages by public repository count.') + '\n\n'
    readme += '<table><tr><td width="50%">'+link('https://github.com/TDUmii/TDUmii/blob/main/docs/SOURCE-MAP.md', 'footer-lab', 'Read the code and module guide')+'</td><td width="50%">'+link('https://github.com/TDUmii?tab=repositories', 'footer-code', 'Browse repositories')+'</td></tr></table>\n\n'
    readme += link('https://giphy.com/gifs/cat-pixel-art-nyan-7lsw8RenVcjCM', 'footer-credit', 'Original Nyan Cat via GIPHY. Public snapshot '+data['date_label']) + '\n'
    (ROOT / 'README.md').write_text(readme, encoding='utf-8')
