# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import pytest


@pytest.fixture(scope="session")
def base_url(request):
    """Return a base URL"""
    config = request.config
    base_url = config.getoption("base_url")
    if base_url is not None:
        return base_url


@pytest.fixture(scope="session", autouse=True)
def _verify_url(request, base_url):
    """Verifies the base URL"""

    verify = request.config.option.verify_base_url
    if base_url and verify:
        # Lazy load requests to reduce cost for tests that don't use the plugin
        import requests
        from requests.packages.urllib3.util.retry import Retry
        from requests.adapters import HTTPAdapter

        session = requests.Session()
        retries = Retry(backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        session.mount(base_url, HTTPAdapter(max_retries=retries))
        session.get(base_url)


def pytest_configure(config):
    if hasattr(config, "workerinput"):
        return  # don't run configure on xdist worker nodes
    base_url = config.getoption("base_url") or config.getini("base_url")
    if base_url is not None:
        config.option.base_url = base_url
        metadata = config.pluginmanager.getplugin("metadata")
        if metadata:
            try:
                from pytest_metadata.plugin import metadata_key

                config.stash[metadata_key]["Base URL"] = base_url
            except ImportError:  # pytest-metadata < 3.x
                config._metadata["Base URL"] = base_url


def pytest_report_header(config, start_path):
    base_url = config.getoption("base_url")
    if base_url:
        return "baseurl: {0}".format(base_url)


def pytest_addoption(parser):
    parser.addini("base_url", help="base url for the application under test.")
    parser.addoption(
        "--base-url",
        metavar="url",
        default=os.getenv("PYTEST_BASE_URL", None),
        help="base url for the application under test.",
    )
    parser.addoption(
        "--verify-base-url",
        action="store_true",
        default=not os.getenv("VERIFY_BASE_URL", "false").lower() == "false",
        help="verify the base url.",
    )
