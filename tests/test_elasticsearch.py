"""Integration tests for the ElasticSearch class."""

import os
from mock import Mock

from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks

from txes2.elasticsearch import ElasticSearch
from txes2.exceptions import ElasticSearchException

from . import settings


def use_mock():
    return os.getenv('USE_MOCKS')


class ElasticSearchIntegrationTest(TestCase):

    """Tests for the ElasticSearch class."""

    def _get_mock(self, *args, **kwargs):
        return self._mock

    @inlineCallbacks
    def setUp(self):
        self.es = ElasticSearch(
            settings.URL, discover=False, discover_interval=False)
        if use_mock():
            self.es.connection = Mock()
            self.es.connection.execute = self._get_mock
        else:
            try:
                yield self.es.create_index(settings.INDEX)
            except ElasticSearchException:
                pass

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

    @inlineCallbacks
    def test_analyze(self):
        self._mock = {'tokens': [
            {'end_offset': 6, 'token': u'text'},
            {'end_offset': 15, 'token': 'hello'},
            {'end_offset': 21, 'token': 'world'}]}

        result = yield self.es.analyze('Hello world', settings.INDEX)
        self.assertTrue('tokens' in result)
        self.assertTrue(len(result['tokens']) == 3)

    @inlineCallbacks
    def test_delete(self):
        self._mock = {'found': True, '_id': '2'}

        data = {'id': 2, 'name': 'Some Doc'}
        yield self.es.index(data, settings.INDEX, settings.DOC_TYPE, id=2)
        result = yield self.es.delete(settings.INDEX, settings.DOC_TYPE, id=2)
        self.assertTrue(result['found'])
        self.assertTrue(result['_id'] == '2')

    @inlineCallbacks
    def test_get(self):
        self._mock = {
            '_source': {'id': 3, 'name': 'Some Doc'},
            '_index': 'test_index', 'found': True}

        data = {'id': 3, 'name': 'Some Doc'}
        yield self.es.index(data, settings.INDEX, settings.DOC_TYPE, id=3)
        result = yield self.es.get(settings.INDEX, settings.DOC_TYPE, 3)
        self.assertTrue(result['found'])
        self.assertTrue('_source' in result)
