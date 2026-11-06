"""Derived public contribution metrics. Counts are contributions, never commits."""
from calendar import monthrange
from datetime import date, timedelta


def analyze(data):
    days = data['contributions']
    dates = [date.fromisoformat(day['date']) for day in days]
    if len(days) < 350 or dates != [dates[0] + timedelta(days=i) for i in range(len(days))]:
        raise ValueError('Expected at least 350 continuous, ordered contribution dates')
    if any(type(day['count']) is not int or day['count'] < 0 for day in days):
        raise ValueError('Contribution counts must be nonnegative integers')
    if dates[-1] > date.fromisoformat(data['date']):
        raise ValueError('Contribution dates extend beyond snapshot')
    monthly = {}
    weekday = [{'weekday': i, 'label': name, 'total': 0, 'observed_days': 0}
               for i, name in enumerate(('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'))]
    for day, observed in zip(days, dates):
        key = observed.strftime('%Y-%m')
        bucket = monthly.setdefault(key, {'month': key, 'label': observed.strftime('%b %Y'), 'total': 0, 'observed_days': 0})
        bucket['total'] += day['count']
        bucket['observed_days'] += 1
        weekday[observed.weekday()]['total'] += day['count']
        weekday[observed.weekday()]['observed_days'] += 1
    for key, bucket in monthly.items():
        year, month = map(int, key.split('-'))
        bucket['partial'] = bucket['observed_days'] != monthrange(year, month)[1]
    for bucket in weekday:
        bucket['mean'] = bucket['total'] / bucket['observed_days']
    total = sum(day['count'] for day in days)
    if total != data['contribution_total'] or total != sum(x['total'] for x in monthly.values()) or total != sum(x['total'] for x in weekday):
        raise ValueError('Contribution totals do not reconcile')
    active = sum(day['count'] > 0 for day in days)
    return {
        'period': {'start': dates[0].isoformat(), 'end': dates[-1].isoformat(), 'observed_days': len(days)},
        'contribution_total': total, 'monthly': list(monthly.values()), 'weekday': weekday,
        'activity': {'active_days': active, 'quiet_days': len(days) - active,
                     'active_share': active / len(days), 'quiet_share': (len(days) - active) / len(days)},
        'projects': [{'name': p['name'], 'language': p['language'], 'stars': p['stargazers_count'],
                      'forks': p['forks_count'], 'pushed_at': p['pushed_at'], 'archived': p['archived'],
                      'url': p['html_url']} for p in data['projects']],
        'repo_summary': data['repo_summary'],
    }
