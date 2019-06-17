# ConseilPy

This is library for blockchain indexer Conseil in Python 3. 

## Installation

Requirements: Python 3.6.7 or above

To install it execute command 

```bash
pip3 install conseilpy
```

## Usage

First of all, you need to create `Conseil` object. To do it you need `ConseilApi` object. For example:

```python
API_KEY = 'very_secret_key'

api = ConseilApi(API_KEY)
c = Conseil(api)

# or

c = Conseil(ConseilApi(API_KEY))

```

All entities and attributes and its description will download dynamically from Conseil API. More info about Conseil data you can find in [docs](https://cryptonomic.github.io/Conseil/#/?id=entities). For example, to get list of availiable entities in Jupyter notebook just press `Tab` after  `c.` and to read docs press `Ctrl+Tab`.

All queries builds by chaining. Data returns in JSON-format. For example, request from Conseil [docs](https://cryptonomic.github.io/Conseil/#/?id=all-originated-accounts-which-are-smart-contracts) which returns all originated accounts which are smart contracts:

```python
data = c.query(c.Account). \
    select([c.Account.Address]). \
    startsWith(c.Account.Address, "KT1"). \
    isnull(c.Account.Script, inverse=True). \
    limit(10). \
    get()
```

`query` - set requested object

`select` - ser requests fields

`startsWith`, `isnull`, `limit` - some filters

`get` - return result of query
