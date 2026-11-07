"""GitHub-native details section."""
from .core import BG, BLUE, GOLD, INK, MINT, MUTED, arrow, image_asset, rect, text, write
from .ornaments import bar_glint


def footer_companion(x):
    """The original toy robot takes a short sideways step, then rests."""
    live = image_asset('pixel-robot.gif', x, 2, 42, 42)
    still = image_asset('pixel-robot-still.png', x, 2, 42, 42).replace('class=""', 'class="nyan-still"')
    return f'''<g class="nyan-live"><animateTransform attributeName="transform" type="translate" values="0 0;0 0;-7 0;-7 3;0 0;0 0" keyTimes="0;.15;.32;.48;.64;1" dur="11s" repeatCount="indefinite"/>{live}</g>{still}'''


def render(data):
    counts = sorted(data['language_counts'].items(), key=lambda item: (-item[1], item[0]))
    total = sum(count for _, count in counts)
    colors = [MINT, GOLD, BLUE, '#d3d4bf', '#b3c89f', '#b4b8b0']
    for mobile in (False, True):
        w, h = (500, 350) if mobile else (1000, 248)
        tools = text(22, 55, 'Toolkit', 32, INK, 700)
        tools += text(22, 99, 'Primary language per public repository', 21 if mobile else 15, MUTED)
        x = 22
        for i, (name, count) in enumerate(counts):
            bar_width = (w-44) * count / total if total else 0
            tools += rect(round(x, 2), 142, round(bar_width, 2), 14, colors[i % len(colors)], 0)
            x += bar_width
            col, row = (i % 2, i // 2) if mobile else (i % 3, i // 3)
            tx, ty = 22 + col * (240 if mobile else 326), 193 + row * (46 if mobile else 26)
            tools += rect(tx, ty-12, 10, 10, colors[i % len(colors)], 0, INK)
            tools += text(tx+20, ty, name, 21 if mobile else 17, INK, 500)
            tools += text(tx+(206 if mobile else 280), ty, count, 21 if mobile else 17, INK, 700)
        tools += bar_glint(22, 142, w-44, 14)
        if mobile:
            tools += text(22, 330, f'{total} repositories / {len(counts)} primary languages', 17, MUTED)
        write('toolkit-compact'+('-mobile' if mobile else '')+'.svg', w, h, tools, 'Primary language per public repository, not a proficiency score')
    for slug, label in [('lab', 'Read the code'), ('code', 'All repositories')]:
        for mobile in (False, True):
            w, h = (250, 94) if mobile else (500, 56)
            fill = MINT if slug == 'lab' else BG
            body = rect(1, 1, w-2, h-2, fill, 0, INK)
            caption = 'Source code' if mobile and slug == 'lab' else ('Repositories' if mobile else label)
            body += text(17, 56 if mobile else 35, caption, 26 if mobile else 21, INK, 600)
            body += arrow(w-39, 49 if mobile else 28, size=20)
            write('footer-'+slug+('-mobile' if mobile else '')+'.svg', w, h, body, label)
    for mobile in (False, True):
        w, h = (500, 90) if mobile else (1000, 56)
        credit = text(22, 33, 'Nyan Cat via GIPHY', 19 if mobile else 15, INK)
        update = 'Updated '+data['updated_label'] if data.get('updated_label') else 'Public snapshot / '+data['date_label']
        credit += text(22 if mobile else 595, 70 if mobile else 33, update, 17 if mobile else 14, MUTED)
        credit += footer_companion(w-55)
        write('footer-credit'+('-mobile' if mobile else '')+'.svg', w, h, credit, 'Original Nyan Cat via GIPHY. '+update)

