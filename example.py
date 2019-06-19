from loguru import logger

from conseilpy import Conseil, AggMethod, ConseilApi


if __name__ == '__main__':
    key = ''
    with open('api_key', 'r') as f:
        key = f.read()

    api = ConseilApi(key)
    c = Conseil(api, platform="tezos", network="alphanet")

    # /v2/data/tezos/<network>/accounts

    data = c.query(c.Account). \
        select([c.Account.Address]). \
        startsWith(c.Account.Address, "KT1"). \
        isnull(c.Account.Script, inverse=True). \
        limit(10). \
        get()

    logger.debug(data)
