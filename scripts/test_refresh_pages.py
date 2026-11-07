"""Offline Pages API state-transition checks."""
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
import unittest

from refresh_pages import refresh, request_build_api

HEAD = 'a' * 40
OLD = 'b' * 40


class PagesTests(unittest.TestCase):
    def test_already_built_is_noop(self):
        api = Mock(return_value={'commit': HEAD, 'status': 'built'})
        refresh('owner/repo', 'secret-fixture', HEAD, api=api)
        self.assertEqual(api.call_count, 1)

    def test_old_built_is_never_accepted_then_queued_build_completes(self):
        api = Mock(side_effect=[{'commit': OLD, 'status': 'built'}, {},
                               {'commit': OLD, 'status': 'built'},
                               {'commit': HEAD, 'status': 'queued'},
                               {'commit': HEAD, 'status': 'built'}])
        sleep = Mock()
        refresh('owner/repo', 'secret-fixture', HEAD, api=api, sleep=sleep)
        self.assertEqual(api.call_args_list[1].args[-1], 'POST')
        self.assertEqual(sleep.call_count, 2)

    def test_current_build_error_fails(self):
        api = Mock(side_effect=[{}, {}, {'commit': HEAD, 'status': 'errored'}])
        with self.assertRaisesRegex(RuntimeError, 'build failed'):
            refresh('owner/repo', 'secret-fixture', HEAD, api=api)

    def test_old_build_times_out(self):
        api = Mock(return_value={'commit': OLD, 'status': 'built'})
        now = [0]
        def sleep(seconds):
            now[0] += seconds
        with self.assertRaisesRegex(RuntimeError, 'Timed out'):
            refresh('owner/repo', 'secret-fixture', HEAD, api=api,
                    sleep=sleep, clock=lambda: now[0], timeout=5)

    def test_api_errors_are_concise_and_do_not_expose_token(self):
        for error in (HTTPError('url', 403, 'secret-fixture', {}, None),
                      URLError('secret-fixture')):
            with self.subTest(error=type(error).__name__), patch('refresh_pages.urlopen', side_effect=error):
                with self.assertRaises(RuntimeError) as caught:
                    request_build_api('owner/repo', 'secret-fixture')
                self.assertNotIn('secret-fixture', str(caught.exception))

    def test_invalid_repository_rejected_before_request(self):
        api = Mock()
        with self.assertRaises(ValueError):
            refresh('../bad/repo', 'secret-fixture', HEAD, api=api)
        api.assert_not_called()


if __name__ == '__main__':
    unittest.main()
