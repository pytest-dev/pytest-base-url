# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from requests.packages.urllib3.util.retry import Retry

from packaging.version import Version
from requests.packages.urllib3 import __version__ as URLLIB3_VERSION

if Version(URLLIB3_VERSION) < Version("1.26.8"):
    BACKOFF_ATTRIB_NAME = "BACKOFF_MAX"
else:
    BACKOFF_ATTRIB_NAME = "DEFAULT_BACKOFF_MAX"


def test_ignore_bad_url_by_default(testdir, httpserver):
    testdir.makepyfile("def test_pass(): pass")
    httpserver.serve_content(content="<h1>Error!</h1>", code=500)
    result = testdir.runpytest("--base-url", httpserver.url)
    assert result.ret == 0


def test_enable_verify_via_cli(testdir, httpserver, monkeypatch):
    testdir.makepyfile("def test_pass(): pass")
    monkeypatch.setenv("VERIFY_BASE_URL", "false")
    monkeypatch.setattr(Retry, BACKOFF_ATTRIB_NAME, 0.5)
    status_code = 500
    httpserver.serve_content(content="<h1>Error!</h1>", code=status_code)
    reprec = testdir.inline_run("--base-url", httpserver.url, "--verify-base-url")
    passed, skipped, failed = reprec.listoutcomes()
    assert len(failed) == 1
    out = failed[0].longrepr.reprcrash.message
    assert "Max retries exceeded with url:" in out
    assert "Caused by ResponseError" in out
    assert "too many 500 error responses" in out


def test_enable_verify_via_env(testdir, httpserver, monkeypatch):
    testdir.makepyfile("def test_pass(): pass")
    monkeypatch.setenv("VERIFY_BASE_URL", "true")
    monkeypatch.setattr(Retry, BACKOFF_ATTRIB_NAME, 0.5)
    status_code = 500
    httpserver.serve_content(content="<h1>Error!</h1>", code=status_code)
    reprec = testdir.inline_run("--base-url", httpserver.url)
    passed, skipped, failed = reprec.listoutcomes()
    assert len(failed) == 1
    out = failed[0].longrepr.reprcrash.message
    assert "Max retries exceeded with url:" in out
    assert "Caused by ResponseError" in out
    assert "too many 500 error responses" in out


def test_disable_verify_via_env(testdir, httpserver, monkeypatch):
    testdir.makepyfile("def test_pass(): pass")
    monkeypatch.setenv("VERIFY_BASE_URL", "false")
    httpserver.serve_content(content="<h1>Error!</h1>", code=500)
    result = testdir.runpytest("--base-url", httpserver.url)
    assert result.ret == 0


def test_url_fails(testdir, httpserver, monkeypatch):
    testdir.makepyfile("def test_pass(): pass")
    monkeypatch.setenv("VERIFY_BASE_URL", "false")
    monkeypatch.setattr(Retry, BACKOFF_ATTRIB_NAME, 0.5)
    reprec = testdir.inline_run("--base-url", "http://foo", "--verify-base-url")
    passed, skipped, failed = reprec.listoutcomes()
    out = failed[0].longrepr.reprcrash.message
    assert len(failed) == 1
    assert "Max retries exceeded with url:" in out
    assert "Caused by NewConnectionError" in out
    assert "Failed to establish a new connection" in out
