# ConseilPy
[![Build Status](https://travis-ci.org/baking-bad/conseilpy.svg?branch=master)](https://travis-ci.org/baking-bad/conseilpy)
[![Made With](https://img.shields.io/badge/made%20with-python-blue.svg?)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python toolkit for [Conseil](https://cryptonomic.github.io/Conseil) blockchain indexer

## Installation

Python 3.6+ required

```bash
$ pip install conseilpy
```

## Usage

### Quickstart

```python
from conseil import conseil

Account = conseil.tezos.alphanet.accounts
Account.query(Account.acccount_id, Account.balance) \
    .filter(Account.script.is_(None), 
            Account.account_id.startswith('KT1')) \
    .order_by(Account.balance.desc()) \
    .limit(5) \
    .all()
```

### Client initialization
If using a default conseil client is not an option you can instantiate it yourself:
```python
from conseil.api import ConseilApi
from conseil.core import Client

conseil = Client(ConseilApi(
    api_key='<API_KEY>',
    api_host='<API_HOST>',
    api_version=2
))
```

### Exploring database schema
Conseil metadata has the following tree structure: 
platform / network / entity / attribute / value

So you can simply access any node by name:
```python
>>> from conseil import conseil
>>> print(conseil.tezos.alphanet.operations.kind.transaction)
'transaction'
```

Autocompletion and docstrings are available in Jupyter:
```python
>>> from conseil import conseil
>>> conseil
Path
metadata/platforms

Platforms
.tezos

>>> conseil.tezos.alphanet
Path
metadata/tezos/alphanet/entities

.query()
Request an entity or specific fields
:param args: Array of attributes (of a common entity) or a single entity
:return: DataQuery

Entities
.accounts
.balance_updates
.ballots
.blocks
.delegates
.fees
.operation_groups
.operations
.proposals
.rolls
```

[View](https://github.com/Cryptonomic/Conseil/blob/master/doc/conseil.sql) database schema

### Selecting fields


### Filtering results


### Data aggregation


### Sorting results


### Query execution