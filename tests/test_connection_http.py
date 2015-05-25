"""Tests for the HTTPConnection module."""

from mock import patch, Mock

from twisted.internet.defer import succeed, inlineCallbacks
from twisted.trial.unittest import TestCase

from txes2.connection_http import _prepare_url, HTTPConnection


class HTTPConnectionTest(TestCase):

    """Tests for the HTTPConnection module."""

    def test_prepare_url(self):
        result = _prepare_url('s1', 'index/doc/_search', {'size': 5})
        self.assertTrue(result == 'http://s1/index/doc/_search?size=5')

    @patch('txes2.connection_http.treq')
    @inlineCallbacks
    def test_execute(self, treq_mock):
        response_mock = Mock(code=200)

        treq_mock.request.return_value = succeed(response_mock)
        treq_mock.json_content.return_value = succeed({'_id': 123})

        conn = HTTPConnection()
        conn.connect('s1', pool=Mock())
        conn.add_server('s2')

        yield conn.execute(
            'GET', 'index/doc/_search', body={'query': {'term': 'something'}})

        assert treq_mock.json_content.called

        conn.close()
