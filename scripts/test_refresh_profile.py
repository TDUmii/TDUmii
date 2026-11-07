"""Offline integration tests using real temporary Git repositories."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import subprocess
import unittest

from refresh_profile import refresh, git


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.remote = base / 'remote.git'
        self.root = base / 'work'
        subprocess.run(['git', 'init', '--bare', str(self.remote)], check=True, capture_output=True)
        subprocess.run(['git', 'clone', str(self.remote), str(self.root)], check=True, capture_output=True)
        git(self.root, 'checkout', '-b', 'main')
        git(self.root, 'config', 'user.name', 'Fixture')
        git(self.root, 'config', 'user.email', 'fixture@example.invalid')
        (self.root / 'assets').mkdir()
        for name, value in [('README.md', 'immutable-original'), ('assets/card.svg', 'old'),
                            ('assets/profile-data.json', '{}'), ('assets/profile-data.js', '{}'),
                            ('index.html', 'page')]:
            (self.root / name).write_text(value)
        git(self.root, 'add', '.')
        git(self.root, 'commit', '-m', 'initial')
        git(self.root, 'push', 'origin', 'main')
        self.initial = git(self.root, 'rev-parse', 'HEAD')

    def remote_head(self):
        return git(self.root, 'ls-remote', 'origin', 'refs/heads/main').split()[0]

    def runner(self, changed=True, fail=False, race=False):
        def run(root, script, *args):
            if script.endswith('update_profile.py') and changed:
                (root / 'assets/card.svg').write_text('fresh-public-art')
            if script.endswith('render_profile.py'):
                (root / 'README.md').write_text(args[-1] if args else 'main')
            if fail and script.endswith('check_assets.py'):
                raise RuntimeError('invalid generated art')
            if race and args and args[0] == '--asset-ref':
                other = root.parent / 'other'
                subprocess.run(['git', 'clone', '-b', 'main', str(self.remote), str(other)],
                               check=True, capture_output=True)
                (other / 'human.txt').write_text('concurrent human work')
                git(other, 'add', 'human.txt')
                git(other, '-c', 'user.name=Human', '-c', 'user.email=human@example.invalid',
                    'commit', '-m', 'human')
                git(other, 'push', 'origin', 'main')
        return run

    def test_two_commit_immutable_pin_and_single_atomic_push(self):
        import refresh_profile
        runner = self.runner()
        def render_with_private_output(root, script, *args):
            runner(root, script, *args)
            (root / 'private-source.json').write_text('private diagnostic fixture')
        with patch.object(refresh_profile, 'git', wraps=git) as calls:
            asset = refresh(self.root, render_with_private_output)
        pushes = [call.args for call in calls.call_args_list if 'push' in call.args]
        self.assertEqual(len(pushes), 1)
        self.assertIn('--atomic', pushes[0])
        self.assertEqual(git(self.root, 'rev-parse', 'HEAD~1'), asset)
        self.assertEqual((self.root / 'README.md').read_text(), asset)
        self.assertEqual(self.remote_head(), git(self.root, 'rev-parse', 'HEAD'))
        self.assertEqual(git(self.root, 'rev-list', '--count', self.initial + '..HEAD'), '2')
        self.assertEqual(git(self.root, 'show', asset + ':assets/card.svg'), 'fresh-public-art')
        self.assertEqual(git(self.root, 'log', '-1', '--format=%ae'),
                         '41898282+github-actions[bot]@users.noreply.github.com')
        self.assertNotIn('private-source.json', git(self.root, 'ls-tree', '-r', '--name-only', 'HEAD'))

    def test_noop_preserves_immutable_readme(self):
        self.assertIsNone(refresh(self.root, self.runner(changed=False)))
        self.assertEqual((self.root / 'README.md').read_text(), 'immutable-original')
        self.assertEqual(self.remote_head(), self.initial)
        self.assertEqual(git(self.root, 'status', '--porcelain'), '')

    def test_failed_validation_does_not_publish(self):
        with self.assertRaisesRegex(RuntimeError, 'invalid generated art'):
            refresh(self.root, self.runner(fail=True))
        self.assertEqual(self.remote_head(), self.initial)

    def test_concurrent_human_update_is_preserved(self):
        with self.assertRaisesRegex(RuntimeError, 'changed during refresh'):
            refresh(self.root, self.runner(race=True))
        self.assertEqual(git(self.root, 'show', 'FETCH_HEAD:human.txt'), 'concurrent human work')
        self.assertNotEqual(self.remote_head(), git(self.root, 'rev-parse', 'HEAD'))

    def test_dirty_checkout_is_not_overwritten(self):
        (self.root / 'README.md').write_text('human draft')
        with self.assertRaisesRegex(RuntimeError, 'clean checkout'):
            refresh(self.root, self.runner())
        self.assertEqual((self.root / 'README.md').read_text(), 'human draft')


if __name__ == '__main__':
    unittest.main()
