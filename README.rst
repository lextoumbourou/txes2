txes2
=====

A PyES compatible-ish ElasticSearch Twisted client.

|travis| |coveralls|

.. |travis| image:: https://travis-ci.org/lextoumbourou/txes2.svg?branch=master
   :target: https://travis-ci.org/lextoumbourou/txes2
.. |coveralls| image:: https://coveralls.io/repos/lextoumbourou/txes2/badge.png?branch=master
   :target: https://coveralls.io/r/lextoumbourou/txes2?branch=master

Before We Begin
---------------

This repo is simply a fork of `txes <https://github.com/jkoelker/txes>`_, however, the API has changed enough that I believe a name change was warranted. I also am not representing it as a fork on Github to avoid getting it confused with the 12 other forks of txes that have taken the software in different directions.

So for clarify: **I am not the original author of this library**, `jkoelker <https://github.com/jkoelker>`_ is. Thanks to all the other contributers who helped make this happen, listed in the `Contributors <https://github.com/lextoumbourou/txes2#contributors>`_  section.

Status
------

WIP - not yet production ready.

Documentation
-------------

Coming soon.

Running Tests
-------------

Unit
^^^^

::

    trial tests/unit

Integration
^^^^^^^^^^^

Requires ElasticSearch to be running locally.

::

    trial tests/integration


.. _contributors:

Contributors
------------

If you contribute to this project, feel free to add your name and/or Github username here.

* `Jason Kölker (@jkoelker) <https://github.com/jkoelker>`_ - original author
* `Zuhaib Siddique (@zsiddique) <https://github.com/zsiddique>`_
* `Lex Toumbourou (@lextoumbourou) <https://github.com/lextoumbourou>`_ - current maintainer
