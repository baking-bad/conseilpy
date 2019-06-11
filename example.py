from loguru import logger

from api.entity import Account
from api.conseil import Conseil, AggMethod


if __name__ == '__main__':
    key = ''
    with open('api_key', 'r') as f:
        key = f.read()

    api = Conseil(key)

    # /v2/data/tezos/<network>/accounts

    api.platform("tezos").network("alphanet"). \
        query(Account). \
        select([Account.account_id]). \
        startsWith(Account.account_id, "KT1"). \
        isnull(Account.script, inverse=True). \
        limit(10). \
        get()
