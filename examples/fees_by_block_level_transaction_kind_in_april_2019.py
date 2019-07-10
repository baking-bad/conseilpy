from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Operation = conseil.tezos.alphanet.operations

    query = Operation.query(Operation.block_level, Operation.kind, Operation.fee.sum(), Operation.fee.avg()) \
        .filter(Operation.fee > 0,
                Operation.timestamp.between(1554076800000, 1556668799000)) \
        .order_by(Operation.fee.sum().desc()) \
        .limit(100000)

    pprint(query.payload())
    print(query.all(output='csv'))
