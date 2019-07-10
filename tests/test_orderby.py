from tests.mock_api import ConseilCase


class AggregationTest(ConseilCase):

    def test_order_directions(self):
        c = self.conseil.tezos.alphanet

        self.assertDictEqual({
            'field': 'balance',
            'direction': 'asc'
        }, c.accounts.balance.asc())

        self.assertDictEqual({
            'field': 'balance',
            'direction': 'desc'
        }, c.accounts.balance.desc())

    def test_order_by(self):
        c = self.conseil.tezos.alphanet

        query = c.accounts.query() \
            .order_by(c.accounts.balance.desc(),
                      c.accounts.manager)
        self.assertListEqual([{
            'field': 'balance',
            'direction': 'desc'
        }, {
            'field': 'manager',
            'direction': 'asc'
        }], query.payload()['orderBy'])

    def test_order_by_aggregated_field(self):
        c = self.conseil.tezos.alphanet

        query = c.query(c.accounts.account_id, c.accounts.balance.sum()) \
            .order_by(c.accounts.balance.sum().desc())
        self.assertListEqual([{
            'field': 'sum_balance',
            'direction': 'desc'
        }], query.payload()['orderBy'])
