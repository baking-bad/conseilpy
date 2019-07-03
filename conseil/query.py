import re
from os.path import basename
from functools import lru_cache
from pprint import pformat

from conseil.api import ConseilApi, ConseilException


def get_attr_docstring(class_type, attr_name):
    attr = getattr(class_type, attr_name, None)
    if attr and attr.__doc__:
        return re.sub(r' {3,}', '', attr.__doc__)


class Query:
    __query_path__ = None

    def __init__(self, api=ConseilApi(), **kwargs):
        self._api = api
        self._kwargs = kwargs

    def _extend(self, **kwargs):
        params = self._kwargs.copy()
        for key, value in kwargs.items():
            if isinstance(params.get(key), list):
                params[key].extend(value)
            else:
                params[key] = value
        return params

    def _spawn(self, **kwargs):
        params = self._extend(**kwargs)
        return self.__class__(self._api, **params)

    @property
    def _query_path(self):
        return self.__query_path__.format(**self._kwargs)

    def __getitem__(self, item):
        return self._kwargs.get(item)

    def __repr__(self):
        docstring = ''
        if self.__query_path__:
            docstring += f'Path\n{self._query_path}\n\n'

        attrs = filter(lambda x: not x.startswith('_'), dir(self.__class__))
        for attr in attrs:
            if type(getattr(self.__class__, attr)) == property:
                name = f'.{attr}'
            else:
                name = f'.{attr}()'
            info = get_attr_docstring(self.__class__, attr) or ''
            docstring += f'{name}{info}\n'

        return docstring


class MetadataQuery(Query):
    __child_key__ = None
    __child_class__ = None

    @lru_cache(maxsize=None)
    def _request(self):
        try:
            if self.__query_path__:
                return self._api.get(self._query_path).json()
        except ConseilException:
            pass
        return list()

    @property
    def _attr_names(self):
        return filter(lambda x: x,
                      map(lambda x: x.get('name', x) if isinstance(x, dict) else x,
                          self._request()))

    def __repr__(self):
        docstring = super(MetadataQuery, self).__repr__()

        attrs = '\n'.join(map(lambda x: f'.{x}', self._attr_names))
        if attrs:
            title = basename(self._query_path).capitalize()
            docstring += f'{title}\n{attrs}\n'

        return docstring

    def __call__(self):
        return self._request()

    def __dir__(self):
        return list(super(MetadataQuery, self).__dir__()) + list(self._attr_names)

    @lru_cache(maxsize=None)
    def __getattr__(self, item):
        if self.__child_class__:
            kwargs = {
                self.__child_key__: item,
                **self._kwargs
            }
            return self.__child_class__(self._api, **kwargs)
        raise ConseilException(item)


class DataQuery(Query):
    __query_path__ = 'data/{platform_id}/{network_id}/{entity_id}'

    def __repr__(self):
        docstring = super(DataQuery, self).__repr__()
        docstring += f'Query\n{pformat(self.payload())}\n\n'
        return docstring

    def payload(self):
        """
        Resulting Conseil query
        :return: object
        """
        attributes = self['attributes'] or {}
        having = self['having'] or []
        orders = self['order_by'] or []

        for predicate in having:
            try:
                attributes[predicate['field']]['aggregation']['predicate'] = predicate
            except (KeyError, TypeError):
                raise ConseilException(f'Orphan HAVING predicate on `{predicate["field"]}`')

        aggregation = [x['aggregation'] for x in attributes.values() if x['aggregation']]

        for order in orders:
            try:
                function = attributes[order['field']]['aggregation']['function']
                order['field'] = f'{function}_{order["field"]}'
            except (KeyError, TypeError):
                pass

        return {
            'fields': list(attributes.keys()),
            'predicates': list(self['predicates'] or []),
            'aggregation': aggregation,
            'orderBy': orders,
            'limit': self['limit'],
            'output': self['output'] or 'json'
        }

    def filter(self, *args):
        """
        Use predicates to filter results (conjunction)
        :param args: array of predicates
        :return: DataQuery
        """
        return self._spawn(predicates=args)

    def filter_by(self, **kwargs):
        """
        Use simple `eq` predicates to filter results (conjunction)
        :param kwargs: pairs <attribute_id>=<value>
        :return: DataQuery
        """
        predicates = [
            {
                'field': k,
                'operation': 'eq',
                'set': [v],
                'inverse': False
            }
            for k, v in kwargs.items()
        ]
        return self._spawn(predicates=predicates)

    def order_by(self, *args):
        """
        Sort results by specified columns
        :param args: one or many sort rules
        :return: DataQuery
        """
        order_by = [x if isinstance(x, dict) else x.asc() for x in args]
        return self._spawn(order_by=order_by)

    def limit(self, limit: int):
        """
        Limit results count
        :param limit: integer
        :return: DataQuery
        """
        return self._spawn(limit=limit)

    def having(self, *args):
        """
        Filter results by aggregated column
        :param args: array of predicates on aggregated columns
        :return: DataQuery
        """
        return self._spawn(having=args)

    def all(self, output='json'):
        """
        Get all results
        :param output: output format (json/csv), default is JSON
        :return: list (json) or string (csv)
        """
        self._kwargs['output'] = output
        res = self._api.post(path=self._query_path, json=self.payload())
        if output == 'json':
            return res.json()
        return res.text

    def one(self):
        """
        Get single result, fail if there are no or multiple records (json only)
        :return: object
        """
        res = self.all()
        if len(res) == 0:
            raise ConseilException('Not found')
        if len(res) > 1:
            raise ConseilException('Multiple results')
        return res[0]

    def one_or_none(self):
        """
        Get single result or None (do not fail)
        :return: object or None
        """
        try:
            return self.one()
        except ConseilException:
            pass

    def scalar(self):
        """
        Get value of a single attribute (single column, single row)
        :return: scalar
        """
        res = self.one()
        if len(res) != 1:
            raise ConseilException('Multiple keys')
        return next(iter(res.values()))
