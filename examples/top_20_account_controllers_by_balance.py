from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Account = conseil.tezos.alphanet.accounts

    query = Account.query(Account.manager, Account.balance.sum()) \
        .filter(Account.script.is_(None)) \
        .order_by(Account.balance.sum().desc()) \
        .limit(20)

    pprint(query.payload())
    print(query.all(output='csv'))
