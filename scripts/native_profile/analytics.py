"""Contribution rhythm and a bounded comparison of the three featured projects."""
from math import ceil
from profile_metrics import analyze
from .core import BG, INK, MUTED, MINT, GOLD, text, rect, write


def motion():
    return '''<style>.peak{animation:peak 3s ease-in-out infinite}.glint{animation:glint 6s linear infinite;transform-box:fill-box;transform-origin:center}@keyframes peak{0%,100%{opacity:.35}50%{opacity:1}}@keyframes glint{to{stroke-dashoffset:-180}}@media(prefers-reduced-motion:reduce){.peak,.glint{animation:none}.moving{display:none}}</style>'''


def ornament(x, y, width):
    return f'''<g class="moving" aria-hidden="true"><g><animateTransform attributeName="transform" type="translate" values="{x} {y};{x+width} {y}" dur="12s" repeatCount="indefinite"/><path d="M-5 0h10M0-5v10" stroke="{INK}" stroke-width="2"/><path d="M-24 0h10M-36 0h6" stroke="{GOLD}" stroke-width="3"/></g></g>'''


def monthly(items, x, y, w, h, mobile):
    fs = 22 if mobile else 16
    title = text(x, y, 'Monthly contributions', 26 if mobile else 23, INK, 600)
    top, bottom = y + 53, y + h - 48
    left = x + (65 if mobile else 52)
    plotw = w - (78 if mobile else 65)
    maximum = max((m['total'] for m in items), default=0)
    ceiling = max(1, ceil(maximum / 100) * 100)
    for value in (0, ceiling // 2, ceiling):
        yy = bottom - (bottom-top) * value / ceiling
        title += f'<path d="M{left} {yy}h{plotw}" stroke="{INK}" opacity=".15"/>'
        title += text(x, yy+6, value, fs-2, MUTED)
    pitch = plotw / len(items)
    for i, m in enumerate(items):
        cx = left + pitch*(i+.5)
        bh = (bottom-top)*m['total']/ceiling
        title += f'<g><title>{m["month"]}: {m["total"]} contributions across {m["observed_days"]} observed days' + ('; partial month' if m['partial'] else '') + '</title>'
        title += rect(round(cx-pitch*.32,2), round(bottom-bh,2), round(pitch*.64,2), round(bh,2), GOLD if m['total']==maximum else MINT, 3, INK)
        title += f'<text x="{cx}" y="{bottom-bh-10}" text-anchor="middle" font-size="{fs-2}" fill="{INK}">{m["total"]}</text>'
        label = m['label'][:3] + ('*' if m['partial'] else '')
        title += f'<text x="{cx}" y="{bottom+29}" text-anchor="middle" font-size="{fs}" fill="{INK}">{label}</text></g>'
        if maximum > 0 and m['total'] == maximum:
            title += f'<circle class="peak" cx="{cx}" cy="{bottom-bh+8}" r="4" fill="{INK}"/>'
    return title


def weekday(items, x, y, w, mobile):
    fs = 23 if mobile else 17
    body = text(x, y, 'Weekday rhythm', 26 if mobile else 23, INK, 600)
    body += text(x, y+34, 'Average contributions per observed day', 21 if mobile else 15, MUTED)
    maximum = max((r['mean'] for r in items), default=0) or 1
    trackx, trackw = x+65, w-125
    for i, row in enumerate(items):
        yy = y+78+i*(43 if mobile else 34)
        end = trackx+trackw*row['mean']/maximum
        body += text(x, yy+7, row['label'][:3], fs, INK, 500)
        body += f'<path d="M{trackx} {yy}h{trackw}" stroke="{INK}" opacity=".12"/><g><title>{row["label"]}: {row["total"]} contributions / {row["observed_days"]} observed days = {row["mean"]:.1f}</title><path d="M{trackx} {yy}H{end}" stroke="{INK}" stroke-width="3"/><circle cx="{end}" cy="{yy}" r="6" fill="{GOLD}" stroke="{INK}"/></g>'
        body += f'''<g class="moving" opacity="0"><circle cx="{end}" cy="{yy}" r="8" fill="none" stroke="{INK}" stroke-width="1.5"/>
<animate attributeName="opacity" values="0;.8;.8;0;0" keyTimes="0;.025;.065;.09;1" dur="10.5s" begin="{i*1.2}s" repeatCount="indefinite"/></g>'''
        body += text(x+w-48, yy+7, f'{row["mean"]:.1f}', fs, INK, 600)
    return body + text(trackx-5, y+78+7*(43 if mobile else 34), '0', fs-2, MUTED)


def donut(activity, period, x, y, mobile):
    r = 70 if mobile else 62
    circumference = 2*3.141592653589793*r
    active = circumference*activity['active_share']
    body = f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{INK}" stroke-opacity=".13" stroke-width="20"/>'
    body += f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{INK}" stroke-width="20" stroke-dasharray="{active} {circumference-active}" transform="rotate(-90 {x} {y})"/>'
    body += f'<defs><mask id="active-ring"><circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="white" stroke-width="20" stroke-dasharray="{active} {circumference-active}" transform="rotate(-90 {x} {y})"/></mask></defs><circle class="glint" mask="url(#active-ring)" cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{GOLD}" stroke-width="20" stroke-dasharray="8 172"/>'
    body += f'<text x="{x}" y="{y+8}" text-anchor="middle" font-size="28" font-weight="700" fill="{INK}">{activity["active_share"]:.1%}</text>'
    return body


def render(data):
    metrics = analyze(data)
    p, a = metrics['period'], metrics['activity']
    for mobile in (False, True):
        w, suffix = (500, '-mobile') if mobile else (1000, '')
        months = metrics['monthly'][-6:] if mobile else metrics['monthly']
        body = motion() + text(26, 46, 'A rhythm of building', 28 if mobile else 30, INK, 700)
        body += text(26, 81, f'{p["start"]} to {p["end"]}', 22 if mobile else 17, MUTED)
        body += ornament(w-(86 if mobile else 160), 40, 60 if mobile else 100)
        body += monthly(months, 26, 139, 448 if mobile else 565, 320, mobile)
        if mobile:
            body += text(26, 478, f'Shown: {months[0]["month"]} to {months[-1]["month"]}', 21, MUTED)
            body += text(26, 510, '* Partial observed month', 21, MUTED)
            body += weekday(metrics['weekday'], 26, 578, 448, True)
            height = 1010
        else:
            body += weekday(metrics['weekday'], 623, 139, 351, False)
            body += text(26, 480, '* Partial month; totals cover observed dates only.', 16, MUTED)
            height = 515
        write('insights-rhythm'+suffix+'.svg', w, height, body, 'Monthly public contributions and average contributions per observed weekday')

        body = motion()+text(26, 46, 'Projects in the open', 28 if mobile else 30, INK, 700)
        body += text(26, 81, f'3 featured / {data["public_repos"]} public repositories', 22 if mobile else 17, MUTED)
        projects = metrics['projects']
        if mobile:
            for i, repo in enumerate(projects):
                yy = 133+i*153
                name = 'BackgroundAutomationStudio' if repo['name']=='BackgroundAutomationStudio' else repo['name']
                # Long repository name stays whole and readable on its own line.
                if name == 'BackgroundAutomationStudio':
                    body += text(26, yy, 'Background', 25, INK, 600)+text(26, yy+29, 'AutomationStudio', 25, INK, 600)
                    yy += 29
                else:
                    body += text(26, yy, name, 25, INK, 600)
                body += text(26, yy+34, f'{repo["language"] or "Unspecified"}  /  {repo["stars"]} stars  /  {repo["forks"]} forks', 22, MUTED)
                body += text(26, yy+66, 'Last push '+(repo['pushed_at'] or 'unavailable')[:10]+' (UTC)', 21, MUTED)
                body += f'<path d="M26 {yy+84}h448" stroke="{INK}" opacity=".2"/>'
            cy = 713
            body += text(26, 652, 'Contribution days', 25, INK, 600)
            body += donut(a,p,116,cy+45,True)
            body += text(221, cy+10, f'{a["active_days"]} active', 25, INK, 600)
            body += text(221, cy+48, f'{a["quiet_days"]} quiet', 25, INK, 600)
            body += text(26, 879, f'Of {p["observed_days"]} observed dates', 23, INK, 500)
            body += text(26, 916, 'Quiet = no displayed contributions', 21, MUTED)
            height = 954
        else:
            for xx, label in [(26,'Repository'),(435,'Language'),(618,'Stars'),(710,'Forks'),(812,'Last push (UTC)')]:
                body += text(xx, 137, label, 17, MUTED, 600)
            for i, repo in enumerate(projects):
                yy = 185+i*59
                body += text(26,yy,repo['name'],20,INK,600)
                for xx,value in [(435,repo['language'] or 'Unspecified'),(618,repo['stars']),(710,repo['forks']),(812,(repo['pushed_at'] or 'unavailable')[:10])]:
                    body += text(xx, yy, value, 18, INK)
                body += f'<path d="M26 {yy+19}h948" stroke="{INK}" opacity=".18"/>'
            body += donut(a,p,110,425,False)
            body += text(213,388,'Contribution days',25,INK,600)
            body += text(213,426,f'{a["active_days"]} active / {a["quiet_days"]} quiet',23,INK,600)
            body += text(213,460,f'Of {p["observed_days"]} observed dates. Quiet = no displayed contributions.',17,MUTED)
            height = 525
        write('insights-projects'+suffix+'.svg',w,height,body,'Three featured public repositories and the share of observed dates with public contributions')
