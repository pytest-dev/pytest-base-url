# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.


def test_fixture(testdir):
    testdir.makepyfile("""
        import pytest
        @pytest.fixture(scope='session')
        def base_url():
            return 'foo'
        def test_fixture(base_url):
            assert base_url == 'foo'
    """)
    result = testdir.runpytest()
    assert result.ret == 0


def test_cli(testdir):
    testdir.makepyfile("""
        def test_funcarg(base_url):
            assert base_url == 'foo'
    """)
    result = testdir.runpytest('--base-url', 'foo')
    assert result.ret == 0


def test_config(testdir):
    testdir.makefile('.ini', pytest="""
        [pytest]
        base_url=foo
    """)
    testdir.makepyfile("""
        def test_config(request, base_url):
            assert request.config.getvalue('base_url') == 'foo'
            assert request.config.getini('base_url') == 'foo'
            assert base_url == 'foo'
    """)
    result = testdir.runpytest()
    assert result.ret == 0


def test_skip_config(testdir):
    testdir.makefile('.ini', pytest="""
        [pytest]
        base_url=foo
    """)
    testdir.makepyfile("""
        import pytest
        @pytest.mark.skipif(
            pytest.config.getoption('base_url') == 'foo',
            reason='skip')
        def test_skip_config(): pass
    """)
    result = testdir.runpytest()
    assert result.ret == 0


def test_env_var_set(testdir, monkeypatch):
    testdir.makepyfile("""
        def test_config(request, base_url):
            assert request.config.getvalue('base_url')
            assert base_url == 'yeehaw'
    """)
    monkeypatch.setenv('PYTEST_BASE_URL', 'yeehaw')
    reprec = testdir.inline_run()
    passed, skipped, failed = reprec.listoutcomes()
    assert len(passed) == 1
