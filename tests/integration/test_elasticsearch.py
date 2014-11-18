"""Integration tests for the ElasticSearch class."""

from mock import patch
from twisted.trial.unittest import TestCase
from twisted.internet.defer import inlineCallbacks, succeed

from txes.elasticsearch import ElasticSearch

from . import settings


class ElasticSearchIntegrationTest(TestCase):

    """Tests for the ElasticSearch class."""

    def setUp(self):
        self.es = ElasticSearch(settings.URL)

    @inlineCallbacks
    def test_index(self):
        data = {'id': 1, 'name': 'Some Doc'}
        result = yield self.es.index(data, settings.INDEX, settings.DOC_TYPE)
        self.assertTrue(result['created'])

    @inlineCallbacks
    def test_mget(self):
        result = yield self.es.mget([1], settings.INDEX, settings.DOC_TYPE)
        self.assertTrue('docs' in result)
