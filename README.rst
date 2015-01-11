txes2
=====

A Twisted ElasticSearch client loosely based on PyES.

|travis| |coveralls| |pypi| |docs|

.. |travis| image:: https://travis-ci.org/lextoumbourou/txes2.svg?branch=master
   :target: https://travis-ci.org/lextoumbourou/txes2
.. |coveralls| image:: https://coveralls.io/repos/lextoumbourou/txes2/badge.png?branch=master
   :target: https://coveralls.io/r/lextoumbourou/txes2?branch=master
.. |pypi| image:: https://pypip.in/version/txes2/badge.svg
   :target: https://pypi.python.org/pypi/txes2/
.. |docs| image:: https://readthedocs.org/projects/txes2/badge/?version=latest
   :target: https://readthedocs.org/projects/txes2/?badge=latest

Before We Begin
---------------

This repo is simply a fork of `txes <https://github.com/jkoelker/txes>`_, however, the API has changed enough that I believe a name change was warranted. I also am not representing it as a fork on Github to avoid getting it confused with the 12 other forks of txes that have taken the software in different directions. So for clarity: I am not the original author of this library, `jkoelker <https://github.com/jkoelker>`_ is. Thanks to all the other contributers who helped make this happen, listed in the `Contributors <https://github.com/lextoumbourou/txes2#contributors>`_ section.


Documentation
-------------

Available at `Read The Docs <https://txes2.readthedocs.org/en/latest/>`_.


.. _contributors:

License
-------

BSD (as per original project).


Changelog
---------

0.1.5
^^^^^

- Fixed ``scan`` method.
- Increased test coverage.

0.1.4
^^^^^

- Fixed ``delete_by_query`` method.
- Increased test coverage.
- Removed ``reindex`` method (relied on an obscure fork of ES).

0.1.3
^^^^^

- Split requirements into main/dev.
- Use treq's persistent arg if no pool passed in.
- Fixed broken requirements path.
- Doc updates.

0.1.0
^^^^^

- PEP8ified API.
- Added docs, tests & PyPi.


Contributors
------------

If you contribute to this project, feel free to add your name and/or Github username here.

* `Jason Kölker (@jkoelker) <https://github.com/jkoelker>`_ - original author
* `Zuhaib Siddique (@zsiddique) <https://github.com/zsiddique>`_
* `Lex Toumbourou (@lextoumbourou) <https://github.com/lextoumbourou>`_ - current maintainer
