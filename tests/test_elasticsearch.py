"""Tests for the ElasticSearch class."""

import uuid
import os
from mock import Mock

from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks, succeed

from txes2.elasticsearch import ElasticSearch
from txes2.exceptions import ElasticSearchException, NotFoundException

from . import settings


def use_mock():
    return os.getenv('USE_MOCKS')


class ElasticSearchTest(TestCase):

    """Tests for the ElasticSearch class."""

    def _get_mock(self, *args, **kwargs):
        return self._mock

    @inlineCallbacks
    def setUp(self):
        self.es = ElasticSearch(
            settings.URL, discover=False,
            discovery_interval=False, persistent=False)
        if use_mock():
            self.es.connection.execute = Mock()
            self.es.connection.execute = self._get_mock
        else:
            pass
            try:
                yield self.es.create_index(settings.INDEX)
            except ElasticSearchException:
                pass

    @inlineCallbacks
    def test_add_alias(self):
        self._mock = {'acknowledged': True}

        result = yield self.es.add_alias('test_alias', settings.INDEX)
        self.assertTrue('acknowledged' in result)

    @inlineCallbacks
    def test_analyze(self):
        self._mock = {'tokens': [
            {'end_offset': 6, 'token': u'text'},
            {'end_offset': 15, 'token': 'hello'},
            {'end_offset': 21, 'token': 'world'}]}

        result = yield self.es.analyze('Hello world', settings.INDEX)
        self.assertTrue('tokens' in result)
        self.assertTrue(len(result['tokens']) == 3)

    def test_can_handle_basestring_input(self):
        tmp_es = ElasticSearch(
            'server', default_indexes='index', discover=False)
        self.assertTrue(isinstance(tmp_es.connection.servers, list))
        self.assertTrue(isinstance(tmp_es.default_indexes, list))

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
    def test_cluster_nodes(self):
        self._mock = {'cluster_name': 'test', 'nodes': {'id1': {}, 'id2': {}}}

        result = yield self.es.cluster_nodes()
        self.assertTrue(len(result['nodes']) == 2)

    @inlineCallbacks
    def test_cluster_state(self):
        # Ensure metric filtering works
        self._mock = {'cluster_name': 'test', 'blocks': {}}

        result = yield self.es.cluster_state(metrics=['blocks'])
        self.assertTrue('metadata' not in result)

        self._mock = {
            'cluster_name': 'test', 'blocks': {},
            'routing_table': {'indices': {}}}

        random_index_name = uuid.uuid4()
        result = yield self.es.cluster_state(indices=[random_index_name.hex])
        self.assertTrue(
            settings.INDEX not in result['routing_table']['indices'])

        self._mock = {
            'cluster_name': 'test', 'metadata': {},
            'routing_table': {'indices': {settings.INDEX: {}}}}

        result = yield self.es.cluster_state()
        self.assertTrue(
            'metadata' in result and
            settings.INDEX in result['routing_table']['indices'])

    @inlineCallbacks
    def test_collect_info(self):
        self._mock = {
            'status': 200, 'cluster_name': 'test', 'version': {},
            'name': 'Jester', 'tagline': 'You Know, for Search'}

        result = yield self.es.collect_info()
        self.assertTrue('server' in result)
        self.assertTrue('allinfo' in result)

    @inlineCallbacks
    def test_count(self):
        self._mock = {'count': 11, '_shards': {}}

        result = yield self.es.count(
            {'query': {'match': {'name': 'Some Doc'}}})
        self.assertTrue('count' in result)
        self.assertTrue(isinstance(result['count'], int))

    @inlineCallbacks
    def test_create_and_delete_river(self):
        self._mock = {'_type': 'twitter', 'created': True}

        river_data = {
            'type': 'twitter',
            'twitter': {'user': 'blah'},
            'index': {
                'index': 'twitter',
            }
        }

        result = yield self.es.create_river(river_data)
        self.assertTrue(result['_type'] == 'twitter')

        self._mock = {'acknowledged': True}

        result = yield self.es.delete_river(river_data)
        self.assertTrue(result['acknowledged'])

    @inlineCallbacks
    def test_create_index(self):
        self._mock = {'acknowledged': True}

        index_name = uuid.uuid4()
        result = yield self.es.create_index(index_name)
        self.assertTrue(result['acknowledged'])

    @inlineCallbacks
    def test_delete(self):
        self._mock = {'found': True, '_id': '2'}

        data = {'id': 2, 'name': 'Some Doc'}
        yield self.es.index(data, settings.INDEX, settings.DOC_TYPE, id=2)
        result = yield self.es.delete(settings.INDEX, settings.DOC_TYPE, id=2)
        self.assertTrue(result['found'])
        self.assertTrue(result['_id'] == '2')

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
    def test_delete_index(self):
        self._mock = {'acknowledged': True}

        result = yield self.es.delete_index(settings.INDEX)
        self.assertTrue(result['acknowledged'])

    @inlineCallbacks
    def test_delete_mapping(self):
        self._mock = {'acknowledged': True}

        yield self.es.index(
            doc_type=settings.DOC_TYPE, index=settings.INDEX, id=1,
            doc={'name': 'Hello breh'})
        # Fixes the race condition that occurs when trying to
        # delete doc that doesn't exist yet.
        yield self.es.refresh(settings.INDEX)

        result = yield self.es.delete_mapping(
            settings.INDEX, settings.DOC_TYPE)

        self.assertTrue(result['acknowledged'])

    @inlineCallbacks
    def test_flush(self):
        self._mock = {'_shards': {'successful': 72, 'failed': 0, 'total': 72}}

        result = yield self.es.flush(
            settings.INDEX, wait_if_ongoing=True, force=True)
        self.assertTrue('_shards' in result)
        self.assertFalse(result['_shards']['failed'])

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
    def test_get_indices(self):
        self._mock = {}

        if use_mock():
            self.es.cluster_state = Mock()
            self.es.cluster_state.side_effect = lambda: succeed({
                'metadata': {'indices': {
                    settings.INDEX: {
                        'aliases': {'test_alias': {
                            'docs': {'num_docs': 2}
                        }},
                        'docs': {'num_docs': 2},
                    }
                }}
            })

            self.es.status = Mock()
            self.es.status.side_effect = lambda: succeed({
                'indices': {settings.INDEX: {
                    'docs': {'num_docs': 2}}}
            })

        yield self.es.add_alias('test_alias', settings.INDEX)
        yield self.es.index(
            {'name': 'Blah'}, doc_type=settings.DOC_TYPE, index=settings.INDEX,
            refresh=True)
        result = yield self.es.get_indices(include_aliases=True)

        self.assertTrue(result['test_alias']['num_docs'] > 0)
        self.assertTrue(settings.INDEX in result['test_alias']['alias_for'])

        result = yield self.es.get_indices(include_aliases=False)
        self.assertTrue('test_alias' not in result)
        self.assertTrue(settings.INDEX in result)

    @inlineCallbacks
    def test_get_mapping(self):
        self._mock = {'test_index': {'mappings': {}}}
        result = yield self.es.get_mapping(settings.DOC_TYPE, settings.INDEX)
        self.assertTrue(settings.INDEX in result)
        self.assertTrue('mappings' in result[settings.INDEX])

    @inlineCallbacks
    def test_index(self):
        self._mock = {u'_type': u'test_doc', u'_id': 1, u'created': True}

        data = {'id': 1, 'name': 'Some Doc'}
        result = yield self.es.index(data, settings.INDEX, settings.DOC_TYPE)
        self.assertTrue(result['created'])

    @inlineCallbacks
    def test_index_bulk(self):
        self._mock = {
            'errors': False,
            'items': [
                {'create': {'_id': 'AUuM_KMFMQEOMq5Ak3hH'}},
                {'create': {'_id': 'AUuM_KMFMQEOMq5Ak3hI'}}]
        }

        self.es.bulk_size = 2

        doc = {'name': 'Hello 1'}
        result = yield self.es.index(
            doc=doc, doc_type=settings.DOC_TYPE,
            index=settings.INDEX, bulk=True)
        self.assertTrue(result is None)

        doc = {'name': 'Hello 2'}
        result = yield self.es.index(
            doc=doc, doc_type=settings.DOC_TYPE,
            index=settings.INDEX, bulk=True)

        self.assertFalse(result['errors'])
        self.assertTrue(len(result['items']) == 2)

    @inlineCallbacks
    def test_mget(self):
        self._mock = dict(docs=[{
            "_index": "my_index", "_type": "my_doc",
            "_id": 1, "_version": 1, "found": True,
            "_source": {"id": 1}}])

        result = yield self.es.mget([1], settings.INDEX, settings.DOC_TYPE)
        self.assertTrue('docs' in result)

        result = yield self.es.mget(
            [(settings.INDEX, settings.DOC_TYPE, 1),
             (settings.INDEX, settings.DOC_TYPE, 1, ['name'])])
        self.assertTrue('docs' in result)

    @inlineCallbacks
    def test_more_like_this(self):
        self._mock = {'hits': {}}
        yield self.es.index(
            {'name': 'Blah'}, id=1,
            doc_type=settings.DOC_TYPE, index=settings.INDEX,
            refresh=True)
        yield self.es.index(
            {'name': 'Blah'}, id=2,
            doc_type=settings.DOC_TYPE, index=settings.INDEX,
            refresh=True)

        result = yield self.es.more_like_this(
            settings.INDEX, settings.DOC_TYPE, id=1, fields=['name'])

        self.assertTrue('hits' in result)

    @inlineCallbacks
    def test_optimize(self):
        self._mock = {'_shards': {'successful': 10, 'failed': 0, 'total': 10}}

        result = yield self.es.optimize(settings.INDEX, max_num_segments=1)
        self.assertTrue('_shards' in result)
        self.assertTrue(result['_shards']['failed'] == 0)

    @inlineCallbacks
    def test_partial_update(self):
        self._mock = {'_source': {'tags': ['tag1', 'tag2']}}

        yield self.es.index(
            doc_type=settings.DOC_TYPE, index=settings.INDEX, id=1,
            doc={'name': 'Hello breh', 'tags': ['tag1']})

        yield self.es.partial_update(
            index=settings.INDEX, doc_type=settings.DOC_TYPE, id=1,
            script='ctx._source.tags+=new_tag', params={'new_tag': 'tag2'})

        result = yield self.es.get(
            index=settings.INDEX, doc_type=settings.DOC_TYPE, id=1)

        self.assertTrue(result['_source']['tags'] == ['tag1', 'tag2'])

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

    @inlineCallbacks
    def test_perform_discovery(self):
        self.es.cluster_nodes = Mock()
        self.es.cluster_nodes.return_value = succeed(
            {'cluster_name': 'test',
             'nodes': {
                 'node-1': {'http_address': 'inet[/10.0.0.1:9200]'},
                 'node-2': {'http_address': 'inet[/10.0.0.2:9200]'},
             }})
        yield self.es._perform_discovery()
        self.assertTrue(len(self.es.connection.servers) == 4)

    @inlineCallbacks
    def test_put_mapping(self):
        self._mock = {'acknowledged': True}

        mapping = {'properties': {'name': {'type': 'string'}}}
        result = yield self.es.put_mapping(settings.DOC_TYPE, mapping)
        self.assertTrue(result['acknowledged'])

    @inlineCallbacks
    def test_refresh(self):
        self._mock = {'_shards': {'successful': 10}}

        result = yield self.es.refresh(settings.INDEX)
        self.assertTrue('_shards' in result)
        self.assertTrue(result['_shards']['successful'])

    @inlineCallbacks
    def test_scan(self):
        self._mock = {'hits': {'hits': []}, '_scroll_id': '1234'}

        query = {'query': {'term': {'name': 'blah'}}}
        scroller = yield self.es.scan(query, settings.INDEX, settings.DOC_TYPE)
        self.assertTrue('_scroll_id' in scroller.results)

    @inlineCallbacks
    def test_set_alias(self):
        def side_effect(*args, **kwargs):
            if args[0] == 'POST' and args[1] == '_aliases':
                return {'acknowledged': True}
            else:
                return {'indices': {'test_index': {}}}

        if use_mock():
            self.es.connection = Mock()
            self.es.connection.execute.side_effect = side_effect

        result = yield self.es.set_alias('test_alias', settings.INDEX)
        self.assertTrue(result['acknowledged'])

    @inlineCallbacks
    def test_status(self):
        self._mock = {
            'indices': {settings.INDEX: {'docs': {}}, 'shards': []}}

        result = yield self.es.status(settings.INDEX)
        self.assertTrue('indices' in result)
        self.assertTrue(settings.INDEX in result['indices'])

    @inlineCallbacks
    def test_update_settings(self):
        self._mock = {'acknowledged': True}

        data = {'index': {'refresh_interval': 10}}
        result = yield self.es.update_settings(settings.INDEX, data)
        self.assertTrue(result['acknowledged'])
