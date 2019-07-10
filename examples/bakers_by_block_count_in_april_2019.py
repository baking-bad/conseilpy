from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Block = conseil.tezos.alphanet.blocks

    query = Block.query(Block.baker, Block.level.count()) \
        .filter(Block.timestamp.between(1554076800000, 1556668799000)) \
        .order_by(Block.level.count().desc()) \
        .having(Block.level.count() > 10000) \
        .limit(5)

    pprint(query.payload())
    print(query.all(output='csv'))
