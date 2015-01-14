"""Tests for the ElasticSearch class."""

import os
from mock import Mock

from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks

from txes2.elasticsearch import ElasticSearch
from txes2.exceptions import ElasticSearchException, NotFoundException

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
            settings.URL, discover=False,
            discover_interval=False, persistent=False)
        if use_mock():
            self.es.connection = Mock()
            self.es.connection.execute = self._get_mock
        else:
            try:
                yield self.es.create_index(settings.INDEX)
            except ElasticSearchException:
                pass

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

    @inlineCallbacks
    def test_status(self):
        self._mock = {
            'indices': {settings.INDEX: {'docs': {}}, 'shards': []}}

        result = yield self.es.status(settings.INDEX)
        self.assertTrue('indices' in result)
        self.assertTrue(settings.INDEX in result['indices'])

    @inlineCallbacks
    def test_get_indices(self):
        self._mock = {'indices': {settings.INDEX: {'docs': {'num_docs': 1}}}}

        result = yield self.es.get_indices(include_aliases=True)
        self.assertTrue(settings.INDEX in result)

    @inlineCallbacks
    def test_count(self):
        self._mock = {'count': 11, '_shards': {}}

        result = yield self.es.count(
            {'query': {'match': {'name': 'Some Doc'}}})
        self.assertTrue('count' in result)
        self.assertTrue(isinstance(result['count'], int))

    @inlineCallbacks
    def test_cluster_health(self):
        self.assertRaises(ValueError, self.es.cluster_health, 'blah')

        self._mock = {'status': 'green', 'number_of_nodes': 2}

        result = yield self.es.cluster_health(
            wait_for_status='green', wait_for_relocating_shards=True,
            wait_for_nodes=True)
        self.assertTrue('status' in result)
        self.assertTrue(result['number_of_nodes'] == 2)

    @inlineCallbacks
    def test_get_mapping(self):
        self._mock = {'test_index': {'mappings': {}}}
        result = yield self.es.get_mapping(settings.DOC_TYPE, settings.INDEX)
        self.assertTrue(settings.INDEX in result)
        self.assertTrue('mappings' in result[settings.INDEX])

    @inlineCallbacks
    def test_collect_info(self):
        self._mock = {
            'status': 200, 'cluster_name': 'test', 'version': {},
            'name': 'Jester', 'tagline': 'You Know, for Search'}

        result = yield self.es.collect_info()
        self.assertTrue('server' in result)
        self.assertTrue('allinfo' in result)

    @inlineCallbacks
    def test_add_alias(self):
        self._mock = {'acknowledged': True}

        result = yield self.es.add_alias('test_alias', settings.INDEX)
        self.assertTrue('acknowledged' in result)

    @inlineCallbacks
    def test_optimize(self):
        self._mock = {'_shards': {'successful': 10, 'failed': 0, 'total': 10}}

        result = yield self.es.optimize(settings.INDEX, max_num_segments=1)
        self.assertTrue('_shards' in result)
        self.assertTrue(result['_shards']['failed'] == 0)

    @inlineCallbacks
    def test_delete_by_query(self):
        def raise_exception(*args, **kwargs):
            raise NotFoundException('Item not found')

        self._mock = {'_id': 'someid'}
        data = {'name': 'blah'}
        result = yield self.es.index(data, settings.INDEX, settings.DOC_TYPE)
        doc_id = result['_id']

        self._mock = {'_id': 'someid', 'found': True}
        result = yield self.es.get(
            settings.INDEX, settings.DOC_TYPE, id=doc_id)
        self.assertTrue(result['found'])

        self._mock = {}
        query = {'term': {'name': 'blah'}}
        result = yield self.es.delete_by_query(
            settings.INDEX, settings.DOC_TYPE, query)

        if use_mock():
            # Reset mock
            self.es.connection.execute = Mock()
            self.es.connection.execute.side_effect = raise_exception

        has_failed = False
        try:
            yield self.es.get(
                settings.INDEX, settings.DOC_TYPE, id=doc_id)
        except NotFoundException:
            has_failed = True

        self.assertTrue(has_failed)

    @inlineCallbacks
    def test_scan(self):
        self._mock = {'hits': {'hits': []}, '_scroll_id': '1234'}

        query = {'query': {'term': {'name': 'blah'}}}
        scroller = yield self.es.scan(query, settings.INDEX, settings.DOC_TYPE)
        self.assertTrue('_scroll_id' in scroller.results)

    @inlineCallbacks
    def test_path_is_encoded_properly(self):
        data = {'name': 'Yo breh'}
        test_id = 'some/id'

        self._mock = {'_id': test_id}

        yield self.es.index(
            data, settings.INDEX, '{}-2'.format(settings.DOC_TYPE), id=test_id)
        result = yield self.es.get(
            settings.INDEX, '{}-2'.format(settings.DOC_TYPE), id=test_id)

        self.assertTrue(result['_id'] == test_id)
