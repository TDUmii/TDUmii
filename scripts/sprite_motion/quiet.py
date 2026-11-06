"""Approved Quiet sprite rig and animation timing."""
from .core import blink, build


def reading_page():
    # The binding is the short cream-paper junction, not the tall amber spine.
    # A lifted leaf sits above the covers; the source covers are restored in front.
    # Bowed long edges flex; the short straight edge keeps paper corners crisp.
    # No perimeter stroke: an outlined straight sliver reads as a rigid pointer.
    poses = [
        'C866 557 912 534 950 530L968 540C926 546 875 566 848 580',
        'C858 550 906 518 943 525L950 540C909 545 872 567 848 580',
        'C844 547 867 516 889 516L895 532C876 548 859 567 848 580',
        'C824 550 818 527 830 514L849 518C858 539 854 559 848 580',
        'C813 550 774 516 754 519L748 533C779 549 817 568 848 580',
        'C806 551 753 528 716 532L713 543C752 548 806 567 848 580',
    ]
    shapes = ['M832 569' + poses[i] + 'Z' for i in [0, 0, 1, 2, 3, 4, 5, 5, 5]]
    times = '0;.22;.245;.28;.31;.34;.38;.40;1'
    return f'''<g class="reading-leaf" opacity="0">
<animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.22;.40;1" calcMode="discrete" dur="7s" repeatCount="indefinite"/>
<path d="{shapes[0]}" fill="#faecd2">
<animate attributeName="d" values="{';'.join(shapes)}" keyTimes="{times}" dur="7s" repeatCount="indefinite"/>
<animate attributeName="fill" values="#faecd2;#faecd2;#f2e3c8;#fff0d4;#fff0d4" keyTimes="0;.25;.31;.35;1" dur="7s" repeatCount="indefinite"/>
</path></g><use xlink:href="#PREFIXsource" clip-path="url(#PREFIXbook-covers)"/>'''


def build_sprite():
    quiet_eyes = '<rect x="915" y="345" width="86" height="53"/><rect x="1034" y="345" width="85" height="53"/>'
    book_covers = '<path d="M697 548H766V560H799V572H829V581L840 621H721Z M849 581H861V574H889V560H913V554H944V546L975 539L998 621H860Z M829 581H849L861 621H840Z"/>'
    return build('quiet', {'eyes': quiet_eyes, 'book-covers': book_covers}, '',
        blink(quiet_eyes, 381, '3.8s') +
        reading_page() +
        (
            '<rect x="1084" y="172" width="28" height="22" fill="#ff9b8f" opacity="0">'
            '<animate attributeName="opacity" values="0;0;.70;0;0" keyTimes="0;.40;.44;.50;1" dur="7s" repeatCount="indefinite"/>'
            '</rect>'
        ), 7)
