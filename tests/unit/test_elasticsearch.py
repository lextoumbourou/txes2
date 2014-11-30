"""Tests for the ElasticSearch class."""

from mock import patch
from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks, succeed

from txes2.elasticsearch import ElasticSearch


class ElasticSearchTest(TestCase):

    """Tests for the ElasticSearch class."""

    @patch('txes2.elasticsearch.connection')
    def setUp(self, conn_mock):
        self.es = ElasticSearch('127.0.0.1:9200', discover=False)

    @inlineCallbacks
    def test_mget(self):
        self.es.connection.execute.return_value = succeed(dict(
            docs=[{
                "_index": "my_index", "_type": "my_doc",
                "_id": 1, "_version": 1, "found": True,
                "_source": {"id": 1}}
            ])
        )
        result = yield self.es.mget([1], 'my_index', 'my_doc')
        self.assertTrue(result['docs'][0]['_id'] == 1)
