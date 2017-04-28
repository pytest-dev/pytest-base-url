# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

import pytest

from requests.packages.urllib3.util.retry import Retry


@pytest.fixture(autouse=True)
def httpserver(httpserver):
    return httpserver


def test_ignore_bad_url_by_default(testdir, httpserver):
    testdir.makepyfile('def test_pass(): pass')
    httpserver.serve_content(content='<h1>Error!</h1>', code=500)
    result = testdir.runpytest('--base-url', httpserver.url)
    assert result.ret == 0


def test_enable_verify_via_cli(testdir, httpserver, monkeypatch):
    testdir.makepyfile('def test_pass(): pass')
    monkeypatch.setenv('VERIFY_BASE_URL', False)
    monkeypatch.setattr(Retry, 'BACKOFF_MAX', 5)
    status_code = 500
    httpserver.serve_content(content='<h1>Error!</h1>', code=status_code)
    reprec = testdir.inline_run('--base-url', httpserver.url,
                                '--verify-base-url')
    passed, skipped, failed = reprec.listoutcomes()
    assert len(failed) == 1
    out = failed[0].longrepr.reprcrash.message
    assert 'UsageError: Base URL failed verification!' in out
    assert 'URL: {0}'.format(httpserver.url) in out
    assert 'Potential HTTP error codes: [500, 502, 503, 504].'
    assert 'Tried 10 times' in out
    assert 'Response headers: ' in out


def test_enable_verify_via_env(testdir, httpserver, monkeypatch):
    testdir.makepyfile('def test_pass(): pass')
    monkeypatch.setenv('VERIFY_BASE_URL', True)
    monkeypatch.setattr(Retry, 'BACKOFF_MAX', 5)
    status_code = 500
    httpserver.serve_content(content='<h1>Error!</h1>', code=status_code)
    reprec = testdir.inline_run('--base-url', httpserver.url)
    passed, skipped, failed = reprec.listoutcomes()
    assert len(failed) == 1
    out = failed[0].longrepr.reprcrash.message
    assert 'UsageError: Base URL failed verification!' in out
    assert 'URL: {0}'.format(httpserver.url) in out
    assert 'Potential HTTP error codes: [500, 502, 503, 504].'
    assert 'Tried 10 times' in out
    assert 'Response headers: ' in out


def test_disable_verify_via_env(testdir, httpserver, monkeypatch):
    testdir.makepyfile('def test_pass(): pass')
    monkeypatch.setenv('VERIFY_BASE_URL', False)
    httpserver.serve_content(content='<h1>Error!</h1>', code=500)
    result = testdir.runpytest('--base-url', httpserver.url)
    assert result.ret == 0


def test_verify_retries_url(testdir, httpserver, monkeypatch):
    testdir.makepyfile('def test_pass(): pass')
    monkeypatch.setenv('VERIFY_BASE_URL', False)
    monkeypatch.setattr(Retry, 'BACKOFF_MAX', 5)
    httpserver.serve_content(content='<h1>Error!</h1>', code=500)
    reprec = testdir.inline_run('--base-url', httpserver.url,
                                '--verify-base-url')
    passed, skipped, failed = reprec.listoutcomes()
    assert len(failed) == 1
    out = failed[0].longrepr.reprcrash.message
    assert 'UsageError: Base URL failed verification!' in out
    httpserver.serve_content(content='<h1>Loaded!</h1>')
    reprec = testdir.inline_run('--base-url', httpserver.url,
                                '--verify-base-url')
    passed, skipped, failed = reprec.listoutcomes()
    assert len(passed) == 1
