txes2
=====

A PyES compatible-ish ElasticSearch Twisted client.

Before We Begin
---------------

This repo is simply a fork a `txes <https://github.com/jkoelker/txes>`, however, the API has changed enough that I believe a name change was warranted. I also am not representing it as a fork on Github to avoid getting it confused with the 12 other forks of txes that have taken the software in different directions. So for clarify: **I am not the original author of this library, `jkoelker <https://github.com/jkoelker>` is. Thanks to all the other contributers who helped make this happen, listed in the :ref:`contributors`  section**.

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

Contributors
------------

* `Jason Kölker <https://github.com/jkoelker>` - original author
* `Zuhaib Siddique <https://github.com/zsiddique>`
* `Lex Toumbourou <https://github.com/lextoumbourou>` - current maintainer
