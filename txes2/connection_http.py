import urllib

import treq
import anyjson

from . import exceptions, utils


def _prepare_url(server, path, params):
    """Prepare Elasticsearch connection URL."""
    if not path.startswith('/'):
        path = '/' + path

    url = server + path

    if params:
        url = url + '?' + urllib.urlencode(params)

    if not url.startswith(('http:', 'https:')):
        url = "http://" + url

    return url.encode('utf-8')


class HTTPConnection(object):
    def add_server(self, server):
        if server not in self.servers:
            self.servers.append(server)

    def connect(
        self, servers=None, timeout=None, retry_time=10, *args, **kwargs
    ):
        if isinstance(servers, (str, unicode)):
            servers = [servers]
        self.servers = utils.ServerList(servers, retry_time=retry_time)
        self.agents = {}
        self.timeout = timeout

        self.persistent = kwargs.get('persistent', True)
        self.pool = kwargs.get('pool')
        self.http_auth = kwargs.get('http_auth')

    def close(self):
        """Close up all persistent connections."""
        if self.pool:
            return self.pool.closeCachedConnections()

    def execute(self, method, path, body=None, params=None):
        """Execute a query against a server."""
        server = self.servers.get()
        timeout = self.servers.timeout

        url = _prepare_url(server, path, params)

        if not isinstance(body, basestring):
            body = anyjson.serialize(body)

        def request_done(response):
            def _raise_error(body):
                exceptions.raise_exceptions(response.code, body)
                return body

            return treq.json_content(response.original).addCallback(
                _raise_error)

        d = treq.request(
            method, url, data=body, pool=self.pool, auth=self.http_auth,
            persistent=self.persistent, timeout=timeout)
        d.addCallback(request_done)
        return d
