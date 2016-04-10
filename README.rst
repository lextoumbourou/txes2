txes2
=====

A Twisted ElasticSearch client loosely based on PyES.

|travis| |coveralls| |docs|

|code_issues| 

.. |travis| image:: https://travis-ci.org/lextoumbourou/txes2.svg?branch=master
   :target: https://travis-ci.org/lextoumbourou/txes2
.. |coveralls| image:: https://coveralls.io/repos/lextoumbourou/txes2/badge.png?branch=master
   :target: https://coveralls.io/r/lextoumbourou/txes2?branch=master
.. |code_issues| image:: http://www.quantifiedcode.com/api/v1/project/407655c0058649998742e2bb654db68e/badge.svg
   :target: http://www.quantifiedcode.com/app/project/407655c0058649998742e2bb654db68e
.. |docs| image:: https://readthedocs.org/projects/txes2/badge/?version=latest
   :target: https://readthedocs.org/projects/txes2/?badge=latest

Before We Begin
---------------

This repo is simply a fork of `txes <https://github.com/jkoelker/txes>`_, however, the API has changed enough that I believe a name change was warranted. I also am not representing it as a fork on Github to avoid getting it confused with the 12 other forks of txes that have taken the software in different directions. So for clarity: I am not the original author of this library, `jkoelker <https://github.com/jkoelker>`_ is. Thanks to all the other contributers who helped make this happen, listed in the Contributors_ section.


Documentation
-------------

Available at `Read The Docs <https://txes2.readthedocs.org/en/latest/>`_.


.. _Contributors:

License
-------

BSD (as per original project).


Changelog
---------

0.5.0
^^^^^

- Add support for HTTP auth (for people using Shield or Nginx in front of ES).
- Add support for HTTPS.

0.4.0
^^^^^

- Add support for ``script_file`` arg in ``partial_update`` (thanks @bra-fsn). 
- Ensure master-only nodes aren't included during Discovery (thanks @zsiddique).

0.3.0
^^^^^

- Fixed ``scan`` method (thanks @bra-fsn) and deprecated old methods.
- Various bug fixes and test coverage increases.

0.2.3
^^^^^

- Check for connection pool before attempting to close it.
- Fixed incorrect method names.
- Small documentation fixes.

0.2.2
^^^^^

- Fixed small bug in ``partial_update`` method.

0.2.1
^^^^^

- Added ``partial_update`` method.

0.2.0
^^^^^

- Ensure ``query_params`` is used consistently across API.
- Lots of test coverage.
- Remove legacy methods.
- Improved support for ES v1.x.

0.1.8
^^^^^

- Removed pip internals from setup.py all together.

0.1.7
^^^^^

- Ensure url path components are quoted.
- Fixed used of Pip session (thanks @reversefold).

0.1.6
^^^^^

- Fixed issue with setup.py on Pip versions > 6.

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
