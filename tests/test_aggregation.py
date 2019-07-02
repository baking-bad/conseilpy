from conseil.core import *
from tests.mock_api import ConseilCase


class QueryTest(ConseilCase):

    def test_aggregated_columns(self):
        c = self.conseil.tezos.alphanet

        query = c.query(c.accounts.account_id, c.accounts.balance.sum())
        self.assertListEqual([{'field': 'balance', 'function': 'sum'}], query.payload()['aggregation'])

    def test_aggregated_sort(self):
        c = self.conseil.tezos.alphanet

        query = c.query(c.accounts.account_id, c.accounts.balance.sum())
        self.assertListEqual([{'field': 'balance', 'function': 'sum'}], query.payload()['aggregation'])
