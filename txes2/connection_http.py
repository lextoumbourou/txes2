import urllib

from twisted.internet import defer
from twisted.internet.error import ConnectError
from twisted.web.client import ResponseFailed, RequestTransmissionFailed
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
        self.max_retries = kwargs.get('max_retries', 3)

    def close(self):
        """Close up all persistent connections."""
        if self.pool:
            return self.pool.closeCachedConnections()

    @defer.inlineCallbacks
    def execute(self, method, path, body=None, params=None):
        """Execute a query against a server."""
        if not isinstance(body, basestring):
            body = anyjson.serialize(body)

        for attempt in range(self.max_retries + 1):
            server = self.servers.get()
            timeout = self.servers.timeout
            url = _prepare_url(server, path, params)

            response = None  # Stop UnboundLocalError on uncaught exception
            try:
                response = yield treq.request(
                    method, url, data=body, pool=self.pool,
                    auth=self.http_auth, persistent=self.persistent,
                    timeout=timeout)
                json_data = yield response.json()
                exceptions.raise_exceptions(response.code, json_data)
            except Exception as e:
                retry = False

                if isinstance(
                    e, (
                        ConnectError,
                        ResponseFailed,
                        RequestTransmissionFailed,
                    )
                ) or response and response.code in (503, 504):
                    retry = True

                if retry:
                    self.servers.mark_dead(server)
                    if attempt == self.max_retries:
                        raise

                    continue
                else:
                    raise
            else:
                defer.returnValue(json_data)
