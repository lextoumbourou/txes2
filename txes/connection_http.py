import urllib

import anyjson
from twisted.web import client
from zope import interface

from txes import exceptions, interfaces, utils


DEFAULT_SERVER = "127.0.0.1:9200"


class HTTPConnection(object):
    interface.implements(interfaces.IConnection)

    def addServer(self, server):
        if server not in self.servers:
            self.servers.append(server)

    def connect(self, servers=None, timeout=None, retryTime=10,
                *args, **kwargs):
        if not servers:
            servers = [DEFAULT_SERVER]
        elif isinstance(servers, (str, unicode)):
            servers = [servers]
        self.servers = utils.ServerList(
            servers, retryTime=retryTime, timeout=timeout)
        self.agents = {}

    def close(self):
        pass

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

        def decode_json(body_string):
            return anyjson.deserialize(body_string)

        def eb(reason):
            reason.trap(client.error.Error)
            status = int(reason.value.status)
            try:
                body = decode_json(reason.value.response)
            except:
                body = {'error': reason.value.response}
            if status != 200:
                exceptions.raiseExceptions(status, body)
            return body

        d = client.getPage(
            str(url), method=method, postdata=body, timeout=timeout,
            headers={'Content-Type': 'application/json'})
        d.addCallback(decode_json)
        d.addErrback(eb)
        return d
