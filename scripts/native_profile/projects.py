"""Three independently linked project scenes for GitHub's native two-cell layout."""
from .core import BG, GOLD, INK, MINT, arrow, image_asset, rect, text, write
from .ornaments import conveyor_pixels, packet_burst, paper_glint, star, workflow_marker


def scene_shelf(width, y, color=INK):
    return f'<path d="M16 {y}H{width-28}v6h12v8H28v-6H16Z" fill="{color}"/>'


def project_panel(slug, mobile):
    bridge = slug == 'bridge'
    width, height = (250, 370) if mobile else (500, 414)
    body = rect(0, 0, width, height, MINT if bridge else BG, 0)
    if bridge:
        body += f'<path d="M{width-33} 0v17h17v17h16V0Z" fill="{BG}"/>'
    else:
        body += f'<path d="M1 17h27L42 1H{width-1}V{height-1}H1Z" fill="none" stroke="{INK}" stroke-width="2"/>'
    body += arrow(width-45, 30, size=23)
    title = 'UmiBridge' if bridge else 'QuietShare'
    body += text(17 if mobile else 25, 58 if mobile else 72, title, 33 if mobile else 49, INK, 800)
    if mobile:
        descriptions = ['ChatGPT meets', 'Windows.'] if bridge else ['Presentations', '& notes.']
        for i, line in enumerate(descriptions):
            body += text(17, 94+i*32, line, 28, INK, 500)
        art_x, art_y, art_w, art_h, shelf_y, footer_y = 7, 135, 236, 151, 268 if bridge else 282, 313
    else:
        body += text(25, 109, 'ChatGPT meets Windows.' if bridge else 'Presentations & notes.', 22, INK, 500)
        art_x, art_y, art_w, art_h, shelf_y, footer_y = 24, 132, 452, 246, 360, 393
    body += scene_shelf(width, shelf_y)
    if bridge:
        path = 'M79 204V178H134V168H162' if mobile else 'M167 243V207H268V189H327'
        body += packet_burst(path, size=7)
        body += star(39 if mobile else 77, 160 if mobile else 177, 9 if mobile else 13, INK, period=5.4, offset=1.2)
    body += image_asset('c1-bridge-art.png' if bridge else 'c1-quiet-art.png', art_x, art_y, art_w, art_h, True)
    if not bridge:
        body += paper_glint(155 if mobile else 295, 207 if mobile else 251, .8 if mobile else 1.15)
    body += f'<path d="M17 {footer_y-19}H{width-17}" stroke="{INK}" stroke-width="1"/>'
    if mobile:
        lines = ['Local dashboard', 'One-click setup'] if bridge else ['Optional offline', 'transcription']
        for i, line in enumerate(lines):
            body += text(17, footer_y+5+i*28, line, 25, INK, 500)
    else:
        body += text(25, footer_y, 'Local dashboard / One-click setup' if bridge else 'Optional offline transcription', 18, INK, 500)
    return width, height, body


def workflow(x, y, mobile):
    """A compact process legend, not controls or a running-job counter."""
    step = 122 if mobile else 112
    body = ''
    for i, name in enumerate(['Record', 'Edit', 'Replay']):
        px = x+i*step
        body += workflow_marker(px, y+45, 70 if mobile else 61, i)
        body += text(px, y+36, name, 20 if mobile else 19, BG, 500)
        if i == 0:
            body += f'<circle cx="{px+10}" cy="{y}" r="8" fill="{GOLD}"/>'
        elif i == 1:
            body += f'<path d="M{px+1} {y+8}l2-8 12-12 6 6-12 12Z" fill="{MINT}"/>'
        else:
            body += f'<path d="M{px} {y-10}l20 10-20 10Z" fill="{GOLD}"/>'
        if i < 2:
            body += f'<path d="M{px+34} {y}h{step-52}" stroke="#52636b" stroke-width="2"/>'
    return body


def render(data):
    for mobile in (False, True):
        for slug in ['bridge', 'quietshare']:
            width, height, body = project_panel(slug, mobile)
            write('project-row-'+slug+('-mobile' if mobile else '')+'.svg', width, height, body,
                  ('UmiBridge. ChatGPT meets Windows.' if slug == 'bridge' else 'QuietShare. Presentations, notes and optional offline transcription.')+' Open repository.')
        width, height = (500, 360) if mobile else (1000, 270)
        body = rect(0, 0, width, height, INK, 0)
        if mobile:
            body += text(22, 52, 'Background', 40, BG, 800)
            body += text(22, 97, 'Automation Studio', 38, BG, 800)
            body += workflow(25, 144, True)
            body += image_asset('c1-automation-art.png', 230, 178, 263, 169, True)
            body += text(25, 252, 'Windows', 23, MINT, 500)+text(25, 282, 'workflows.', 23, MINT, 500)
            body += arrow(27, 324, BG, 30)
        else:
            for i, line in enumerate(['Background', 'Automation', 'Studio']):
                body += text(25, 61+i*55, line, 50, BG, 800)
            body += workflow(448, 85, False)
            body += text(448, 178, 'Windows workflows.', 22, MINT, 500)
            body += arrow(450, 216, BG)
            body += image_asset('c1-automation-art.png', 735, 36, 260, 210, True)
        body += f'<path d="M{180 if mobile else 400} {height}l22-22H{width}v22Z" fill="{GOLD}"/>'
        body += conveyor_pixels(249 if mobile else 468, height-13, 80 if mobile else 174)
        write('project-row-automation'+('-mobile' if mobile else '')+'.svg', width, height, body,
              'Background Automation Studio. Record, edit and replay Windows workflows. Open repository.')

