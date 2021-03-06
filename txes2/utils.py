import time
import random

from urllib import quote

from . import exceptions


def make_path(components):
    """Build a path from a list of components."""
    return '/{}'.format(
        '/'.join([quote(str(c), '') for c in components if c]))


class Scroller(object):

    """Handle scrolling through scan and scroll API."""

    def __init__(self, results, scroll_timeout, es):
        self.results = results
        self.scroll_timeout = scroll_timeout
        self.es = es
        self._scroll_id = None

    @property
    def scroll_id(self):
        if self.results:
            self._scroll_id = str(self.results['_scroll_id'])

        return self._scroll_id

    def next_page(self):
        """Fetch next page from scroll API."""
        d = self.es._send_request(
            'POST', '_search/scroll',
            {'scroll': self.scroll_timeout, 'scroll_id': self.scroll_id})
        d.addCallback(self._set_results)
        return d

    def _set_results(self, results):
        if not results['hits']['hits']:
            self.results = None
        else:
            self.results = results

        return self.results

    def delete(self):
        """Clear Scroll when finished."""
        def _clear_scroll(*args, **kwargs):
            self._scroll_id = None

        if not self.scroll_id:
            return

        return self.es._send_request(
            'DELETE', '_search/scroll',
            body={'scroll_id': [self.scroll_id]}).addCallback(_clear_scroll)


class ServerList(list):
    def __init__(self, servers, retry_time=10, timeout=None):
        list.__init__(self, servers)
        self.dead = []
        self.retry_time = retry_time
        self.timeout = timeout

    def get(self):
        if self.dead:
            retry_time, server = self.dead.pop()
            if retry_time > time.time():
                self.dead.append((retry_time, server))
            else:
                self.append(server)
        if not self:
            raise exceptions.NoServerAvailable()

        return random.choice(self)

    def mark_dead(self, server):
        if server in self:
            self.remove(server)
            self.dead.insert(0, (time.time() + self.retry_time, server))
