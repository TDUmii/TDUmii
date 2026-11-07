"""Request and verify a legacy GitHub Pages build of the current commit."""
import json
import os
import re
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def request_build_api(repository, token, method='GET', timeout=30):
    request = Request('https://api.github.com/repos/' + repository + '/pages/builds' +
                      ('/latest' if method == 'GET' else ''),
                      data=b'{}' if method == 'POST' else None, method=method,
                      headers={'Authorization': 'Bearer ' + token,
                               'Accept': 'application/vnd.github+json',
                               'X-GitHub-Api-Version': '2026-03-10',
                               'User-Agent': 'UmiGitProfile-Pages-Refresh'})
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.load(response)
            if not isinstance(result, dict):
                raise RuntimeError('Pages API returned an invalid build response')
            return result
    except HTTPError as error:
        if method == 'GET' and error.code == 404:
            return {}
        raise RuntimeError('Pages API returned HTTP ' + str(error.code)) from None
    except (URLError, TimeoutError, json.JSONDecodeError):
        raise RuntimeError('Pages API request failed or returned invalid JSON') from None


def refresh(repository, token, head, api=request_build_api, sleep=time.sleep,
            clock=time.monotonic, timeout=300):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('GITHUB_REPOSITORY must be owner/repository')
    if not token:
        raise ValueError('GITHUB_TOKEN is required')
    if not re.fullmatch(r'[0-9a-f]{40}', head):
        raise ValueError('Expected a full Git commit SHA')
    deadline = clock() + timeout
    def call(method='GET'):
        remaining = deadline - clock()
        if remaining <= 0:
            raise RuntimeError('Timed out waiting for Pages to build the current commit')
        return api(repository, token, method, timeout=min(30, remaining))
    build = call()
    if build.get('commit') == head and build.get('status') == 'built':
        print('Pages already built the current commit.')
        return
    call('POST')
    while clock() < deadline:
        build = call()
        if build.get('commit') == head:
            if build.get('status') == 'built':
                print('Pages built current commit: ' + head)
                return
            if build.get('status') == 'errored':
                raise RuntimeError('Pages build failed for the current commit')
        sleep(min(5, max(0, deadline - clock())))
    raise RuntimeError('Timed out waiting for Pages to build the current commit')


if __name__ == '__main__':
    try:
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], check=True,
                              capture_output=True, text=True).stdout.strip()
        refresh(os.environ.get('GITHUB_REPOSITORY', ''),
                os.environ.get('GITHUB_TOKEN', ''), head)
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error)) from None
