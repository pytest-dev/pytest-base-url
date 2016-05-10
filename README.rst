pytest-base-url
===============

pytest-base-url is a simple plugin for pytest_ that provides an optional base
URL via the command line or configuration file.

.. image:: https://img.shields.io/badge/license-MPL%202.0-blue.svg
   :target: https://github.com/davehunt/pytest-base-url/blob/master/LICENSE
   :alt: License
.. image:: https://img.shields.io/travis/davehunt/pytest-base-url.svg
   :target: https://travis-ci.org/davehunt/pytest-base-url/
   :alt: Travis
.. image:: https://img.shields.io/github/issues-raw/davehunt/pytest-base-url.svg
   :target: https://github.com/davehunt/pytest-base-url/issues
   :alt: Issues
.. image:: https://img.shields.io/requires/github/davehunt/pytest-base-url.svg
   :target: https://requires.io/github/davehunt/pytest-base-url/requirements/?branch=master
   :alt: Requirements

Requirements
------------

You will need the following prerequisites in order to use pytest-base-url:

- Python 2.6, 2.7, 3.3, 3.4, 3.5, PyPy, or PyPy3
- py.test 2.7 or newer

Installation
------------

To install pytest-base-url:

.. code-block:: bash

  $ pip install git+git://github.com/davehunt/pytest-base-url

Specifying a Base URL
---------------------

Rather than repeating or abstracting a base URL in your tests, pytest-base-url
provides a ``base_url`` fixture that returns the specified base URL.

.. code-block:: python

  import urllib2

  def test_example(base_url):
      assert 200 == urllib2.urlopen(base_url).getcode()

Using the Command Line
^^^^^^^^^^^^^^^^^^^^^^

You can specify the base URL on the command line:

.. code-block:: bash

  $ py.test --base-url http://www.example.com

Using a Configuration File
^^^^^^^^^^^^^^^^^^^^^^^^^^

You can specify the base URL using a `configuration file`_:

.. code-block:: ini

  [pytest]
  base_url = http://www.example.com

Using a Fixture
^^^^^^^^^^^^^^^

If your test harness takes care of launching an instance of your application
under test, you may not have a predictable base URL to provide on the command
line. Fortunately, it's easy to override the ``base_url`` fixture and return
the correct URL to your test.

In the following example a ``live_server`` fixture is used to start the
application and ``live_server.url`` returns the base URL of the site.

.. code-block:: python

  import urllib2
  import pytest

  @pytest.fixture
  def base_url(live_server):
      return live_server.url

  def test_search(base_url):
      assert 200 == urllib2.urlopen('{0}/search'.format(base_url)).getcode()

Available Live Servers
----------------------

It's relatively simple to create your own ``live_server`` fixture, however you
may be able to take advantage of one of the following:

* Django applications can use pytest-django_'s  ``live_server`` fixture.
* Flask applications can use pytest-flask_'s ``live_server`` fixture.

Verifying the Base URL
----------------------

If you specify a base URL for a site that's unavailable then all tests using
that base URL will likely fail. To avoid running every test in this instance,
you can enable base URL verification. This will check the base URL is
responding before proceeding with the test suite. To enable this, specify the
``--verify-base-url`` command line option or set the ``VERIFY_BASE_URL``
environment variable to ``TRUE``.

Skipping Base URLs
------------------

You can `skip tests`_ based on the value of the base URL so long as it is
provided either by the command line or in a configuration file:

.. code-block:: python

  import urllib2
  import pytest

  @pytest.mark.skipif(
      'dev' in pytest.config.getoption('base_url'),
      reason='Search not available on dev')
  def test_search(base_url):
      assert 200 == urllib2.urlopen('{0}/search'.format(base_url)).getcode()

Unfortunately if the URL is provided by a fixture, there is no way to know this
value at test collection.

Resources
---------

- `Issue Tracker`_
- Code_

.. _pytest: http://www.python.org/
.. _configuration file: http://pytest.org/latest/customize.html#command-line-options-and-configuration-file-settings
.. _pytest-django: http://pytest-django.readthedocs.org/
.. _pytest-flask: http://pytest-flask.readthedocs.org/
.. _skip tests: http://pytest.org/latest/skipping.html
.. _Issue Tracker: http://github.com/davehunt/pytest-base-url/issues
.. _Code: http://github.com/davehunt/pytest-base-url
