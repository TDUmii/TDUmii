"""Related 32-unit pixel maker seals, derived from the hero's T/D geometry.

Pure vector output, no fonts, IDs, raster assets, or animation dependencies.
"""
from .core import GOLD, INK, MINT


def maker_mark(kind, x, y, size=24):
    """Place a stepped TD seal; kind is bridge, quietshare, or automation.

    x/y is the top-left corner, size the square footprint. A shared stepped
    housing and compact T/D signature unite three distinct tool pictograms.
    """
    if kind == 'bridge':
        pictogram = f'''<path d="M7 5H10V7H12V9H14V11H12V13H10V15H7V12H9V10H7Z" fill="{MINT}"/>
<path d="M17 12H25V15H17Z" fill="{GOLD}"/>'''
    elif kind == 'quietshare':
        pictogram = f'''<path d="M9 4H20L25 9V17H9Z" fill="{MINT}"/>
<path d="M20 4V9H25Z" fill="{GOLD}"/>
<path d="M12 10H18V12H12ZM12 14H22V16H12Z" fill="{INK}"/>'''
    elif kind == 'automation':
        pictogram = f'''<path d="M8 10V7H11V5H21V7H24V5H27V13H19V10H22V9H20V8H12V10Z" fill="{MINT}"/>
<path d="M24 13V16H21V18H11V16H8V18H5V10H13V13H10V14H12V15H20V13Z" fill="{GOLD}"/>'''
    else:
        raise ValueError('maker mark kind must be bridge, quietshare, or automation')
    return f'''<g aria-hidden="true" pointer-events="none" transform="translate({x:g} {y:g}) scale({size/32:g})" shape-rendering="crispEdges">
<path d="M4 0H28V4H32V28H28V32H4V28H0V4H4Z" fill="{INK}"/>
{pictogram}
<path d="M5 21H15V24H12V29H9V24H5Z" fill="{MINT}"/>
<path d="M18 21H24V23H27V27H24V29H18V26H22V25H24V24H22V23H18Z" fill="{MINT}"/>
<path d="M28 19H30V21H28Z" fill="{GOLD}"/>
</g>'''
