from urllib import quote

import anyjson
from twisted.internet import defer, reactor

from . import connection, exceptions


class ElasticSearch(object):

    """A PyES-like ElasticSearch client."""

    def __init__(self, servers='127.0.0.1:9200', timeout=30, bulk_size=400,
                 discover=True, retry_time=10, discovery_interval=300,
                 default_indexes=None, autorefresh=False, *args, **kwargs):
        """
        :param servers: either a single ES server URL or list of servers.
        :param int timeout: connection timeout in seconds.
        :param int bulk_size: how much bulk data to accumulate before indexing
                              (when indexing in bulk).
        :param int retry_time: frequency in seconds for retrying broken ES
                               nodes.
        :param bool discover: if True, will autodiscover ES nodes at
                              connection time.
        :param bool discovery_interval: time in seconds between node discovery
                                        after initial discovery, set to False
                                        to skip.
        :param list default_indexes: list of indexes to use by default when
                                     querying ES.
        :param bool autorefresh: should we perform index autorefresh.
        :param bool persistent: use persistent connection.
        :param HTTPConnectionPool pool: optionally pass in HTTPConnectionPool
                                        instance to use for connection pool.
        """
        if isinstance(servers, basestring):
            servers = [servers]
        else:
            servers = servers

        if not default_indexes:
            default_indexes = ['_all']
        elif isinstance(default_indexes, basestring):
            default_indexes = [default_indexes]

        self.default_indexes = default_indexes
        self.timeout = timeout
        self.bulk_size = bulk_size
        self.discovery_interval = discovery_interval
        self.autorefresh = autorefresh
        self.refreshed = True

        self.info = {}
        self.bulk_data = []

        self.connection = connection.connect(
            servers=servers, timeout=timeout, retry_time=retry_time,
            *args, **kwargs)
        if discover:
            self._perform_discovery()

    def _make_path(self, components):
        """Build a path from a list of components."""
        return '/' + '/'.join([quote(str(c), '') for c in components if c])

    def _perform_discovery(self):
        def cb(data):
            self.cluster_name = data['cluster_name']
            for node in data['nodes']:
                http_addr = data['nodes'][node].get('http_address')
                if not http_addr:
                    continue

                server = http_addr.strip('inet[/]')
                self.connection.addServer(server)

            if self.discovery_interval:
                reactor.callLater(
                    self.discovery_interval, self._perform_discovery)

        d = self.cluster_nodes()
        d.addCallback(cb)
        return d

    def _send_query(
        self, query_type, query, indexes=None, doc_types=None, **params
    ):
        """Send query to ES."""
        def send_it(result=None):
            indices = self._validate_indexes(indexes)
            dt = doc_types
            if dt is None:
                dt = []
            elif isinstance(dt, basestring):
                dt = [dt]
            path = self._make_path(
                [','.join(indices), ','.join(dt), query_type])
            d = self._send_request('GET', path, body=query, params=params)
            return d

        if self.autorefresh and not self.refreshed:
            d = self.refresh(indexes)
            d.addCallback(send_it)
            return d
        else:
            return send_it()

    def _send_request(self, method, path, body=None, params=None):
        d = defer.maybeDeferred(self.connection.execute,
                                method, str(path), body, params)
        return d

    def _validate_indexes(self, indexes=None):
        indices = indexes or self.default_indexes
        if isinstance(indices, basestring):
            return [indices]
        return indices

    def status(self, indexes=None):
        """Retrieve the status of one or more indices."""
        indices = self._validate_indexes(indexes)
        path = self._make_path([','.join(indices), '_status'])
        d = self._send_request('GET', path)
        return d

    def create_index(self, index, settings=None):
        """Create an index with the optional settings dict."""
        d = self._send_request('PUT', index, settings)
        return d

    def create_index_if_missing(self, index, settings=None):
        """
        Create an index with the optional settings dict.

        Doesn't fail when index already exists.
        """
        def eb(failure):
            failure.trap(exceptions.IndexAlreadyExistsException)
            return {u'acknowledged': True, u'ok': True}

        d = self.create_index(index, settings)
        return d.addErrback(eb)

    def delete_index(self, index):
        """Deletes an index."""
        d = self._send_request('DELETE', index)
        return d

    def delete_index_if_exists(self, index):
        """Deletes an index if it exists."""
        def eb(failure):
            failure.trap(exceptions.IndexMissingException,
                         exceptions.NotFoundException)
            return {u'acknowledged': True, u'ok': True}

        d = self.delete_index(index)
        return d.addErrback(eb)

    def get_indices(self, include_aliases=False):
        """
        Get a dict holding an entry for each index which exists.

        If ``include_aliases`` is True, the dict will also contain entries for
        aliases.

        The key for each entry in the dict is the index or alias name. The
        value is a dict holding the following properties:

         - num_docs: Number of ducuments in the index or alias.
         - alias_for: Only present for an alias: hols a list of indicis
                      which this is an alias for.
        """
        def factor(status):
            result = {}
            indices = status['indices']
            for index in sorted(indices):
                info = indices[index]
                num_docs = info['docs']['num_docs']
                result[index] = {'num_docs': num_docs}
                if not include_aliases or 'aliases' not in info:
                    continue

                for alias in info['aliases']:
                    if alias not in result:
                        result[alias] = dict()

                    alias_docs = result[alias].get('num_docs', 0) + num_docs
                    result[alias]['num_docs'] = alias_docs

                    if 'alias_for' not in result[alias]:
                        result[alias]['alias_for'] = list()
                    result[alias]['alias_for'].append(index)
            return result

        d = self.status()
        return d.addCallback(factor)

    def get_alias(self, alias):
        """
        Return a list of indices pointed to by a given alias.

        Raises IndexMissionException if the alias does not exist.
        """
        def factor(status):
            return status['indices'].keys()

        d = self.status(alias)
        return d.addCallback(factor)

    def change_aliases(self, *commands):
        """
        Change the aliases stored.

        A command is a tuple of (["add"|"remove"], index, alias).

        You may specify multiple commands as additional arguments.
        """
        actions = [{c: {'index': i, 'alias': a}} for c, i, a in commands]
        d = self._send_request('POST', '_aliases', {'actions': actions})
        return d

    def add_alias(self, alias, indices):
        """Add an alias to point to a set of indices."""
        if isinstance(indices, basestring):
            indices = [indices]

        return self.change_aliases(*[('add', i, alias) for i in indices])

    def delete_alias(self, alias, indices):
        """Delete an alias."""
        if isinstance(indices, basestring):
            indices = [indices]

        return self.change_aliases(*[('remove', i, alias) for i in indices])

    def set_alias(self, alias, indices):
        """Set and alias (possibly removing what it already points to)."""
        def eb(failure):
            failure.trap(exceptions.IndexMissingException)
            return self.add_alias(alias, indices)

        def factor(old_indices):
            commands = [['remove', i, alias] for i in old_indices]
            commands.extend([['add', i, alias] for i in indices])
            if len(commands):
                return self.change_aliases(*commands)

        if isinstance(indices, basestring):
            indices = [indices]

        d = self.get_alias(alias)
        d.addCallbacks(factor, eb)
        return d

    def close_index(self, index):
        """Close an index."""
        d = self._send_request('POST', '/{}/_close'.format(index))
        return d

    def open_index(self, index):
        """Open an index."""
        d = self._send_request('POST', '/{}/_open'.format(index))
        return d

    def flush(self, indexes=None, wait_if_ongoing=None, full=None, force=None):
        def flush_it(result=None):
            indices = self._validate_indexes(indexes)
            path = self._make_path([','.join(indices), '_flush'])
            params = {}

            if wait_if_ongoing:
                params['wait_if_ongoing'] = bool(wait_if_ongoing)
            if full:
                params['full'] = bool(full)
            if force:
                params['force'] = bool(force)

            d = self._send_request('POST', path, params=params)
            return d

        if self.bulk_data:
            d = self.force_bulk()
            d.addCallback(flush_it)
            return d
        else:
            return flush_it()

    def refresh(self, indexes=None, timesleep=1):
        def wait(results):
            d = self.cluster_health(wait_for_status='green')
            d.addCallback(lambda _: results)
            self.refreshed = True
            return d

        def delay(results):
            d = defer.Deferred()
            reactor.callLater(timesleep, d.callback, results)
            d.addCallback(wait)
            return d

        def refresh_it(result=None):
            indices = self._validate_indexes(indexes)
            path = self._make_path([','.join(indices), '_refresh'])
            d = self._send_request('POST', path)
            d.addCallback(delay)
            return d

        if self.bulk_data:
            d = self.force_bulk()
            d.addCallback(refresh_it)
            return d
        else:
            return refresh_it()

    def optimize(
        self, indexes=None, wait_for_merge=False,
        max_num_segments=None, only_expunge_deletes=False,
        refresh=True, flush=True
    ):
        """Optimize one or more indices."""
        def done(results):
            self.refreshed = True
            return results

        indices = self._validate_indexes(indexes)
        path = self._make_path([','.join(indices), '_optimize'])
        params = {'wait_for_merge': wait_for_merge,
                  'only_expunge_deletes': only_expunge_deletes,
                  'refesh': refresh,
                  'flush': flush}
        if max_num_segments:
            params['max_num_segments'] = max_num_segments
        d = self._send_request('POST', path, params=params)
        d.addCallback(done)
        return d

    def analyze(self, text, index, analyzer=None):
        """Perform analysis on textual input."""
        if analyzer:
            analyzer = {'analyzer': analyzer}

        body = {'text': text}
        path = self._make_path([index, '_analyze'])
        d = self._send_request('POST', path, body=body, params=analyzer)
        return d

    def put_mapping(self, doc_type, mapping, indexes=None):
        """Register mapping definition for a specific type."""
        indices = self._validate_indexes(indexes)
        path = self._make_path([','.join(indices), doc_type, '_mapping'])
        if doc_type not in mapping:
            mapping = {doc_type: mapping}
        self.refreshed = False
        d = self._send_request('PUT', path, body=mapping)
        return d

    def get_mapping(self, doc_type=None, indexes=None):
        """Get the mapping definition"""
        indices = self._validate_indexes(indexes)
        path_items = [','.join(indices)]

        if doc_type:
            path_items.append(doc_type)

        path_items.append('_mapping')
        path = self._make_path(path_items)
        d = self._send_request('GET', path)
        return d

    def collect_info(self):
        """Collect info about the connection and fill the info dictionary."""
        def factor(result):
            self.info = {}
            self.info['server'] = {}
            self.info['server']['name'] = result['name']
            self.info['server']['version'] = result['version']
            self.info['allinfo'] = result
            return self.info

        d = self._send_request('GET', '/')
        d.addCallback(factor)
        return d

    def cluster_health(
        self, level='cluster', wait_for_status=None,
        wait_for_relocating_shards=None, wait_for_nodes=None,
        timeout=30
    ):
        """Check the current cluster health."""
        path = self._make_path(['_cluster', 'health'])
        if level not in ('cluster', 'indices', 'shards'):
            raise ValueError('Invalid level: %s' % level)

        mapping = {'level': level}

        if wait_for_status:
            if wait_for_status not in ('green', 'yellow', 'red'):
                raise ValueError(
                    'Invalid wait_for_status: {}'.format(wait_for_status))
            mapping['wait_for_status'] = wait_for_status

        if wait_for_relocating_shards:
            mapping['wait_for_relocating_shards'] = wait_for_relocating_shards

        if wait_for_nodes:
            mapping['wait_for_nodes'] = wait_for_nodes

        if wait_for_status or wait_for_relocating_shards or wait_for_nodes:
            mapping['timeout'] = timeout

        d = self._send_request('GET', path, mapping)
        return d

    def cluster_state(self, metrics=None, indices=None, **kwargs):
        """
        Retrieve the cluster state.

        :param metric: a list of metrics for filtering results (see ES docs).
        :param indices: a list of indicies for filtering results (see ES docs).
        """
        path = ['_cluster', 'state']

        if metrics:
            if not isinstance(metrics, basestring):
                metrics = ','.join(metrics)
            path.append(metrics)
        else:
            path.append('_all')

        if indices:
            if not isinstance(indices, basestring):
                indices = ','.join(indices)
            path.append(indices)

        path = self._make_path(path)
        d = self._send_request('GET', path, **kwargs)
        return d

    def cluster_nodes(self, nodes=None):
        """The cluster nodes info API."""
        parts = ['_nodes']
        if nodes:
            parts.append(','.join(nodes))
        path = self._make_path(parts)
        d = self._send_request('GET', path)
        return d

    def index(
        self, doc, index, doc_type, id=None, parent=None,
        force_insert=None, bulk=False, version=None, **query_params
    ):
        """Index a dict into an index."""
        self.refreshed = False

        if bulk:
            optype = 'index'
            if force_insert:
                optype = 'create'
            cmd = {optype: {'_index': index, '_type': doc_type}}
            if parent:
                cmd[optype]['_parent'] = parent
            if version:
                cmd[optype]['_version'] = version
            if id:
                cmd[optype]['_id'] = id
            data = '\n'.join([anyjson.serialize(cmd),
                              anyjson.serialize(doc)])
            data += '\n'
            self.bulk_data.append(data)
            return self.flush_bulk()

        if force_insert:
            query_params['op_type'] = 'create'

        if parent:
            query_params['parent'] = parent

        if version:
            query_params['version'] = version

        if id:
            request_method = 'PUT'
        else:
            request_method = 'POST'

        path = self._make_path([index, doc_type, id])
        d = self._send_request(
            request_method, path, body=doc,
            params=query_params)
        return d

    def flush_bulk(self, forced=False):
        """Wait to process all pending operations."""
        if not forced and len(self.bulk_data) < self.bulk_size:
            return defer.succeed(None)

        return self.force_bulk()

    def force_bulk(self):
        """Force executing of all bulk data."""
        if not len(self.bulk_data):
            return defer.succeed(None)

        data = '\n'.join(self.bulk_data)
        d = self._send_request('POST', '/_bulk', body=data)
        self.bulk_data = []
        return d

    def delete(self, index, doc_type, id, bulk=False, **query_params):
        """Delete a document based on its id."""
        if bulk:
            cmd = {'delete': {'_index': index,
                              '_type': doc_type,
                              '_id': id}}
            self.bulk_data.append(anyjson.serialize(cmd))
            return self.flush_bulk()

        path = self._make_path([index, doc_type, id])
        d = self._send_request('DELETE', path, params=query_params)
        return d

    def delete_by_query(self, indexes, doc_types, query, **query_params):
        """Delete documents from one or more indexes/types from query."""
        indices = self._validate_indexes(indexes)
        if not doc_types:
            doc_types = []
        elif isinstance(doc_types, basestring):
            doc_types = [doc_types]

        path = self._make_path(
            [','.join(indices), ','.join(doc_types), '_query'])
        body = {'query': query}
        d = self._send_request('DELETE', path, body, params=query_params)
        return d

    def delete_mapping(self, index, doc_type):
        """Delete a document type from a specific index."""
        path = self._make_path([index, doc_type])
        d = self._send_request('DELETE', path)
        return d

    def get(
        self, index, doc_type, id, fields=None, routing=None, **query_params
    ):
        """Get a typed document from an index based on its id."""
        path = self._make_path([index, doc_type, id])
        if fields:
            query_params['fields'] = ','.join(fields)
        if routing:
            query_params['routings'] = routing
        d = self._send_request('GET', path, params=query_params)
        return d

    def mget(self, ids, index=None, doc_type=None, **query_params):
        """
        Get multiples documents based on id.

        ids can be:
            list of tuples: (index, type, id)
            list of ids: index and doc_type are required
        """
        if not ids:
            return {'docs': []}

        body = []
        for value in ids:
            if isinstance(value, tuple):
                if len(value) == 3:
                    a, b, c = value
                    body.append({'_index': a,
                                 '_type': b,
                                 '_id': c})
                elif len(value) == 4:
                    a, b, c, d = value
                    body.append({'_index': a,
                                 '_type': b,
                                 '_id': c,
                                 'fields': d})
            else:
                if index is None:
                    raise Exception('index value is required for id')
                if doc_type is None:
                    raise Exception('doc_type value is required for id')

                body.append({'_index': index,
                             '_type': doc_type,
                             '_id': value})

        d = self._send_request(
            'GET', path='/_mget', body={'docs': body}, params=query_params)
        return d

    def search(self, query, indexes=None, doc_type=None, **params):
        """Execute a search against one or more indices."""
        indices = self._validate_indexes(indexes)
        d = self._send_query('_search', query, indices, doc_type, **params)
        return d

    def scan(
        self, query, indexes=None, doc_type=None,
        scroll_timeout='10m', **params
    ):
        """
        Return an iterator which will scan against one or more indices.

        Each call to next() will yield a deferred that will contain the
        next dataset.
        """

        class Scroller(object):
            def __init__(self, results, es_parent):
                self.results = results
                self.es_parent = es_parent

            def __iter__(self):
                return self

            def _set_results(self, results):
                if not len(results['hits']['hits']):
                    raise StopIteration
                self.results = results
                return results

            def next(self):
                scroll_id = str(self.results['_scroll_id'])
                d = self.es_parent._send_request(
                    'GET', '_search/scroll', scroll_id,
                    {'scroll': scroll_timeout})
                d.addCallback(self._set_results)
                return

        def scroll(results):
            return Scroller(results, self)

        d = self.search(
            query=query, indexes=indexes, doc_type=doc_type,
            search_types='scan', scroll=scroll_timeout, **params)
        d.addCallback(scroll)
        return d

    def count(self, query, indexes=None, doc_types=None, **params):
        """Execute a query against one or more indices & get the hit count."""
        indices = self._validate_indexes(indexes)
        d = self._send_query('_count', query, indices, doc_types, **params)
        return d

    def create_river(self, river, river_name=None):
        """Create a river."""
        if not river_name:
            river_name = river['index']['index']
        d = self._send_request(
            'PUT', '/_river/{}/_meta'.format(river_name), body=river)
        return d

    def delete_river(self, river, river_name=None):
        """Delete a river."""
        if not river_name:
            river_name = river['index']['index']
        d = self._send_request('DELETE', '/_river/{}/'.format(river_name))
        return d

    def more_like_this(self, index, doc_type, id, fields, **params):
        """Execute a "more like this" query against one or more fields."""
        path = self._make_path([index, doc_type, id, '_mlt'])
        params['fields'] = ','.join(fields)
        d = self._send_request('GET', path, params=params)
        return d

    def update_settings(self, index, settings):
        """Update settings of an index."""
        path = self._make_path([index, '_settings'])
        d = self._send_request('PUT', path, body=settings)
        return d

    def partial_update(
        self, index, doc_type, id, doc=None, script=None,
        params=None, upsert=None, **query_params
    ):
        """Partially update a document with a script."""
        if doc is None and script is None:
            raise exceptions.InvalidQuery("script or doc can not both be None")

        if doc is None:
            cmd = {'script': script}
            if params:
                cmd["params"] = params
            if upsert:
                cmd["upsert"] = upsert
        else:
            cmd = {'doc': doc}

        path = self._make_path([index, doc_type, id, '_update'])
        d = self._send_request('POST', path, cmd, params=query_params)
        return d

    @property
    def servers(self):
        """Return a list of servers available for connections."""
        return self.connection.servers
