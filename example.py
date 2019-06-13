from loguru import logger

from conseilpy import Conseil, AggMethod


if __name__ == '__main__':
    key = ''
    with open('api_key', 'r') as f:
        key = f.read()

    api = Conseil(key, platform="tezos", network="alphanet")

    # /v2/data/tezos/<network>/accounts

    api.query(api.Account). \
        select([api.Account.Address]). \
        startsWith(api.Account.Address, "KT1"). \
        isnull(api.Account.Script, inverse=True). \
        limit(10). \
        get()
