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
    """Record/Edit/Replay underline; phase is 0, 1, or 2 in an 8s loop."""
    start, length = ((0, .8), (1.1, 1.2), (2.8, 1.5))[phase]
    return f'''<g class="moving" opacity="0" aria-hidden="true">
<rect x="{x}" y="{y}" width="{width}" height="3" fill="{MINT}"/>
{_opacity(start, start+length, 8)}
</g>'''


def conveyor_pixels(x, y, step):
    """Three tread marks advance only during the Replay phase of the legend."""
    marks = ''.join(f'<rect x="{x+i*step}" y="{y}" width="8" height="5"/>' for i in range(3))
    return f'''<g fill="{INK}" aria-hidden="true">
<g opacity=".16">{marks}</g>
<g class="moving" opacity="0">{_opacity(2.8, 4.3, 8, .8)}
<g><animateTransform attributeName="transform" type="translate" values="0 0;0 0;32 0;32 0" keyTimes="0;.35;.5375;1" dur="8s" repeatCount="indefinite"/>{marks}</g>
</g></g>'''


def _opacity(start, end, period, peak=1):
    """A bounded activity window with brief fades and an explicit rest."""
    times = (0, max(.001, start)/period, (start+.06)/period,
             (end-.06)/period, end/period, 1)
    return f'<animate attributeName="opacity" values="0;0;{peak};{peak};0;0" keyTimes="{";".join(f"{t:.8f}" for t in times)}" dur="{period:g}s" repeatCount="indefinite"/>'


def bridge_dialogue(outbound_path, return_path, robot_x, robot_y,
                    terminal_x, terminal_y, size=7):
    """Absolute scene paths and acknowledgement centers; a 6.8s dialogue."""
    reply = escape(str(return_path), quote=True)
    def ack(x, y, start, end):
        return f'''<g transform="translate({x:g} {y:g})" opacity="0" fill="none" stroke="{INK}" stroke-width="2.5">
<path d="M-10-4v-6h6M4-10h6v6M10 4v6H4M-4 10h-6V4"/>
{_opacity(start, end, 6.8)}</g>'''
    return f'''<g class="moving" aria-hidden="true" pointer-events="none">
{packet_burst(outbound_path, size, 6.8)}
{ack(robot_x, robot_y, 1.25, 1.85)}
<g opacity="0"><rect x="{-size/2:g}" y="{-size/2:g}" width="{size:g}" height="{size:g}" fill="{AMBER}"/>
{_opacity(1.9, 2.7, 6.8)}
<animateMotion path="{reply}" rotate="0" keyPoints="0;0;1;1" keyTimes="0;.27941176;.39705882;1" calcMode="linear" dur="6.8s" repeatCount="indefinite"/></g>
{ack(terminal_x, terminal_y, 2.8, 3.2)}
</g>'''


def projection_scene(x, y, scale=1):
    """Local screen 0,0..100,68; presenter beam originates at 145,92.

    Insert before the presenter PNG. The beam stops at 4.9s; the completed
    screen stays through its folded-corner ending at 5.7s of a 7s loop.
    """
    blocks = ''.join(f'''<rect x="{12+i*26}" y="20" width="18" height="22" fill="{AMBER}" opacity="0">{_opacity(3+i*.2, 5.7, 7)}</rect>''' for i in range(3))
    return f'''<g class="moving" aria-hidden="true" pointer-events="none" transform="translate({x:g} {y:g}) scale({scale:g})">
<path d="M145 92L100 0V68Z" fill="{MINT}" opacity="0">{_opacity(2.8, 4.9, 7, .18)}</path>
<g opacity="0">{_opacity(2.8, 5.7, 7)}
<rect width="100" height="68" fill="#f0ebe1" stroke="{INK}" stroke-width="2"/>
<rect x="8" y="8" width="84" height="4" fill="{INK}" opacity=".25"/>
{blocks}<path d="M12 53H88" stroke="{INK}" stroke-width="2" opacity=".2"/>
<rect x="9" y="16" width="82" height="3" fill="{MINT}" opacity="0">{_opacity(3.4, 4.6, 7)}
<animate attributeName="y" values="16;16;57;57" keyTimes="0;.48571429;.65714286;1" dur="7s" repeatCount="indefinite"/>
</rect></g></g>'''


def workflow_icon_action(x, y, phase):
    """Add around a base icon center; phases 0 Record, 1 Edit, 2 Replay."""
    if phase == 0:
        shape = f'''<circle r="12" fill="none" stroke="{AMBER}" stroke-width="2.5"><animate attributeName="r" values="10;14;10;10" keyTimes="0;.05;.10;1" dur="8s" repeatCount="indefinite"/></circle>'''
    elif phase == 1:
        shape = f'''<path d="M-9 10H9" fill="none" stroke="{AMBER}" stroke-width="3" stroke-dasharray="18" stroke-dashoffset="18"><animate attributeName="stroke-dashoffset" values="18;18;0;0" keyTimes="0;.1375;.2875;1" dur="8s" repeatCount="indefinite"/></path>'''
    elif phase == 2:
        shape = f'''<g><animateTransform attributeName="transform" type="rotate" values="0;0;180;180" keyTimes="0;.35;.5375;1" dur="8s" repeatCount="indefinite"/><path d="M-11 0A11 11 0 1 1 8 8M8 8V2M8 8H2" fill="none" stroke="{AMBER}" stroke-width="2.5"/></g>'''
    else:
        raise ValueError('workflow phase must be 0, 1, or 2')
    start, length = ((0, .8), (1.1, 1.2), (2.8, 1.5))[phase]
    return f'''<g class="moving" aria-hidden="true" pointer-events="none" transform="translate({x:g} {y:g})" opacity="0">{_opacity(start, start+length, 8)}{shape}</g>'''


def bar_glint(x, y, width, height):
    """An ink sweep clipped by a nested viewport; never changes data width."""
    stripe = min(12, max(2, width*.12))
    return f'''<svg class="moving" aria-hidden="true" pointer-events="none" x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" viewBox="0 0 {width:g} {height:g}" overflow="hidden">
<rect x="{-stripe:g}" width="{stripe:g}" height="{height:g}" fill="{INK}" opacity="0">{_opacity(.01, 2, 10, .18)}
<animate attributeName="x" values="{-stripe:g};{width:g};{width:g}" keyTimes="0;.2;1" dur="10s" repeatCount="indefinite"/>
</rect></svg>'''


def bridge_ending(x, y, scale=1):
    """A small checked reply bubble, 3.4..4.2s of the 6.8s dialogue.

    x/y is the bubble's top-left corner; bounds are 30 by 27 local units.
    """
    return f'''<g class="moving" aria-hidden="true" pointer-events="none" transform="translate({x:g} {y:g}) scale({scale:g})" opacity="0">
{_opacity(3.4, 4.2, 6.8)}
<path d="M0 0H30V21H13L7 27V21H0Z" fill="#f0ebe1" stroke="{INK}" stroke-width="2"/>
<path d="M8 10L13 15L23 6" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="miter"/>
</g>'''


def slide_ending(x, y, scale=1):
    """A completed slide's folded corner, 5.0..5.7s of the 7s reading loop.

    x/y and scale match projection_scene; cue occupies its upper-right corner.
    """
    return f'''<g class="moving" aria-hidden="true" pointer-events="none" transform="translate({x:g} {y:g}) scale({scale:g})" opacity="0">
{_opacity(5, 5.7, 7)}
<path d="M70 0H92L100 8V28H70Z" fill="#f0ebe1" stroke="{INK}" stroke-width="2"/>
<path d="M92 0V8H100" fill="{AMBER}" stroke="{INK}" stroke-width="2"/>
<path d="M76 15H88M76 20H91" fill="none" stroke="{INK}" stroke-width="2" opacity=".55"/>
<rect x="93" y="19" width="5" height="5" fill="{AMBER}"/>
</g>'''


def automation_ending(x, y, scale=1):
    """A drawn check and three pixel sparks, 4.6..5.6s of an 8s loop.

    x/y centers the check; all geometry stays within a 40-by-32 local box.
    """
    sparks = ''.join(f'''<rect x="{px}" y="{py}" width="3" height="3" fill="{color}" opacity="0">{_opacity(start, 5.6, 8)}
<animateTransform attributeName="transform" type="translate" values="0 0;0 0;{dx} {dy};{dx} {dy}" keyTimes="0;.625;.675;1" dur="8s" repeatCount="indefinite"/></rect>'''
                      for px, py, dx, dy, color, start in
                      ((-14, -8, -3, -3, MINT, 5.0),
                       (8, -13, 2, -3, AMBER, 5.08),
                       (14, 3, 3, 1, MINT, 5.16)))
    return f'''<g class="moving" aria-hidden="true" pointer-events="none" transform="translate({x:g} {y:g}) scale({scale:g})" opacity="0">
{_opacity(4.6, 5.6, 8)}
<path d="M-10 1L-3 8L10-7" fill="none" stroke="{MINT}" stroke-width="3" stroke-linejoin="miter" stroke-dasharray="32" stroke-dashoffset="32">
<animate attributeName="stroke-dashoffset" values="32;32;0;0" keyTimes="0;.575;.625;1" dur="8s" repeatCount="indefinite"/>
</path>{sparks}</g>'''
