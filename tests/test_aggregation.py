from conseil.api import ConseilException
from tests.mock_api import ConseilCase


class AggregationTest(ConseilCase):

    def test_aggregated_columns(self):
        c = self.conseil.tezos.alphanet

        query = c.query(c.accounts.account_id, c.accounts.balance.sum())
        self.assertListEqual([{
            'field': 'balance',
            'function': 'sum'
        }], query.payload()['aggregation'])

        query = c.query(c.accounts.account_id, c.accounts.balance.count())
        self.assertListEqual([{
            'field': 'balance',
            'function': 'count'
        }], query.payload()['aggregation'])

        query = c.query(c.accounts.account_id, c.accounts.balance.min())
        self.assertListEqual([{
            'field': 'balance',
            'function': 'min'
        }], query.payload()['aggregation'])

        query = c.query(c.accounts.account_id, c.accounts.balance.max())
        self.assertListEqual([{
            'field': 'balance',
            'function': 'max'
        }], query.payload()['aggregation'])

        query = c.query(c.accounts.account_id, c.accounts.balance.avg())
        self.assertListEqual([{
            'field': 'balance',
            'function': 'avg'
        }], query.payload()['aggregation'])

    def test_having(self):
        c = self.conseil.tezos.alphanet

        query = c.query(c.accounts.account_id, c.accounts.balance.sum()) \
            .having(c.accounts.balance > 1000)
        self.assertListEqual([{
            'field': 'balance',
            'function': 'sum',
            'predicate': {
                'field': 'balance',
                'operation': 'gt',
                'set': [1000],
                'inverse': False
            }
        }], query.payload()['aggregation'])

    def test_orphan_having(self):
        c = self.conseil.tezos.alphanet

        query = c.query(c.accounts.account_id, c.accounts.balance.sum()) \
            .having(c.accounts.manager.in_('a', 'b'))
        self.assertRaises(ConseilException, query.payload)

    def test_group_by(self):
        c = self.conseil.tezos.alphanet

        query = c.query(c.accounts.balance.avg()) \
            .group_by(c.accounts.account_id)
        self.assertListEqual(['balance', 'account_id'], query.payload()['fields'])
