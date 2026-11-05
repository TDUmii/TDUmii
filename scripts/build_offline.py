"""Build one private HTML file from the same finished profile page."""
from pathlib import Path
import base64
import json
import re

ROOT = Path(__file__).resolve().parents[1]
MIME = {'gif': 'image/gif', 'png': 'image/png', 'svg': 'image/svg+xml', 'woff2': 'font/woff2'}
assets = {}
for path in (ROOT / 'assets').iterdir():
    ext = path.suffix.removeprefix('.')
    if ext in MIME:
        assets['assets/' + path.name] = 'data:' + MIME[ext] + ';base64,' + base64.b64encode(path.read_bytes()).decode()
html = (ROOT / 'index.html').read_text(encoding='utf-8')
css = (ROOT / 'styles.css').read_text(encoding='utf-8')
css = re.sub(r"url\('([^']+)'\)", lambda match: "url('" + assets.get(match[1], match[1]) + "')", css)
html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>' + css + '</style>')
html = re.sub(r'(src|srcset|href)="(assets/[^" ]+)"', lambda match: match[1] + '="' + assets.get(match[2], match[2]) + '"', html)
data = (ROOT / 'assets/profile-data.js').read_text(encoding='utf-8')
html = html.replace('<script src="assets/profile-data.js"></script>', '<script>' + data + '</script>')
code = 'window.UMI_ASSETS=' + json.dumps(assets).replace('<', '\\u003c') + ';\n' + (ROOT / 'profile.js').read_text(encoding='utf-8')
html = html.replace('<script src="profile.js"></script>', '<script>' + code + '</script>')
out = ROOT / 'output'
out.mkdir(exist_ok=True)
(out / 'Umi-Profile.html').write_text(html, encoding='utf-8')
print('Standalone profile built with the original animated GIF and real public activity.')
