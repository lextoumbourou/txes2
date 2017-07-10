.. _usage:

Usage Example
==============

::

    from pprint import pprint
    
    from twisted.internet import reactor
    from twisted.internet.defer import inlineCallbacks
    
    from txes2 import Elasticsearch
    
    
    @inlineCallbacks
    def example():
        index = 'main'
        doc_type = 'person'
    
        ########################
        # Setup connection
        ########################
        es = Elasticsearch('127.0.0.1:9200')
    
        ########################
        # Index a document
        ########################
        document = {'name': 'Travis Bickle', 'tagline': 'You talking to me?'}
        yield es.index(document, doc_type=doc_type, index=index, id=123)
    
        ########################
        # Retrieve a document
        ########################
        result = yield es.get(index=index, doc_type=doc_type, id=123)
        pprint(result)
    
        ########################
        # Refresh an index
        ########################
        yield es.refresh(index)
    
        ########################
        # Perform a query
        ########################
        query = {'query': {'match': {'name': 'Travis'}}}
        results = yield es.search(query, doc_type=doc_type, index=index)
        pprint(results)
    
    
    if __name__ == '__main__':
        df = example()
        df.addErrback(lambda err: err.printTraceback())
        df.addCallback(lambda _: reactor.stop())
        reactor.run()
