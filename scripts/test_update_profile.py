"""Public pagination must never publish a partial or private repository set."""
import json
import unittest

from update_profile import USER, public_repositories


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
