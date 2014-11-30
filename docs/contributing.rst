.. _contributing:

Contributing
============

Style Guide
-----------

All code should pass through `flake8 <http://flake8.readthedocs.org/en/2.2.3/>`_. This will be enforced at build time by Travis.

Writing Tests
-------------

Please ensure any new functionality has tests written for it. The tests are designed to be run as both integration tests or units tests depending on the existance of the ``USE_MOCKS`` environment variable. When run as unit tests, the ``self._mocks`` attribute should be populated with the dict expected to be returned by the ``txes2.ElasticSearch.connection.execute`` method. Refer to already written test for examples.
