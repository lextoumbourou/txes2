"""Tests for the Exceptions module."""

from twisted.trial.unittest import TestCase

from txes2.exceptions import (
    raise_exceptions, NotFoundException,
    ElasticSearchException, RequestException)


class ExceptionsTest(TestCase):

    """Tests for the Exceptions module."""

    def test_raises_404(self):
        self.assertRaises(NotFoundException, raise_exceptions, 404, {})

    def test_raises_unknown_exception_type(self):
        ex = None

        try:
            raise_exceptions(400, {})
        except ElasticSearchException as e:
            ex = e

        self.assertTrue(
            hasattr(ex, 'message') and ex.message == 'Unknown exception type')

    def test_handles_exception_script_correctly(self):
        result = {
            'error': {
                'root_cause': [{
                    'type': 'index_already_exists_exception',
                    'reason': 'already exists',
                    'index': 'my_index'
                }],
                'type': 'index_already_exists_exception',
                'reason': 'already exists',
                'index': 'my_index'
            },
            'status': 400
        }

        self.assertRaises(
            RequestException, raise_exceptions, 400, result)

    def test_handle_fall_through_case(self):
        result = {'error': 'Not what I expect'}
        self.assertRaises(
            ElasticSearchException, raise_exceptions, 412, result)
