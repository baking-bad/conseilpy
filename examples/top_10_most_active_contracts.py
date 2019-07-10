from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Operation = conseil.tezos.alphanet.operations

    query = Operation.query(Operation.destination, Operation.operation_group_hash.count()) \
        .filter(Operation.kind == Operation.kind.transaction,
                Operation.destination.startswith('KT1'),
                Operation.parameters.isnot(None)) \
        .order_by(Operation.operation_group_hash.count().desc()) \
        .limit(10)

    pprint(query.payload())
    print(query.all(output='csv'))
