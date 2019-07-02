from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Operation = conseil.tezos.alphanet.operations

    query = Operation.query(Operation.source, Operation.amount.sum()) \
        .filter(Operation.kind == Operation.kind.transaction,
                Operation.timestamp.between(1546300800000, 1577836799000)) \
        .order_by(Operation.amount.desc()) \
        .limit(100)

    pprint(query.payload())
    print(query.all(output='csv'))
