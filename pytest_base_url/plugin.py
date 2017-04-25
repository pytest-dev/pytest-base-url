# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import time

import pytest
import requests


@pytest.fixture(scope='session')
def base_url(request):
    """Return a base URL"""
    config = request.config
    base_url = config.getoption('base_url')
    if base_url is not None:
        return base_url


@pytest.fixture(scope='session', autouse=True)
def _verify_url(request, base_url):
    """Verifies the base URL"""
    verify = request.config.option.verify_base_url
    verify_timeout = request.config.getoption('verify_base_url_timeout')
    if base_url and verify:
        timeout = time.time() + verify_timeout
        while time.time() < timeout:
            try:
                response = requests.get(base_url, timeout=1)
            except Exception:
                continue
        try:
            response.status_code == requests.codes.ok
        except UnboundLocalError:
            raise pytest.UsageError(
                'Base URL failed verification!'
                '\nURL: {0}. Tried for {1} seconds'.format(
                    base_url, verify_timeout))


def pytest_configure(config):
    if hasattr(config, 'slaveinput'):
        return  # xdist slave
    base_url = config.getoption('base_url') or config.getini('base_url')
    if base_url is not None:
        config.option.base_url = base_url
        if hasattr(config, '_metadata'):
            config._metadata['Base URL'] = base_url


def pytest_report_header(config, startdir):
    base_url = config.getoption('base_url')
    if base_url:
        return 'baseurl: {0}'.format(base_url)


def pytest_addoption(parser):
    parser.addini('base_url', help='base url for the application under test.')
    parser.addoption(
        '--base-url',
        metavar='url',
        default=os.getenv('PYTEST_BASE_URL', None),
        help='base url for the application under test.')
    parser.addoption(
        '--verify-base-url',
        action='store_true',
        default=not os.getenv('VERIFY_BASE_URL', 'false').lower() == 'false',
        help='verify the base url.')
    parser.addoption(
        '--verify-base-url-timeout',
        type=int,
        default=os.getenv('VERIFY_BASE_URL_TIMEOUT', None),
        help='amount of time to verify the base url.')
