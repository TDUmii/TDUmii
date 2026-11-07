"""Validate a public snapshot, then publish assets and an immutable README together."""
from pathlib import Path
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ('assets/*.svg', 'assets/profile-data.json', 'assets/profile-data.js', 'index.html')
CHECKS = ('scripts/test_profile_metrics.py', 'scripts/native_profile/check.py', 'scripts/check_assets.py')


def git(root, *args):
    return subprocess.run(['git', *args], cwd=root, check=True, text=True,
                          stdout=subprocess.PIPE).stdout.strip()


def command(root, *args):
    subprocess.run([sys.executable, *args], cwd=root, check=True)


def refresh(root=ROOT, run=command):
    if git(root, 'status', '--porcelain'):
        raise RuntimeError('Refresh requires a clean checkout; existing work is preserved.')
    if git(root, 'branch', '--show-current') != 'main':
        raise RuntimeError('Refresh only publishes from main.')
    start = git(root, 'rev-parse', 'HEAD')
    git(root, 'fetch', 'origin', 'main')
    if start != git(root, 'rev-parse', 'FETCH_HEAD'):
        raise RuntimeError('Checkout is behind origin/main; rerun with a fresh checkout.')
    readme = root / 'README.md'
    original_readme = readme.read_bytes()
    run(root, 'scripts/update_profile.py', '--data-only')
    run(root, 'scripts/render_profile.py')
    run(root, 'scripts/build_offline.py')
    for check in CHECKS:
        run(root, check)
    # Rendering defaults to main. Never replace an immutable pin on a no-op.
    readme.write_bytes(original_readme)
    git(root, 'add', '--', *ARTIFACTS)
    if not git(root, 'diff', '--cached', '--name-only'):
        print('No generated artifact changes; no commits or push.')
        return None
    identity = ['-c', 'user.name=github-actions[bot]', '-c',
                'user.email=41898282+github-actions[bot]@users.noreply.github.com']
    git(root, *identity, 'commit', '-m', 'chore: refresh public profile snapshot')
    asset_commit = git(root, 'rev-parse', 'HEAD')
    run(root, 'scripts/render_profile.py', '--asset-ref', asset_commit)
    for check in CHECKS:
        run(root, check)
    # A second render must only change README, never the committed artwork.
    if git(root, 'diff', '--name-only', '--', *ARTIFACTS):
        raise RuntimeError('Pinned render unexpectedly changed generated artifacts.')
    git(root, 'add', '--', 'README.md')
    git(root, *identity, 'commit', '-m', 'chore: pin profile images to snapshot commit')
    # Refuse a concurrent human update. No merge, force push, or partial publication.
    git(root, 'fetch', 'origin', 'main')
    if git(root, 'rev-parse', 'FETCH_HEAD') != start:
        raise RuntimeError('origin/main changed during refresh; rerun with a fresh checkout.')
    git(root, 'push', '--atomic', 'origin', 'HEAD:refs/heads/main')
    print('Published immutable profile snapshot: ' + asset_commit)
    return asset_commit


if __name__ == '__main__':
    published = refresh()
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
            output.write('published=' + str(published is not None).lower() + '\n')
