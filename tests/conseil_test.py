import unittest
from parameterized import parameterized

from mock_api import MockApi
from conseilpy.conseil import Conseil, OutputType, AggMethod, ConseilException

class Test_Conseil(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(Test_Conseil, self).__init__(*args, **kwargs)
        self.c = None

    def setUp(cls):
        cls.c = Conseil(MockApi(), platform="tezos", network="alphanet")

    def tearDown(cls):
        cls.c._reset_temp()

    def test_reset_temp(self):
        self.c._query_platform = 'tezos'
        self.c._query_network = 'alphanet'
        self._temp_request = 'request'
        self._temp_query = {}
        self._temp_entity = 'entity'

        self.c._reset_temp()

        self.assertEqual(self.c._query_platform, None)
        self.assertEqual(self.c._query_network, None)
        self.assertEqual(self.c._temp_request, '')
        self.assertEqual(self.c._temp_query, {
            'fields': [],
            'predicates': [],
            'limit': 5
        })
        self.assertEqual(self.c._temp_entity, None)

    def test_init_entities(self):
        self.c._init_entities()
        self.assertIsNotNone(self.c.Accounts)
        self.assertEqual(self.c.Accounts.count, 19587)

    def test_platforms(self):
        data = self.c.platforms()
        self.assertEqual(data, [{
            "name": "tezos",
            "displayName": "Tezos"
        }])

    @parameterized.expand([
        (None,),
        ("tezos",),
    ])
    def test_networks(self, platform):
        data = self.c.networks(platform_name=platform)
        self.assertEqual(data, [{
            "name": "alphanet",
            "displayName": "Alphanet",
            "platform": "tezos",
            "network": "alphanet"
        }])

    @parameterized.expand([
        (None, None),
        ("tezos", None),
        (None, 'alphanet'),
        ("tezos", "alphanet"),
    ])
    def test_entities(self, platform, network):
        data = self.c.entities(platform_name=platform, network=network)
        self.assertEqual(data, [{
            "name": "accounts",
            "displayName": "Accounts",
            "count": 19587
        }])

    @parameterized.expand([
        (None, None, "accounts"),
        ("tezos", None, "accounts"),
        (None, 'alphanet', "accounts"),
        ("tezos", "alphanet", "accounts"),
    ])
    def test_attributes(self, platform, network, entity):
        data = self.c.attributes(platform_name=platform, network=network, entity=entity)
        self.assertEqual(data, [{
            "name": "account_id",
            "displayName": "Account id",
            "dataType": "String",
            "cardinality": 19587,
            "keyType": "UniqueKey",
            "entity": "accounts"
        }, {
            "name": "block_id",
            "displayName": "Block id",
            "dataType": "String",
            "cardinality": 4614,
            "keyType": "NonKey",
            "entity": "accounts"
        }])

    def test_platform(self):
        obj = self.c.platform('test')
        self.assertEqual(obj._query_platform, 'test')

    def test_network(self):
        obj = self.c.network('test')
        self.assertEqual(obj._query_network, 'test')

    @parameterized.expand([
        (None, None),
        ("tezos", None),
        (None, "alphanet"),
        ("tezos", "alphanet"),
    ])
    def test_query(self, platform, network):
        if platform:
            self.c.platform(platform)
        if network:
            self.c.network(network)
        
        entity = self.c.Accounts
        self.c.query(entity)
        self.assertEqual(self.c._temp_entity, entity)
        self.assertEqual(self.c._temp_request, 'data/tezos/alphanet/accounts')

    def test_select(self):
        self.c.query(self.c.Accounts).select([self.c.Accounts.Accountid])
        self.assertEqual(self.c._temp_query['fields'], ['account_id'])
    
    def test_limit(self):
        self.c.query(self.c.Accounts).limit(10)
        self.assertEqual(self.c._temp_query['limit'], 10)

    def test_output(self):
        self.c.query(self.c.Accounts).output(OutputType.JSON)
        self.assertEqual(self.c._temp_query['output'], 'json')

    def test_agg(self):
        self.c.query(self.c.Accounts).agg(self.c.Accounts.Accountid, AggMethod.SUM)
        self.assertEqual(self.c._temp_query['aggregation'], {
            'field': 'account_id',
            'function': 'sum',
            'predicate': {}
        })
    @parameterized.expand([
        ("asc",),
        ("desc",),
        ("unknown",)
    ])
    def test_order_by(self, direction):
        if direction in ["asc", "desc"]:
            self.c.query(self.c.Accounts).order_by(self.c.Accounts.Accountid, direction)
            self.assertEqual(self.c._temp_query['orderBy'], [{
                'field': "account_id",
                'direction': direction
            }])
        else:
            with self.assertRaises(ConseilException):
                self.c.query(self.c.Accounts).order_by(self.c.Accounts.Accountid, direction)
    
    @parameterized.expand([
        (["test1", "test2"], False, None),
        (["test1", "test2"], True, None),
        (["test1"], False, None),
        (["test1"], True, None),
        (["test1", "test2"], False, 3),
        (["test1", "test2"], True, 3),
        (["test1"], False, 3),
        (["test1"], True, 3),
    ])
    def test_in(self, check_list, inverse, precision):
        if len(check_list) < 2:
            with self.assertRaises(ConseilException):
                self.c.query(self.c.Accounts).in_(self.c.Accounts.Accountid, 
                                                       check_list, inverse, precision)
        else:
            self.c.query(self.c.Accounts).in_(self.c.Accounts.Accountid, 
                                                    check_list, inverse, precision)
            if precision is None:
                self.assertEqual(self.c._temp_query['predicates'], [{
                    'field': 'account_id',
                    'operation': 'in',
                    'set': check_list,
                    'inverse': inverse
                }])
            else:
                self.assertEqual(self.c._temp_query['predicates'], [{
                    'field': 'account_id',
                    'operation': 'in',
                    'set': check_list,
                    'inverse': inverse,
                    'precision': precision
                }])

    @parameterized.expand([
        ([100, 200], False, None),
        ([100, 200], True, None),
        ([100], False, None),
        ([100], True, None),
        ([100, 200], False, 3),
        ([100, 200], True, 3),
        ([100], False, 3),
        ([100], True, 3),
    ])
    def test_between(self, check_list, inverse, precision):
        if len(check_list) != 2:
            with self.assertRaises(ConseilException):
                self.c.query(self.c.Accounts).between(self.c.Accounts.Accountid, 
                                                      check_list, inverse, precision)
        else:
            self.c.query(self.c.Accounts).between(self.c.Accounts.Accountid, 
                                                  check_list, inverse, precision)
            if precision is None:
                self.assertEqual(self.c._temp_query['predicates'], [{
                    'field': 'account_id',
                    'operation': 'between',
                    'set': check_list,
                    'inverse': inverse
                }])
            else:
                self.assertEqual(self.c._temp_query['predicates'], [{
                    'field': 'account_id',
                    'operation': 'between',
                    'set': check_list,
                    'inverse': inverse,
                    'precision': precision
                }])

    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_like(self, inverse):
        self.c.query(self.c.Accounts).like(self.c.Accounts.Accountid, "template", inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
                    'field': 'account_id',
                    'operation': 'like',
                    'set': ["template"],
                    'inverse': inverse
                }])

    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_less_than(self, inverse):
        self.c.query(self.c.Accounts).less_than(self.c.Accounts.Accountid, 10, inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
            'field': 'account_id',
            'operation': 'lt',
            'set': [10],
            'inverse': inverse
        }])
    
    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_greater_than(self, inverse):
        self.c.query(self.c.Accounts).greater_than(self.c.Accounts.Accountid, 10, inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
            'field': 'account_id',
            'operation': 'gt',
            'set': [10],
            'inverse': inverse
        }])
    
    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_equals(self, inverse):
        self.c.query(self.c.Accounts).equals(self.c.Accounts.Accountid, 10, inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
            'field': 'account_id',
            'operation': 'eq',
            'set': [10],
            'inverse': inverse
        }])
    
    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_startsWith(self, inverse):
        self.c.query(self.c.Accounts).startsWith(self.c.Accounts.Accountid, "10", inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
            'field': 'account_id',
            'operation': 'startsWith',
            'set': ["10"],
            'inverse': inverse
        }])
    
    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_endsWith(self, inverse):
        self.c.query(self.c.Accounts).endsWith(self.c.Accounts.Accountid, "10", inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
            'field': 'account_id',
            'operation': 'endsWith',
            'set': ["10"],
            'inverse': inverse
        }])
     
    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_before(self, inverse):
        self.c.query(self.c.Accounts).before(self.c.Accounts.Accountid, 10, inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
            'field': 'account_id',
            'operation': 'before',
            'set': [10],
            'inverse': inverse
        }])
    
    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_after(self, inverse):
        self.c.query(self.c.Accounts).after(self.c.Accounts.Accountid, 10, inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
            'field': 'account_id',
            'operation': 'after',
            'set': [10],
            'inverse': inverse
        }])
    
    @parameterized.expand([
        (False,),
        (True,),
    ])
    def test_isnull(self, inverse):
        self.c.query(self.c.Accounts).isnull(self.c.Accounts.Accountid, inverse)
        self.assertEqual(self.c._temp_query['predicates'], [{
            'field': 'account_id',
            'operation': 'isnull',
            'set': [],
            'inverse': inverse
        }])

    @parameterized.expand([
        ('test',),
        (None,),
    ])
    def test_get(self, uri):
        self.c._temp_request = uri
        self.c._temp_query = {}
        data = self.c.query(self.c.Accounts).get()
        self.assertEqual(data, [1])
        self.assertEqual(self.c._query_platform, None)
        self.assertEqual(self.c._query_network, None)
        self.assertEqual(self.c._temp_request, '')
        self.assertEqual(self.c._temp_query, {
            'fields': [],
            'predicates': [],
            'limit': 5
        })
        self.assertEqual(self.c._temp_entity, None)
    

if __name__ == '__main__':
    unittest.main()
