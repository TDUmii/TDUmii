"""A quiet release ledger: one independently linked row per featured project."""
from .core import BG, INK, MUTED, arrow, rect, text, write
from .marks import maker_mark

MARKS = {'umi-bridge': 'bridge', 'QuietShare': 'quietshare',
         'BackgroundAutomationStudio': 'automation'}


def line_width(value, size):
    """Conservative Sora-like advances, used only to fit bounded plain copy."""
    return size * sum(1.18 if c in 'MWmw@%' else .42 if c in 'ilIjtfr.,:;!| '
                      else .82 if c.isupper() else .72 for c in value)


def fit(value, width, size):
    if line_width(value, size) <= width:
        return value
    while value and line_width(value + '...', size) > width:
        value = value[:-1].rstrip()
    return value + '...'


def lines(value, width, size, limit=2):
    words, result, current = value.split(), [], ''
    for index, word in enumerate(words):
        candidate = (current + ' ' + word).strip()
        if current and line_width(candidate, size) > width:
            result.append(current)
            current = word
            if len(result) == limit-1:
                result.append(fit(' '.join(words[index:]), width, size))
                return result
        else:
            current = candidate
    if current:
        result.append(fit(current, width, size))
    return result[:limit]


def render(data):
    for mobile in (False, True):
        w, h = (500, 66) if mobile else (1000, 64)
        body = rect(0, 0, w, h, BG, 0)
        body += text(22, 44, 'Latest shipped', 30 if mobile else 32, INK, 700)
        write('shipped-heading'+('-mobile' if mobile else '')+'.svg', w, h, body, 'Latest shipped')
        for release in data.get('latest_releases', []):
            kind = MARKS[release['repo']]
            w, h = (500, 158) if mobile else (1000, 88)
            body = rect(0, 0, w, h, BG, 0)
            body += f'<path d="M22 1H{w-22}" stroke="{INK}" stroke-opacity=".2"/>'
            body += maker_mark(kind, 22, 21 if mobile else 22, 32)
            name = 'Automation Studio' if mobile and kind == 'automation' else release['name']
            body += text(70, 43 if mobile else 34, name, 26 if mobile else 23, INK, 700)
            if mobile:
                body += text(70, 76, fit(release['version'], 145, 21), 21, INK, 600)
                body += text(235, 76, release['date_label'], 21, MUTED)
                for index, line in enumerate(lines(release.get('highlight', ''), 404, 22)):
                    body += text(70, 110+index*29, line, 22, INK)
                body += arrow(458, 34, size=20)
            else:
                body += text(620, 34, fit(release['version'], 158, 19), 19, INK, 600)
                body += text(803, 34, release['date_label'], 17, MUTED)
                body += text(70, 65, fit(release.get('highlight', ''), 858, 19), 19, MUTED)
                body += arrow(949, 34, size=22)
            title = release['name']+' '+release['version']+'. '+release['date_label']+'. '+release.get('highlight', '')+' Open release.'
            write('shipped-'+kind+('-mobile' if mobile else '')+'.svg', w, h, body, title)
