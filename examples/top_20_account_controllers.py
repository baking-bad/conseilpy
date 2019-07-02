from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Account = conseil.tezos.alphanet.accounts

    query = Account.query(Account.manager, Account.account_id.count()) \
        .filter(Account.balance > 0,
                Account.script.is_(None)) \
        .order_by(Account.account_id.desc()) \
        .limit(20)

    pprint(query.payload())
    print(query.all(output='csv'))
