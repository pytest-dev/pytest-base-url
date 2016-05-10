# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os

import pytest
import requests


@pytest.fixture(scope='session')
def base_url(request):
    """Return a base URL"""
    config = request.config
    base_url = config.getoption('base_url')
    if base_url is not None:
        if hasattr(config, '_environment'):
            config._environment.append(('Base URL', base_url))
        return base_url


@pytest.fixture(scope='session', autouse=True)
def _verify_url(request, base_url):
    """Verifies the base URL"""
    verify = request.config.option.verify_base_url
    if base_url and verify:
        response = requests.get(base_url, timeout=10)
        if not response.status_code == requests.codes.ok:
            raise pytest.UsageError(
                'Base URL failed verification!'
                '\nURL: {0}, Response status code: {1.status_code}'
                '\nResponse headers: {1.headers}'.format(base_url, response))


def pytest_configure(config):
    if hasattr(config, 'slaveinput'):
        return  # xdist slave
    base_url = config.getoption('base_url') or config.getini('base_url')
    if base_url is not None:
        config.option.base_url = base_url


def pytest_addoption(parser):
    parser.addini('base_url', help='base url for the application under test.')
    parser.addoption(
        '--base-url',
        metavar='url',
        help='base url for the application under test.')
    parser.addoption(
        '--verify-base-url',
        action='store_true',
        default=not os.getenv('VERIFY_BASE_URL', 'false').lower() == 'false',
        help='verify the base url.')
