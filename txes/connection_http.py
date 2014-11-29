import urllib

import treq
import anyjson
from twisted.web.client import HTTPConnectionPool
from twisted.internet import reactor
from zope import interface

from txes import exceptions, interfaces, utils


class HTTPConnection(object):
    interface.implements(interfaces.IConnection)

    def addServer(self, server):
        if server not in self.servers:
            self.servers.append(server)

    def connect(
        self, servers=None, timeout=None, retryTime=10, *args, **kwargs
    ):
        if isinstance(servers, (str, unicode)):
            servers = [servers]
        self.servers = utils.ServerList(servers, retryTime=retryTime)
        self.agents = {}
        self.timeout = timeout

        persistent = kwargs.get('persistent', False)
        self.pool = kwargs.get('pool') or HTTPConnectionPool(
            reactor, persistent)

    def close(self):
        """Close up all persistent connections."""
        return self.pool.closeCachedConnections()

    def execute(self, method, path, body=None, params=None):
        server = self.servers.get()
        timeout = self.servers.timeout
        if not path.startswith('/'):
            path = '/' + path
        url = server + path

        if params:
            url = url + '?' + urllib.urlencode(params)

        if not isinstance(body, basestring):
            body = anyjson.serialize(body)

        if not url.startswith("http://"):
            url = "http://" + url
        url = url.encode('utf-8')

        def request_done(response):
            def _raise_error(body):
                if response.code != 200:
                    exceptions.raiseExceptions(response.code, body)
                return body

            return treq.json_content(response.original).addCallback(_raise_error)

        d = treq.request(
            method, url, data=body, pool=self.pool)
        d.addCallback(request_done)
        return d
