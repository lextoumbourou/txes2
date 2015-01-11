"""Tests for the utils module."""

import sys
from mock import patch

from twisted.trial.unittest import TestCase

from txes2.utils import ServerList
from txes2.exceptions import NoServerAvailable


class UtilsTest(TestCase):

    """Tests for the util modules."""

    def test_get_returns_exception_when_empty(self):
        s = ServerList([])
        self.assertRaises(NoServerAvailable, s.get)

    @patch('txes2.utils.time')
    def test_retests_a_dead_server(self, time_mock):
        s = ServerList(['srv1', 'srv2'], retry_time=0)
        time_mock.time.return_value = 1
        s.mark_dead('srv2')
        time_mock.time.return_value = 2
        s.get()
        self.assertTrue('srv2' in s)

    @patch('txes2.utils.time')
    def test_doesnt_retest_if_in_future(self, time_mock):
        s = ServerList(['srv1', 'srv2'])
        time_mock.time.return_value = 2
        s.mark_dead('srv2')
        s.dead.append((sys.maxint, 'srv2'))
        time_mock.time.return_value = 1
        s.get()
        self.assertTrue('srv2' not in s)
