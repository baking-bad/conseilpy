from decimal import Decimal

from conseil.query import MetadataQuery, DataQuery
from conseil.api import ConseilException


def not_(predicate: dict):
    res = predicate.copy()
    res['inverse'] = True
    return res


class Attribute(MetadataQuery):
    __query_path__ = 'metadata/{platform_id}/{network_id}/{entity_id}/{attribute_id}'

    def __hash__(self):
        return id(self)

    def __getattr__(self, item):
        return item

    def query(self) -> DataQuery:
        """
        Request specific attribute
        :return: DataQuery
        """
        kwargs = self._extend(attributes={self['attribute_id']: self})
        return DataQuery(self._api, **kwargs)

    def _predicate(self, operation, *args, inverse=False):
        predicate = {
            'field': self['attribute_id'],
            'operation': operation,
            'set': list(args),
            'inverse': inverse
        }

        if args and all(map(lambda x: isinstance(x, Decimal), args)):
            precision = max(map(lambda x: max(0, -x.as_tuple().exponent), args))
            predicate['precision'] = precision

        return predicate

    def _sort_order(self, direction):
        return {
            'field': self['attribute_id'],
            'direction': direction
        }

    def _aggregate(self, function):
        return self._spawn(aggregation={
            'field': self['attribute_id'],
            'function': function
        })

    def in_(self, *args):
        if len(args) == 0:
            return self.is_(None)
        if len(args) == 1:
            return self.is_(args[0])
        return self._predicate('in', *args)

    def notin_(self, *args):
        if len(args) == 0:
            return self.isnot(None)
        if len(args) == 1:
            return self.isnot(args[0])
        return self._predicate('in', *args, inverse=True)

    def is_(self, value):
        if value is None:
            return self._predicate('isnull')
        return self._predicate('eq', value)

    def isnot(self, value):
        if value is None:
            return self._predicate('isnull', inverse=True)
        return self._predicate('eq', value, inverse=True)

    def between(self, first, second):
        return self._predicate('between', first, second)

    def like(self, value):
        return self._predicate('like', value)

    def notlike(self, value):
        return self._predicate('like', value, inverse=True)

    def __lt__(self, other):
        return self._predicate('lt', other)

    def __ge__(self, other):
        return self._predicate('lt', other, inverse=True)

    def __gt__(self, other):
        return self._predicate('gt', other)

    def __le__(self, other):
        return self._predicate('gt', other, inverse=True)

    def __eq__(self, other):
        return self.is_(other)

    def __ne__(self, other):
        return self.isnot(other)

    def startswith(self, value):
        return self._predicate('startsWith', value)

    def endswith(self, value):
        return self._predicate('endsWith', value)

    def asc(self):
        return self._sort_order('asc')

    def desc(self):
        return self._sort_order('desc')

    def sum(self):
        return self._aggregate('sum')

    def count(self):
        return self._aggregate('count')

    def avg(self):
        return self._aggregate('avg')

    def min(self):
        return self._aggregate('min')

    def max(self):
        return self._aggregate('max')

    def label(self, label):
        return self._spawn(label=label)


class Entity(MetadataQuery):
    __child_key__ = 'attribute_id'
    __child_class__ = Attribute
    __query_path__ = 'metadata/{platform_id}/{network_id}/{entity_id}/attributes'

    def query(self, *args) -> DataQuery:
        """__query_path__
        Request an entity or specific fields
        :param args: Array of attributes (of a common entity) or a single entity
        :return: DataQuery
        """
        if all(map(lambda x: isinstance(x, Attribute), args)):
            attributes = {x['attribute_id']: x for x in args}
            if any(map(lambda x: x['entity_id'] != self['entity_id'], args)):
                raise ConseilException('Entity mismatch')
        elif len(args) == 0:
            attributes = dict()
        else:
            raise ConseilException('List of attributes (single entity) or an entity is allowed')
        kwargs = self._extend(attributes=attributes)
        return DataQuery(self._api, **kwargs)


class Network(MetadataQuery):
    __child_key__ = 'entity_id'
    __child_class__ = Entity
    __query_path__ = 'metadata/{platform_id}/{network_id}/entities'

    def query(self, *args) -> DataQuery:
        """
        Request an entity or specific fields
        :param args: Array of attributes (of a common entity) or a single entity
        :return: DataQuery
        """
        if all(map(lambda x: isinstance(x, Attribute), args)):
            attributes = {x['attribute_id']: x for x in args}
            if any(map(lambda x: x['entity_id'] != args[0]['entity_id'], args)):
                raise ConseilException('Mixed entities')
        elif len(args) == 1 and isinstance(args[0], Entity):
            attributes = dict()
        else:
            raise ConseilException('List of attributes (single entity) or an entity is allowed')

        kwargs = self._extend(
            attributes=attributes,
            entity_id=args[0]['entity_id']
        )
        return DataQuery(self._api, **kwargs)


class Platform(MetadataQuery):
    __child_key__ = 'network_id'
    __child_class__ = Network
    __query_path__ = 'metadata/{platform_id}/networks'


class Client(MetadataQuery):
    __child_key__ = 'platform_id'
    __child_class__ = Platform
    __query_path__ = 'metadata/platforms'
