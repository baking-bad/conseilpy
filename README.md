# ConseilPy
[![PyPI version](https://badge.fury.io/py/conseil.svg?)](https://badge.fury.io/py/conseil)
[![Build Status](https://travis-ci.org/baking-bad/conseilpy.svg?branch=master)](https://travis-ci.org/baking-bad/conseilpy)
[![Made With](https://img.shields.io/badge/made%20with-python-blue.svg?)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python toolkit for [Conseil](https://cryptonomic.github.io/Conseil) blockchain indexer

## Installation

Python 3.6+ required

```bash
$ pip install conseil
```

## Usage

ConseilPy is a lot like Sqlalchemy, so if you're familiar with it, you can easily cook queries.

![It's time to cook](https://memegenerator.net/img/instances/48258954.jpg)

### Quickstart
Get top 5 delegators by balance
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

See more [examples](https://github.com/baking-bad/conseilpy/tree/master/examples)

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
transaction
```

Autocompletion `Shift + Tab` and docstrings are available in Jupyter:
```python
>>> conseil
Path
metadata/platforms

Platforms
.tezos

>>> conseil.tezos.alphanet
Path
metadata/tezos/alphanet/entities

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

Alternatively you can check full [SQL schema](https://github.com/Cryptonomic/Conseil/blob/master/doc/conseil.sql)

### Selecting fields
Conseil doesn't support joins at the moment so you can request attributes for a single entity only. 

```python
from conseil import conseil

c = conseil.tezos.alphanet

# select all fields
c.query(c.accounts)
c.accounts.query()

# select specific fields
c.query(c.accounts.balance, c.accounts.account_id)
c.accounts.query(c.accounts.balance, c.accounts.account_id)

# select single field
c.accounts.balance.query()
```

### Filtering results
Conseil receives a conjunction of predicates, which can be inverted by one, but not together.
Predicate syntax is similar to Sqlalchemy, but has less operations.

```python
from conseil import conseil
from conseil.core import not_

Account = conseil.tezos.alphanet.accounts
Account.query() \
    .filter(not_(Account.account_id.startswith('tz')),
            Account.script.is_(None),
            Account.balance > 0)
```

Here is a full list of supported operations:

| Conseil operation | Filter             | Inversed                |
| ----------------- | ------------------ | ----------------------- |
| in                | `x.in_(a, b, ...)` | `x.notin_(a, b, ...)`   |
| between           | `x.between(a, b)`  | `not_(x.between(a, b))` |
| like              | `x.like(a)`        | `x.notlike(a)`          |
| lt                | `x < a`            | `x >= a`                |
| gt                | `x > a`            | `x <= a`                |
| eq                | `x == a`           | `x != a`                |
| startsWith        | `x.startswith(a)`  | `not_(x.startsWith(a))` |
| endsWith          | `x.endswith(a)`    | `not_(x.endswith(a))`   |
| isnull            | `x.is_(None)`      | `x.isnot(None)`         |

You can also use `filter_by` for simple queries:

```python
from conseil import conseil

conseil.tezos.alphanet.accounts.query() \
    .filter_by(account_id='tzkt')
```

### Data aggregation

This is an important concept to understand. In Conseil you specify which columns will be aggregated and the rest of them are used in `GROUP BY` clause. Here is an example:

```python
from conseil import conseil

Block = conseil.tezos.alphanet.blocks
Block.query(Block.baker, Block.level.count(), Block.timestamp.max())  
# will be compiled to SELECT baker, COUNT(level), MAX(timestamp) FROM blocks GROUP BY baker
```

Additionally, you can specify `HAVING` predicates if you want to filter results by aggregated column:

```python
from conseil import conseil

Block = conseil.tezos.alphanet.blocks
Block.query(Block.baker, Block.level.count()) \
    .having(Block.level.count() > 1)  # you have to specify aggregation function here as well
```

Here is the list of supported aggregation functions:

* `count`
* `sum`
* `avg`
* `min`
* `max`

If you want to group by some fields but not include them in the result use `group_by` method:

```python
from conseil import conseil

Block = conseil.tezos.alphanet.blocks
Block.query(Block.level.count()) \
	.group_by(Block.baker)
```

### Sorting and limiting results

This is similar to Sqlalchemy as well, you can specify one or multiple sort columns with optional descending modifier.

```python
from conseil import conseil

Account = conseil.tezos.alphanet.accounts
Account.query() \
    .order_by(Account.balance.desc(), Account.account_id) \
    .limit(20)
```

You can sort by aggregated column too:

```python
from conseil import conseil

Operation = conseil.tezos.alphanet.operations
Operation.query(Operation.source, Operation.amount.avg()) \
    .order_by(Operation.amount.avg().desc()) \
    .limit(50)
```

### Query preview

So you have cooked a simple query and want to see the resulting Conseil request body.

```python
from conseil import conseil

Account = conseil.tezos.alphanet.accounts
query = Account.query() \
    .order_by(Account.balance.desc()) \
    .limit(1)
```

Then you can simply:

```python
>>> query
Path
data/tezos/alphanet/accounts

Query
{"aggregation": [],
 "fields": [],
 "limit": 1,
 "orderBy": [{"direction": "desc", "field": "balance"}],
 "output": "json",
 "predicates": []}
```

### Execution

It's time to submit our query and get some data.

```python
from conseil import conseil

Account = conseil.tezos.alphanet.accounts
```

#### Return multiple rows

```python
query = Account.query()

query.all()  # will return List[dict] (default output type)
query.all(output='csv')  # will return string (csv)
```

#### Return single row

```python
query = Account.query() \
	.filter_by(account_id='tzkt')

query.one()  # will fail if there is no account with such id or there are many
query.one_or_none()  # will handle the exception and return None
```

#### Return scalar

```python
query = Account.balance.query() \
	.order_by(Account.balance.desc()) \
    .limit(1)

query.scalar()  # will return single numeric value
```

#### Return vector

```python
query = Operation.query(Operation.timestamp) \
    .filter_by(source='tzkt')
    
query.vector()  # will return flat list of timestamps
```

### Precision
Conseil allows to specify numeric column precision. In order to use this functionality use `decimal` type. For example:

```python
from conseil import conseil
from decimal import Decimal

Account = conseil.tezos.alphanet.accounts
Account.query(Account.balance) \
    .filter(Account.balance > Decimal('0.1'), 
            Account.balance < Decimal('0.01'))  # precision will be 2 (max)
```

### Renaming fields
You can change names of requested fields in the resulting json/csv:

```python
from conseil import conseil

Account = conseil.tezos.alphanet.accounts
Account.query(Account.account_id.label('address'))
```