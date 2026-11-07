"""Public pagination must never publish a partial or private repository set."""
import json
import unittest

from update_profile import USER, public_repositories
from release_summary import REPOSITORIES, highlight, latest_releases, summarize


def release(repo='umi-bridge', tag='v1.0.0', **changes):
    row = {'tag_name': tag, 'draft': False, 'prerelease': False,
           'html_url': f'https://github.com/TDUmii/{repo}/releases/tag/{tag}',
           'published_at': '2026-11-01T10:00:00Z',
           'body': '## What is new\n- Add local CSV export.'}
    row.update(changes)
    return row


class PublicReleaseTests(unittest.TestCase):
    def test_filters_drafts_prereleases_and_sorts_by_publication(self):
        def get(url):
            repo = url.split('/')[5]
            return json.dumps([release(repo, 'draft', draft=True),
                               release(repo, 'preview', prerelease=True),
                               release(repo, 'v9.0.0', published_at='2026-10-01T00:00:00Z'),
                               release(repo, 'v1.0.0', published_at='2026-11-0'+str(REPOSITORIES.index(repo)+1)+'T00:00:00Z')])
        rows = latest_releases(get)
        self.assertEqual([row['repo'] for row in rows], list(reversed(REPOSITORIES)))
        self.assertTrue(all(row['tag'] == 'v1.0.0' for row in rows))
        self.assertEqual(rows[0]['highlight'], 'Add local CSV export.')
        self.assertEqual(rows[0]['name'], 'Background Automation Studio')

    def test_pagination_can_find_stable_release_after_full_preview_page(self):
        urls = []
        def get(url):
            urls.append(url)
            repo = url.split('/')[5]
            if repo != 'umi-bridge':
                return '[]'
            if url.endswith('&page=1'):
                return json.dumps([release(tag='preview'+str(i), prerelease=True) for i in range(100)])
            return json.dumps([release()])
        rows = latest_releases(get)
        self.assertEqual(len(rows), 1)
        self.assertTrue(any('page=2' in url for url in urls))
        with self.assertRaisesRegex(ValueError, 'Duplicate public release'):
            latest_releases(lambda url: json.dumps([release(), release()]))

    def test_no_release_is_omitted_and_source_errors_propagate(self):
        self.assertEqual(latest_releases(lambda url: '[]'), [])
        def failed(url):
            raise RuntimeError('source failure')
        with self.assertRaisesRegex(RuntimeError, 'source failure'):
            latest_releases(failed)
        for payload in ('{}', 'not JSON'):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                latest_releases(lambda url: payload)

    def test_canonical_public_release_url_and_repo_are_required(self):
        for url in ('https://evil.example/TDUmii/umi-bridge/releases/tag/v1.0.0',
                    'https://github.com/TDUmii/QuietShare/releases/tag/v1.0.0',
                    'https://github.com/TDUmii/umi-bridge/releases/tag/other',
                    'https://github.com/TDUmii/umi-bridge/releases/tag/v1.0.0?redirect=1',
                    'http://github.com/TDUmii/umi-bridge/releases/tag/v1.0.0'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                summarize('umi-bridge', release(html_url=url))
        with self.assertRaises(ValueError):
            summarize('unlisted', release())
        with self.assertRaises(ValueError):
            summarize('umi-bridge', release(published_at='invalid'))
        with self.assertRaises(ValueError):
            summarize('umi-bridge', release(draft='false'))

    def test_notes_sanitize_markup_skip_headings_and_truncate(self):
        body = '## Add an invented heading\n- Add **local** [CSV](https://example.com) export.\n- Fix another issue.'
        self.assertEqual(highlight('umi-bridge', 'unknown', body), 'Add local CSV export.')
        text = highlight('umi-bridge', 'unknown', '- Add ' + 'documented '*30 + 'features.')
        self.assertLessEqual(len(text), 82)
        self.assertTrue(text.endswith('...'))
        self.assertEqual(highlight('umi-bridge', 'unknown', '## What is new\n- Amazing ultimate tool.\n- Thêm tính năng.'), '')
        self.assertEqual(highlight('umi-bridge', 'unknown', '## Changes\\n- Fix local export.'), 'Fix local export.')

    def test_audited_excerpt_must_still_exist_in_exact_tag_notes(self):
        excerpt = 'A calendar heatmap shows actual requests by local day.'
        self.assertEqual(highlight('umi-bridge', 'v1.16.0', '- '+excerpt),
                         'Calendar heatmap of requests by local day.')
        self.assertEqual(highlight('umi-bridge', 'v1.16.0', '- Fix a different issue.'), 'Fix a different issue.')
        self.assertEqual(highlight('umi-bridge', 'another-tag', '- '+excerpt), '')
        self.assertEqual(highlight('QuietShare', 'v0.20.0',
                                   '- Add on-demand PDF thumbnails, bookmarks and go-to-page.'),
                         'PDF thumbnails, bookmarks and go-to-page.')
        self.assertEqual(highlight('BackgroundAutomationStudio', 'v2.6.1',
                                   '- Avoids unnecessary workflow expansion when the coordinate overlay is disabled.'),
                         'Avoid extra workflow expansion with overlay off.')


class PublicRepositoryTests(unittest.TestCase):
    def test_paginated_snapshot(self):
        pages = [[{'id': i, 'private': False} for i in range(100)],
                 [{'id': 100, 'private': False}]]
        urls = []
        def get(url):
            urls.append(url)
            return json.dumps(pages.pop(0))
        result = public_repositories({'login': USER, 'public_repos': 101}, get)
        self.assertEqual(len(result), 101)
        self.assertIn('page=2', urls[1])
        self.assertTrue(all('type=owner' in url for url in urls))

    def test_rejects_private_duplicate_and_incomplete_snapshots(self):
        profile = {'login': USER, 'public_repos': 2}
        for rows in ([{'id': 1, 'private': True}],
                     [{'id': 1, 'private': False}]*2,
                     [{'id': 1, 'private': False}]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                public_repositories(profile, lambda url: json.dumps(rows))


if __name__ == '__main__':
    unittest.main()
