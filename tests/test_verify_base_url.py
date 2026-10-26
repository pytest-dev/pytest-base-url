# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
from requests.packages.urllib3.util.retry import Retry
import pytest

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
    assert "Caused by NameResolutionError" in out
    assert "Failed to resolve" in out


@pytest.mark.parametrize("scope", ["function", "class", "module", "package", "session"])
@pytest.mark.parametrize("verify", [False, True])
def test_custom_fixture_scope(testdir, monkeypatch, scope, verify):
    verified = []
    monkeypatch.setenv("VERIFY_BASE_URL", "false")
    monkeypatch.setattr("requests.Session.get", lambda self, url: verified.append(url))
    testdir.makeconftest("""
        import pytest

        @pytest.fixture(scope={!r})
        def base_url():
            return "http://example.test"
    """.format(scope))
    testdir.makepyfile("""
        class TestURLs:
            def test_first(self, base_url):
                assert base_url == "http://example.test"

            def test_second(self, base_url):
                assert base_url == "http://example.test"
    """)
    args = ["--base-url-scope", scope]
    if verify:
        args.append("--verify-base-url")
    reprec = testdir.inline_run(*args)
    reprec.assertoutcome(passed=2)
    expected = (2 if scope == "function" else 1) if verify else 0
    assert verified == ["http://example.test"] * expected


def test_default_scope_verifies_once(testdir, monkeypatch):
    verified = []
    monkeypatch.setattr("requests.Session.get", lambda self, url: verified.append(url))
    testdir.makepyfile("""
        def test_first(base_url):
            assert base_url == "http://example.test"

        def test_second(base_url):
            assert base_url == "http://example.test"
    """)
    reprec = testdir.inline_run(
        "--base-url", "http://example.test", "--verify-base-url"
    )
    reprec.assertoutcome(passed=2)
    assert verified == ["http://example.test"]
