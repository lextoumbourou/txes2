"""Integration tests for the ElasticSearch class."""

import os
from mock import Mock

from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks

from txes2.elasticsearch import ElasticSearch

from . import settings


def use_mock():
    return os.getenv('USE_MOCKS')


class ElasticSearchIntegrationTest(TestCase):

    """Tests for the ElasticSearch class."""

    def _get_mock(self, *args, **kwargs):
        return self._mock

    def setUp(self):
        self.es = ElasticSearch(
            settings.URL, discover=False, discover_interval=False)
        if use_mock():
            self.es.connection = Mock()
            self.es.connection.execute = self._get_mock

    def tearDown(self):
        """Close persistent connections to keep Reactor clean."""
        self.es.connection.close()

    @inlineCallbacks
    def test_cluster_nodes(self):
        self._mock = {'cluster_name': 'test', 'nodes': {'id1': {}, 'id2': {}}}

        result = yield self.es.cluster_nodes()
        self.assertTrue(len(result['nodes']) == 2)

    @inlineCallbacks
    def test_index(self):
        self._mock = {u'_type': u'test_doc', u'_id': 1, u'created': True}

        data = {'id': 1, 'name': 'Some Doc'}
        result = yield self.es.index(data, settings.INDEX, settings.DOC_TYPE)
        self.assertTrue(result['created'])

    @inlineCallbacks
    def test_mget(self):
        self._mock = dict(docs=[{
            "_index": "my_index", "_type": "my_doc",
            "_id": 1, "_version": 1, "found": True,
            "_source": {"id": 1}}])

        result = yield self.es.mget([1], settings.INDEX, settings.DOC_TYPE)
        self.assertTrue('docs' in result)
