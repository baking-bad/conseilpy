from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Roll = conseil.tezos.alphanet.rolls

    query = Roll.query(Roll.pkh, Roll.rolls) \
        .order_by(Roll.block_level.desc(),
                  Roll.rolls.desc()) \
        .limit(20)

    pprint(query.payload())
    print(query.all(output='csv'))
