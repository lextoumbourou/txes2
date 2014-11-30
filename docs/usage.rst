.. _usage:

Usage
=====

Creating a connection:

::

    >>> from txes2 import ElasticSearch
    >>> conn = ElasticSearch('127.0.0.1:9200')

Indexing a document:

::

    >>> def handle_result(data):
        ...  print 'Result indexed!'

    >>> d = conn.index(
        ...    {'name': 'Travis Bickle',
                'tagline': 'All my life needed was a sense of some place to go.'},
               doc_type='person', index='users')
    >>> d.addCallback(handle_result)

Refreshing indexes:

::

    >>> conn.refresh('users')
