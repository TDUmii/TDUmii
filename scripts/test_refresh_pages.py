"""Offline Pages API state-transition checks."""
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
import unittest

from refresh_pages import refresh, request_build_api

HEAD = 'a' * 40


class PagesTests(unittest.TestCase):
    def test_already_deployed_is_noop(self):
        api = Mock(return_value={'status': 'succeed'})
        refresh('owner/repo', 'secret-fixture', HEAD, api=api)
        self.assertEqual(api.call_count, 1)

    def test_missing_then_queued_deployment_completes(self):
        api = Mock(side_effect=[{}, {'status': 'errored'}, {},
                               {'status': 'deployment_in_progress'},
                               {'status': 'succeed'}])
        sleep = Mock()
        refresh('owner/repo', 'secret-fixture', HEAD, api=api, sleep=sleep)
        self.assertEqual(api.call_args_list[1].args[-1], 'POST')
        self.assertEqual(sleep.call_count, 2)
        for call in api.call_args_list:
            self.assertEqual(call.args[2], HEAD)

    def test_current_deployment_error_fails(self):
        for status in ('deployment_failed', 'deployment_content_failed',
                       'deployment_cancelled', 'deployment_attempt_error'):
            with self.subTest(status=status):
                api = Mock(side_effect=[{}, {}, {'status': status}])
                with self.assertRaisesRegex(RuntimeError, 'deployment failed'):
                    refresh('owner/repo', 'secret-fixture', HEAD, api=api)

    def test_missing_deployment_times_out(self):
        api = Mock(return_value={})
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
                    request_build_api('owner/repo', 'secret-fixture', HEAD)
                self.assertNotIn('secret-fixture', str(caught.exception))

    def test_http_get_uses_exact_deployment_and_post_only_triggers_build(self):
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read = Mock(return_value=b'{"status":"succeed"}')
        with patch('refresh_pages.urlopen', return_value=response) as open_url:
            request_build_api('owner/repo', 'secret-fixture', HEAD)
            self.assertTrue(open_url.call_args.args[0].full_url.endswith('/pages/deployments/' + HEAD))
            request_build_api('owner/repo', 'secret-fixture', HEAD, 'POST')
            self.assertTrue(open_url.call_args.args[0].full_url.endswith('/pages/builds'))

    def test_deployment_404_is_not_yet_created(self):
        error = HTTPError('url', 404, 'missing', {}, None)
        with patch('refresh_pages.urlopen', side_effect=error):
            self.assertEqual(request_build_api('owner/repo', 'secret-fixture', HEAD), {})

    def test_invalid_repository_rejected_before_request(self):
        api = Mock()
        with self.assertRaises(ValueError):
            refresh('../bad/repo', 'secret-fixture', HEAD, api=api)
        api.assert_not_called()


if __name__ == '__main__':
    unittest.main()
