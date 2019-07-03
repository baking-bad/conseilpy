from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Account = conseil.tezos.alphanet.accounts

    query = Account.query(Account.account_id) \
        .filter(Account.account_id.startswith('KT1'),
                Account.script.isnot(None)) \
        .limit(10000)

    pprint(query.payload())
    print(query.all(output='csv'))
