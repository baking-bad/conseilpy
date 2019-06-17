from conseilpy.conseil import ConseilException
from unittest.mock import MagicMock

__all__ = ['MockApi']

responses = {
    'metadata/platforms': [{
        "name": "tezos",
        "displayName": "Tezos"
    }],
    'metadata/tezos/networks': [{
        "name": "alphanet",
        "displayName": "Alphanet",
        "platform": "tezos",
        "network": "alphanet"
    }],
    'metadata/tezos/alphanet/entities': [{
        "name": "accounts",
        "displayName": "Accounts",
        "count": 19587
    }],
    'metadata/tezos/alphanet/accounts/attributes': [{
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
    }]
}

class MockApi(MagicMock):
    def get(self, uri: str):
        return responses.get(uri)

    def post(self, uri, data):
        if uri is None:
            raise ConseilException('test')
        return [1]
