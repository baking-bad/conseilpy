from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Operation = conseil.tezos.alphanet.operations

    query = Operation.query(Operation.source, Operation.operation_group_hash.count()) \
        .filter(Operation.kind == Operation.kind.origination,
                Operation.script.isnot(None)) \
        .order_by(Operation.operation_group_hash.count().desc()) \
        .limit(10)

    pprint(query.payload())
    print(query.all(output='csv'))
