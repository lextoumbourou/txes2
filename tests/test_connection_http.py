"""Tests for the HTTPConnection module."""

from mock import patch, Mock

from twisted.internet.defer import succeed, inlineCallbacks
from twisted.trial.unittest import TestCase
from twisted.internet.error import ConnectionRefusedError

from txes2.connection_http import _prepare_url, HTTPConnection
from txes2.exceptions import ElasticSearchException


@patch('txes2.connection_http.treq')
class HTTPConnectionTest(TestCase):

    """Tests for the HTTPConnection module."""

    def setUp(self):
        """Setup connection mocks."""
        self.conn = HTTPConnection()
        self.conn.connect('s1', pool=Mock())
        self.conn.add_server('s2')

    def test_prepare_url(self, _):
        result = _prepare_url('s1', 'index/doc/_search', {'size': 5})
        self.assertTrue(result == 'http://s1/index/doc/_search?size=5')

    def test_prepare_url_handles_ssl(self, _):
        result = _prepare_url(
            'https://s1:443', 'index/doc/_search', {'size': 5})
        self.assertTrue(result == 'https://s1:443/index/doc/_search?size=5')

    @inlineCallbacks
    def test_execute(self, treq_mock):
        response_mock = Mock(code=200)

        treq_mock.request.return_value = succeed(response_mock)
        treq_mock.json_content.return_value = succeed({'_id': 123})

        yield self.conn.execute(
            'GET', 'index/doc/_search', body={'query': {'term': 'something'}})

        assert treq_mock.json_content.called

        self.conn.close()

    @inlineCallbacks
    def test_execute_marks_dead_on_connection_failure(self, treq_mock):
        """
        Handle ConnectionRefusedError error.

        When Twisted raises exception, we mark the server dead and retry.
        """
        def raise_connection_refused(*args, **kwargs):
            """Raise ConnectionRefusedError."""
            raise ConnectionRefusedError()

        treq_mock.request.side_effect = raise_connection_refused

        self.conn.servers.mark_dead = Mock()

        yield self.assertFailure(
            self.conn.execute('GET', 'index/doc/_search'),
            ConnectionRefusedError)

        # Ensure we retry enough times
        self.assertEquals(self.conn.servers.mark_dead.call_count, 3)

        self.conn.close()

    @inlineCallbacks
    def test_execute_doesnt_retry_on_client_error(self, treq_mock):
        """When ES returns a client-exception, we shouldn't retry."""
        response_mock = Mock(code=429)

        treq_mock.request.return_value = succeed(response_mock)
        treq_mock.json_content.return_value = succeed({
            u'status': 429,
            u'error': u'ReduceSearchPhaseException[Failed to execute phase [fetch], [reduce] ; shardFailures {[2A-6X8MDRP-gZ6M_752d-A][tmp][0]: EsRejectedExecutionException[rejected execution (queue capacity 0) on org.elasticsearch.search.action.SearchServiceTransportAction$23@24084605]}]; nested: EsRejectedExecutionException[rejected execution (queue capacity 0) on org.elasticsearch.action.search.type.TransportSearchQueryThenFetchAction$AsyncAction$2@42658745]'})   # noqa

        self.conn.servers.mark_dead = Mock()

        yield self.assertFailure(
            self.conn.execute('GET', 'index/doc/_search'),
            ElasticSearchException)

        # Ensure no retries
        self.assertEquals(self.conn.servers.mark_dead.call_count, 0)

        self.conn.close()
