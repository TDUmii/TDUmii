"""Small native SVG pixel motifs; the shell hides every moving group on reduce.

Coordinates are in the containing scene's viewBox. Callers keep shooting stars
in the upper scene margin and route packets along a real connection path.
"""
from html import escape
from math import atan2, degrees

from .core import GOLD as AMBER, INK, MINT


def star(x, y, size, color, period=4.8, offset=0):
    """A dim 12-step pixel star with one short bright accent per period.

    x/y mark the center; size is the full width. offset advances the loop,
    making neighboring stars easy to stagger without additional state.
    """
    shape = 'M5 0H7V3H9V5H12V7H9V9H7V12H5V9H3V7H0V5H3V3H5Z'
    color = escape(str(color), quote=True)
    return f'''<g aria-hidden="true" pointer-events="none" transform="translate({x-size/2:g} {y-size/2:g}) scale({size/12:g})" fill="{color}">
<path d="{shape}" opacity=".18"/>
<g class="moving" opacity="0"><path d="{shape}"/>
<animate attributeName="opacity" values="0;0;.85;0;0" keyTimes="0;.12;.19;.29;1" dur="{period:g}s" begin="{-offset:g}s" repeatCount="indefinite"/>
</g></g>'''


def shooting_star(x, y, dx, dy):
    """A 36-by-3 pixel trail travels once for .7 seconds, then rests 6.8s.

    x/y is the initial head position, dx/dy its travel vector. The caller
    controls the endpoint, so the streak never has to cross text or artwork.
    """
    angle = degrees(atan2(dy, dx))
    return f'''<g class="moving" aria-hidden="true" pointer-events="none" opacity="0">
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;.008;.070;.093333;1" dur="7.5s" repeatCount="indefinite"/>
<g transform="translate({x:g} {y:g})">
<animateTransform attributeName="transform" type="translate" values="{x:g} {y:g};{x+dx:g} {y+dy:g};{x+dx:g} {y+dy:g}" keyTimes="0;.093333;1" dur="7.5s" repeatCount="indefinite"/>
<g transform="rotate({angle:g})">
<path d="M-36-1.5h9v3h-9z" fill="{MINT}" opacity=".20"/>
<path d="M-25-1.5h9v3h-9z" fill="{MINT}" opacity=".43"/>
<path d="M-14-1.5h9v3h-9z" fill="{MINT}" opacity=".72"/>
<path d="M-3-1.5h3v3h-3z" fill="{AMBER}"/>
</g></g></g>'''


def packet_burst(path, size=6, period=5.4):
    """Three ink/amber packets remain visible over the mint Bridge field.

    Each packet travels for .6 seconds and then hides; the whole burst lasts
    1.2 seconds including the stagger. period includes the remaining rest.
    Path is an SVG path-data string, not an element or resource identifier.
    """
    if period <= 1.2:
        raise ValueError('packet period must leave rest after the 1.2s burst')
    path = escape(str(path), quote=True)
    end = .6 / period
    packets = []
    for index, color in enumerate((INK, AMBER, INK)):
        delay = index * .3
        packets.append(f'''<g opacity="0">
<rect x="{-size/2:g}" y="{-size/2:g}" width="{size:g}" height="{size:g}" fill="{color}"/>
<animateMotion path="{path}" rotate="0" keyPoints="0;1;1" keyTimes="0;{end:.8f};1" calcMode="linear" dur="{period:g}s" begin="{delay:g}s" repeatCount="indefinite"/>
<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;{.03/period:.8f};{.54/period:.8f};{end:.8f};1" dur="{period:g}s" begin="{delay:g}s" repeatCount="indefinite"/>
</g>''')
    return '<g class="moving" aria-hidden="true" pointer-events="none">\n' + '\n'.join(packets) + '\n</g>'


def paper_glint(x, y, scale=1):
    """Two amber rays and a tiny pixel star acknowledge a completed page turn.

    The fixed-position glint appears at 3.0s, peaks at 3.2s, holds to 3.6s,
    and disappears at 3.8s of a seven-second reading loop.
    """
    return f'''<g class="moving" aria-hidden="true" pointer-events="none" transform="translate({x:g} {y:g}) scale({scale:g})" opacity="0" fill="{AMBER}">
<animate attributeName="opacity" values="0;0;.85;.85;0;0" keyTimes="0;.428571;.457143;.514286;.542857;1" dur="7s" repeatCount="indefinite"/>
<path d="M-14-11h3v7h-3zM-23-4h7v3h-7z"/>
<path d="M-1-4h2v3h3v2H1v3h-2V1h-3v-2h3z"/>
</g>'''


def workflow_marker(x, y, width, phase):
    """A single process underline advances every two seconds, with a rest."""
    return f'''<g class="moving" opacity="0" aria-hidden="true">
<rect x="{x}" y="{y}" width="{width}" height="3" fill="{MINT}"/>
<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.27;.31;1" calcMode="discrete" dur="6s" begin="{phase*2}s" repeatCount="indefinite"/>
</g>'''


def conveyor_pixels(x, y, step):
    """Three tread marks advance only during the Replay phase of the legend."""
    marks = ''.join(f'<rect x="{x+i*step}" y="{y}" width="8" height="5"/>' for i in range(3))
    return f'''<g fill="{INK}" aria-hidden="true">
<g opacity=".16">{marks}</g>
<g class="moving" opacity="0"><animate attributeName="opacity" values="0;0;.8;.8;0;0" keyTimes="0;.64;.67;.94;.97;1" dur="6s" repeatCount="indefinite"/>
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;14 0;14 0" keyTimes="0;.64;.94;1" dur="6s" repeatCount="indefinite"/>{marks}</g>
</g></g>'''
