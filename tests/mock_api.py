from requests import Response
from unittest import TestCase
from unittest.mock import MagicMock

from conseil.core import Client


class MockResponse(Response):

    def json(self):
        return []

    def text(self):
        return ''


class ConseilCase(TestCase):

    def setUp(self):
        self.api = MagicMock()
        self.api.get.return_value = MockResponse()
        self.api.post.return_value = MockResponse()
        self.conseil = Client(self.api)

    def assertLastGetPathEquals(self, path):
        self.assertEqual(path, self.api.get.call_args_list[-1][0][0])
