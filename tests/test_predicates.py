from conseil.core import *
from tests.mock_api import ConseilCase


class PredicatesTest(ConseilCase):

    def setUp(self):
        super(PredicatesTest, self).setUp()
        self.attr = self.conseil.tezos.alphanet.accounts.account_id

    def test_in(self):
        self.assertDictEqual({
            'field': 'account_id',
            'operation': 'in',
            'set': [1, 2, 3],
            'inverse': False
        }, self.attr.in_(1, 2, 3))

        self.assertDictEqual({
            'field': 'account_id',
            'operation': 'in',
            'set': ['1', '2', '3'],
            'inverse': True
        }, self.attr.notin_('1', '2', '3'))

        self.assertDictEqual({
            'field': 'account_id',
            'operation': 'isnull',
            'set': [],
            'inverse': False
        }, self.attr.in_())

        self.assertDictEqual({
            'field': 'account_id',
            'operation': 'isnull',
            'set': [],
            'inverse': True
        }, self.attr.notin_())

        self.assertDictEqual({
            'field': 'account_id',
            'operation': 'eq',
            'set': ['1'],
            'inverse': False
        }, self.attr.in_('1'))

        self.assertDictEqual({
            'field': 'account_id',
            'operation': 'eq',
            'set': ['2'],
            'inverse': True
        }, self.attr.notin_('2'))

    def test_between(self):
        pass

    def test_like(self):
        pass

    def test_lt(self):
        pass

    def test_gt(self):
        pass

    def test_eq(self):
        pass

    def test_startswith(self):
        pass

    def test_endswith(self):
        pass

    def test_before(self):
        pass

    def test_after(self):
        pass

    def test_isnull(self):
        pass

    def test_not(self):
        pass

    def test_filter(self):
        pass

    def test_filter_by(self):
        pass
