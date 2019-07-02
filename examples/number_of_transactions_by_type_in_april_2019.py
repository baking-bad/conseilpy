from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Operation = conseil.tezos.alphanet.operations

    query = Operation.query(Operation.kind, Operation.operation_group_hash.count()) \
        .filter(Operation.timestamp.between(1554076800000, 1556668799000)) \
        .order_by(Operation.operation_group_hash.desc()) \
        .limit(20)

    pprint(query.payload())
    print(query.all(output='csv'))
