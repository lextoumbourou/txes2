"""Integration tests for the ElasticSearch class."""

from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks

from txes2.elasticsearch import ElasticSearch

from . import settings


class ElasticSearchIntegrationTest(TestCase):

    """Tests for the ElasticSearch class."""

    def setUp(self):
        self.es = ElasticSearch(
            settings.URL, discover=False, discover_interval=False)

    def tearDown(self):
        """Close persistent connections to keep Reactor clean."""
        self.es.connection.close()

    @inlineCallbacks
    def test_cluster_nodes(self):
        result = yield self.es.cluster_nodes()
        self.assertTrue(len(result['nodes']) == 2)

    @inlineCallbacks
    def test_index(self):
        data = {'id': 1, 'name': 'Some Doc'}
        result = yield self.es.index(data, settings.INDEX, settings.DOC_TYPE)
        self.assertTrue(result['created'])

    @inlineCallbacks
    def test_mget(self):
        result = yield self.es.mget([1], settings.INDEX, settings.DOC_TYPE)
        self.assertTrue('docs' in result)
