gRPC Access Log
===============

|PyPI| |Status| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/grpc-accesslog.svg
   :target: https://pypi.org/project/grpc-accesslog/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/grpc-accesslog.svg
   :target: https://pypi.org/project/grpc-accesslog/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/grpc-accesslog
   :target: https://pypi.org/project/grpc-accesslog
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/grpc-accesslog
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/grpc-accesslog/latest.svg?label=Read%20the%20Docs
   :target: https://grpc-accesslog.readthedocs.io/
   :alt: Read the documentation at https://grpc-accesslog.readthedocs.io/
.. |Tests| image:: https://github.com/villainy/grpc-accesslog/workflows/Tests/badge.svg
   :target: https://github.com/villainy/grpc-accesslog/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/villainy/grpc-accesslog/branch/main/graph/badge.svg
   :target: https://app.codecov.io/gh/villainy/grpc-accesslog
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black


Features
--------

* Write stdout logs for every RPC request
* Log messages built with customizable callback handlers


Requirements
------------

* Python 3.9+


Installation
------------

You can install *gRPC Access Log* via pip_ from PyPI_:

.. code:: console

   $ pip install grpc-accesslog


Usage
-----

Please see the `Reference <Usage_>`_ for details.


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `MIT license`_,
*gRPC Access Log* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.

.. _@cjolowicz: https://github.com/cjolowicz
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _MIT license: https://opensource.org/licenses/MIT
.. _PyPI: https://pypi.org/
.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _file an issue: https://github.com/villainy/grpc-accesslog/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: https://grpc-accesslog.readthedocs.io/en/latest/contributing.html
.. _Usage: https://grpc-accesslog.readthedocs.io/en/latest/usage.html
