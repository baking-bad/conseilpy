from unittest.mock import MagicMock

from conseil.core import *
from tests.mock_api import ConseilCase, MockQuery


class QueryTest(ConseilCase):

    def test_network_query(self):
        c = self.conseil.tezos.alphanet

        query = c.query(c.accounts)
        self.assertListEqual([], query.payload()['fields'])

        query = c.query(c.accounts.account_id, c.accounts.balance)
        self.assertListEqual(['account_id', 'balance'], query.payload()['fields'])

        self.assertRaises(ConseilException, c.query, c.accounts.account_id, c.operations.kind)
        self.assertRaises(ConseilException, c.query, 'account_id')

    def test_entity_query(self):
        c = self.conseil.tezos.alphanet

        query = c.accounts.query()
        self.assertListEqual([], query.payload()['fields'])

        query = c.query(c.accounts.account_id, c.accounts.balance)
        self.assertListEqual(['account_id', 'balance'], query.payload()['fields'])

        self.assertRaises(ConseilException, c.accounts.query, c.accounts.account_id, c.operations.kind)
        self.assertRaises(ConseilException, c.accounts.query, 'account_id')
        self.assertRaises(ConseilException, c.accounts.query, c.accounts)

    def test_attribute_query(self):
        c = self.conseil.tezos.alphanet

        query = c.accounts.account_id.query()
        self.assertListEqual(['account_id'], query.payload()['fields'])

    def test_label(self):
        response = MagicMock()
        response.json.return_value = [{'account_id': 'tzkt'}]

        api = MagicMock()
        api.post.return_value = response

        c = ConseilClient(api).tezos.alphanet

        res = c.accounts.query(c.accounts.account_id.label('address')).all()
        self.assertDictEqual({'address': 'tzkt'}, res[0])

    def test_one(self):
        query = MockQuery()

        query.res = [{'a': 1}]
        self.assertDictEqual({'a': 1}, query.one())
        self.assertDictEqual({'a': 1}, query.one_or_none())

        query.res = [{'a': 1}, {'a': 2}]
        self.assertRaises(ConseilException, query.one)
        self.assertIsNone(query.one_or_none())

        query.res = []
        self.assertRaises(ConseilException, query.one)
        self.assertIsNone(query.one_or_none())

    def test_scalar(self):
        query = MockQuery()

        query.res = [{'a': 1}]
        self.assertEqual(1, query.scalar())

        query.res = [{'a': 1, 'b': 2}]
        self.assertRaises(ConseilException, query.scalar)

        query.res = [{'a': 1}, {'a': 2}]
        self.assertRaises(ConseilException, query.scalar)

        query.res = []
        self.assertRaises(ConseilException, query.scalar)

    def test_vector(self):
        query = MockQuery()

        query.res = [{'a': 1}, {'a': 2}]
        self.assertListEqual([1, 2], query.vector())

        query.res = []
        self.assertListEqual([], query.vector())

        query.res = [{'a': 1, 'b': 2}, {'a': 2, 'b': 3}]
        self.assertRaises(ConseilException, query.vector)
