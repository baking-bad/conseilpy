from conseil.core import *
from tests.mock_api import ConseilCase


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
        pass
