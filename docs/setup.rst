.. _setup:

Setup
=====


Installing via pip
------------------

::

    $ pip install txes2


Installing from source
----------------------

Clone repository and run ``setup.py``

::

    $ git clone git@github.com:lextoumbourou/txes2.git
    $ cd txes2
    $ python setup.py install


Running tests
-------------

Unit
^^^^

::

    ./bin/unit

Integration
^^^^^^^^^^^

1. Start Vagrant box, which runs an ElasticSearch cluster with ports ``9210`` and ``9211`` forwarded to the separate ElasticSearch instances.

::

    vagrant up --provision

2. Run integration tests.

::

    ./bin/integration
