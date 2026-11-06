"""Small independent boundary/denominator check: python scripts/test_profile_metrics.py."""
from datetime import date, timedelta
from profile_metrics import analyze


start = date(2025, 11, 2)
days = [{'date': (start + timedelta(days=i)).isoformat(), 'count': i % 8} for i in range(370)]
data = {'date': days[-1]['date'], 'contributions': days,
        'contribution_total': sum(range(8)) * 46 + sum(range(2)), 'projects': [], 'repo_summary': {}}
metrics = analyze(data)
assert metrics['monthly'][0]['observed_days'] == 29
assert metrics['monthly'][-1]['observed_days'] == 6
assert metrics['monthly'][0]['partial'] and metrics['monthly'][-1]['partial']
assert all(not row['partial'] for row in metrics['monthly'][1:-1])
for index, row in enumerate(metrics['weekday']):
    counts = [day['count'] for day in days if date.fromisoformat(day['date']).weekday() == index]
    assert row['observed_days'] == len(counts) and row['mean'] == sum(counts) / len(counts)
assert sum(row['total'] for row in metrics['monthly']) == data['contribution_total']
assert metrics['activity']['quiet_days'] == 47
assert metrics['activity']['active_days'] + metrics['activity']['quiet_days'] == 370
try:
    analyze({**data, 'contributions': days[:30] + days[31:]})
except ValueError:
    pass
else:
    raise AssertionError('Missing calendar date accepted')
print('Metrics boundaries, zero counts, weekday denominators and reconciliation passed')
