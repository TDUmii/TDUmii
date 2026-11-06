"""A single owner mark and an animated Nyan night scene for the native README."""
from .core import BG, GOLD, INK, MINT, pixel, rect, text, write
from .ornaments import shooting_star, star


def owner_mark(x, y):
    """Interlocking pixel T/D letterforms, drawn as type rather than an icon font."""
    return f'''<g transform="translate({x} {y})">
<path d="M0 0H43V12H29V51H15V12H0Z" fill="{MINT}"/>
<path d="M37 17H58L73 30V54L58 67H37V54H52L60 47V36L52 30H37Z" fill="{BG}"/>
<path d="M66 0H77V11H66Z" fill="{GOLD}"/></g>'''


def night_scene(x, y, scale=1):
    # Original GIF payloads retain colors, timing and natural aspect ratios.
    scene = '<ellipse cx="224" cy="91" rx="119" ry="44" transform="rotate(-24 224 91)" fill="none" stroke="#476168" stroke-width="1.5"/>'
    for sx, sy, size in [(13, 31, 5), (89, 68, 3), (348, 22, 6), (323, 200, 4), (42, 184, 4)]:
        scene += rect(sx, sy, size, size, MINT if size < 5 else GOLD, 0)
    for sx, sy, size, color, offset in [(32, 89, 12, GOLD, 0), (145, 18, 8, MINT, 1.6), (340, 104, 10, GOLD, 3.2)]:
        scene += star(sx, sy, size, color, offset=offset)
    scene += shooting_star(32, 25, 100, 30)
    scene += pixel('pixel-planet', 180, 4, 118, 118)
    scene += pixel('nyan-cat', 4, 113, 345, 136.62)
    scene += f'''<g class="moving"><rect width="5" height="5" fill="{GOLD}">
<animateMotion dur="12s" repeatCount="indefinite" path="M112 115C125 60 330 16 341 66C349 105 141 169 112 115Z"/></rect></g>'''
    return f'<g transform="translate({x} {y}) scale({scale})">{scene}</g>'


def render(data):
    for mobile in (False, True):
        width, height = (500, 414) if mobile else (1000, 300)
        body = rect(0, 0, width, height, INK, 0)
        body += owner_mark(26, 24)
        body += text(120, 62, data['login'], 23 if mobile else 24, BG, 600)
        if mobile:
            body += text(25, 143, 'Code, cats', 53, BG, 800)
            body += text(25, 201, '& side quests.', 48, MINT, 800)
            body += night_scene(77, 226, .70)
            body += f'<path d="M0 {height-15}H18V{height-28}H38V{height}H0Z" fill="{GOLD}"/>'
        else:
            body += text(27, 158, 'Code, cats', 72, BG, 800)
            body += text(27, 236, '& side quests.', 65, MINT, 800)
            body += night_scene(617, 24)
            body += f'<path d="M0 284H20V273H40V300H0Z" fill="{GOLD}"/>'
        body += f'<path d="M{width-42} 0V12H{width-22}V26H{width}V0Z" fill="{MINT}"/>'
        write('profile-hero' + ('-mobile' if mobile else '') + '.svg', width, height, body,
              'TDUmii. Code, cats and side quests. Original Nyan Cat and pixel planet.')

