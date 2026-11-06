"""GitHub-native activity section."""
from datetime import date
from .core import INK, MUTED, commit_orbit, pixel, text, write


def render(data):
    days = data['contributions']
    start = date.fromisoformat(days[0]['date'])
    cells, months = '', set()
    palette = ['#dedfd2', '#8cab7a', '#5e874f', '#355f35', '#153e27']
    for day in days:
        current = date.fromisoformat(day['date'])
        column, row = divmod((current-start).days, 7)
        x, y = 32 + column * 17.8, 101 + row * 14.2
        cells += f'<rect x="{x:.1f}" y="{y:.1f}" width="12" height="11" rx="2" fill="{palette[day["level"]]}"><title>{current.isoformat()}: {day["count"]} contributions</title></rect>'
        month = (current.year, current.month)
        if month not in months:
            cells += text(x, 84, current.strftime('%b'), 11, MUTED)
            months.add(month)
    sweep = commit_orbit(days, start, 32, 101, 17.8, 14.2, 943)
    calendar_body = '<g transform="translate(0,-64)">' + cells + sweep + '</g>'
    write('calendar.svg', 1000, 170, calendar_body, 'Real public GitHub calendar; a decorative comet highlights only active dates')
    write('calendar-static.svg', 1000, 170, '<g transform="translate(0,-64)">' + cells + '</g>', 'Real public GitHub calendar, static reduced-motion edition')
    # Header flame keeps the original 15:20 GIF ratio at a visible 2x size.
    activity = pixel('pixel-flame', 28, 43, 30, 40)
    activity += text(72, 76, 'Commit orbit', 32, INK, 700)
    activity += text(733, 49, data['contribution_total'], 35, INK, 700)
    activity += text(733, 73, 'contributions in this snapshot', 12, MUTED)
    # Move the exact original calendar and active-cell orbit together.
    activity += '<g transform="translate(0,30)">' + cells + sweep + '</g>'
    activity += '<path d="M28 245h944" stroke="' + INK + '"/>'
    metrics = [(data['active_days'], 'Active days', 'Days with public contributions'),
               (data['recent_contributions'], 'Last 30 days', 'Contributions in the recent window'),
               (data['best_day'], 'Peak day', 'Most contributions on one date')]
    for i, (value, label, note) in enumerate(metrics):
        x = 29 + i * 320
        activity += text(x, 272, label.upper(), 11, MUTED, 600)
        activity += text(x, 312, value, 33, INK, 700)
        if i < 2:
            activity += f'<path d="M{x+295} 265v73" stroke="#ccd0c1"/>'
    activity += text(29, 372, f"PUBLIC GITHUB / {data['date_label']}", 11, MUTED, 500)
    write('activity.svg', 1000, 394, activity, 'Real public GitHub calendar and dated activity summary')

    recent_days = days[-182:]
    recent_start = date.fromisoformat(recent_days[0]['date'])
    mc = pixel('pixel-flame', 22, 42, 30, 40)
    mc += text(68, 75, 'Commit orbit', 31, INK, 700)
    mc += text(23, 112, 'Latest 26 weeks', 18, MUTED)
    month_seen = set()
    for day in recent_days:
        current = date.fromisoformat(day['date'])
        column, row = divmod((current - recent_start).days, 7)
        x, y = 26 + column * 17.3, 153 + row * 15.5
        mc += f'<rect x="{x:.1f}" y="{y:.1f}" width="12" height="12" rx="2" fill="{palette[day["level"]]}"><title>{current.isoformat()}: {day["count"]} contributions</title></rect>'
        if (current.year, current.month) not in month_seen:
            mc += text(x, 140, current.strftime('%b'), 12, MUTED)
            month_seen.add((current.year, current.month))
    mc += commit_orbit(recent_days, recent_start, 26, 153, 17.3, 15.5, 445, 12, 12)
    mc += '<path d="M22 271h456" stroke="' + INK + '"/>'
    mc += text(22, 312, data['contribution_total'], 36, INK, 700)
    mc += text(132, 309, 'contributions / full snapshot', 17, MUTED)
    for i, (value, label, _) in enumerate(metrics):
        x = 22 + i * 159
        mc += text(x, 356, value, 27, INK, 700)
        mc += text(x, 380, label, 14, MUTED)
    mc += text(22, 421, 'PUBLIC GITHUB / ' + data['date_label'], 13, MUTED)
    write('activity-mobile.svg', 500, 444, mc, 'Latest 26 weeks of real public contributions, with full-snapshot totals and dated summary')
