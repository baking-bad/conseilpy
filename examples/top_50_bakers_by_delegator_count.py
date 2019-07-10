from conseil import conseil
from pprint import pprint


if __name__ == '__main__':
    Account = conseil.tezos.alphanet.accounts

    query = Account.query(Account.delegate_value, Account.account_id.count()) \
        .filter(Account.delegate_value.isnot(None)) \
        .order_by(Account.account_id.count().desc()) \
        .limit(50)

    pprint(query.payload())
    print(query.all(output='csv'))
