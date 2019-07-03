from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Account = conseil.tezos.alphanet.accounts

    query = Account.query(Account.delegate_value, Account.balance.sum()) \
        .filter(Account.delegate_value.isnot(None)) \
        .order_by(Account.balance.desc()) \
        .limit(50)

    pprint(query.payload())
    print(query.all(output='csv'))
