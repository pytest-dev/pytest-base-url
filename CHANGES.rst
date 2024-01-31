Release Notes
-------------

**2.1.0 (2024-01-31)**

* Drop support for python 3.7

* Add support for python 3.11 - 3.12

* Add support for ``pytest-metadata`` 3.x

* Switch to Hatch

**2.0.0 (2022-03-27)**

* Drop python 2.7 and 3.6 support

* Switch to pyproject.toml and Poetry

**1.4.2 (2020-06-20)**

* Lazy load requests dependency to reduce cost

  * Thanks to `@boxed <https://github.com/boxed>`_ for the PR

* Fixed compatibility with ``pytest-xdist`` 2.0+ (supporting >= 1.22.3)

  * Thanks to `@Zac-HD <https://github.com/Zac-HD>`_ for the PR

**1.4.1 (2017-06-22)**

* Update dependency of requests to require v2.9 or later.

**1.4.0 (2017-06-12)**

* Add verify base URL timeouts

  * Thanks to `@jrbenny35 <https://github.com/jrbenny35>`_ for the PR

**1.3.0 (2017-02-27)**

* Add base URL to metadata provided by
  `pytest-metadata <https://pypi.python.org/pypi/pytest-metadata/>`_.

**1.2.0 (2016-11-17)**

* Added support for specifying the base URL by environment variable

  * Thanks to `@m8ttyB <https://github.com/m8ttyB>`_ for the PR

**1.1.0 (2016-07-07)**

* Added base URL to report header

**1.0.0 (2016-05-10)**

* Initial release
