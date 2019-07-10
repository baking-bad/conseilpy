from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Operation = conseil.tezos.alphanet.operations

    query = Operation.query(Operation.block_level, Operation.operation_group_hash.count()) \
        .filter(Operation.timestamp.between(1554076800000, 1556668799000),
                Operation.kind.in_(Operation.kind.transaction,
                                   Operation.kind.origination,
                                   Operation.kind.delegation,
                                   Operation.kind.activation,
                                   Operation.kind.reveal)) \
        .order_by(Operation.operation_group_hash.count().desc()) \
        .limit(100)

    pprint(query.payload())
    print(query.all(output='csv'))
