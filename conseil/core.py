from decimal import Decimal

from conseil.query import MetadataQuery, DataQuery
from conseil.api import ConseilException


def not_(predicate: dict):
    """
    Inverse predicate
    :param predicate: Predicate to invert
    :return: dict
    """
    res = predicate.copy()
    res['inverse'] = True
    return res


def and_(*predicates) -> list:
    return list(predicates)


def or_(*predicates) -> list:
    """
    Returns flat list of predicates divided by groups (OR)
    :param predicates: list of predicates or list of predicates is accepted
    :return: list
    """
    res = list()

    for i, item in enumerate(list(predicates)):
        if isinstance(item, dict):
            assert 'group' not in item, predicates
            res.append({'group': f'g{i}', **item})
        elif isinstance(item, list):
            for sub_item in item:
                assert isinstance(sub_item, dict), predicates
                assert 'group' not in sub_item, predicates
                res.append({'group': f'g{i}', **sub_item})
        else:
            assert False, predicates

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
        return DataQuery(self.api, **kwargs)

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
        return self._spawn(
            attribute_id=f'{function}_{self["attribute_id"]}',
            aggregation={
                'field': self['attribute_id'],
                'function': function
            }
        )

    def in_(self, *args):
        """
        Select elements occurring in the given list (predicate)
        :param args: Unpacked list
        :return: dict
        """
        if len(args) == 0:
            return self.is_(None)
        if len(args) == 1:
            return self.is_(args[0])
        return self._predicate('in', *args)

    def notin_(self, *args):
        """
        Select elements not occurring in the given list (predicate)
        :param args: Unpacked list
        :return: dict
        """
        if len(args) == 0:
            return self.isnot(None)
        if len(args) == 1:
            return self.isnot(args[0])
        return self._predicate('in', *args, inverse=True)

    def is_(self, value):
        """
        Select elements that are equal to given value (predicate)
        :param value: Anything
        :return: dict
        """
        if value is None:
            return self._predicate('isnull')
        return self._predicate('eq', value)

    def isnot(self, value):
        """
        Select elements that are not equal to given value (predicate)
        :param value: Anything
        :return: dict
        """
        if value is None:
            return self._predicate('isnull', inverse=True)
        return self._predicate('eq', value, inverse=True)

    def between(self, first, second):
        """
        Select elements lying in given range (predicate)
        :param first: Range start, int or Decimal
        :param second: Range end, int or Decimal
        :return: dict
        """
        return self._predicate('between', first, second)

    def like(self, value):
        """
        Select elements containing given string (predicate)
        :param value: String
        :return: dict
        """
        return self._predicate('like', value)

    def notlike(self, value):
        """
        Select elements not containing given string (predicate)
        :param value: String
        :return: dict
        """
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
        """
        Select elements starting with given string (predicate)
        :param value: String
        :return: dict
        """
        return self._predicate('startsWith', value)

    def endswith(self, value):
        """
        Select elements ending with given string (predicate)
        :param value: String
        :return: dict
        """
        return self._predicate('endsWith', value)

    def asc(self):
        """
        Sort in ascending order (sorting)
        :return: dict
        """
        return self._sort_order('asc')

    def desc(self):
        """
        Sort in descending order (sorting)
        :return: dict
        """
        return self._sort_order('desc')

    def sum(self):
        """
        Select sum of elements across this column (used in aggregation)
        :return: Attribute
        """
        return self._aggregate('sum')

    def count(self):
        """
        Select number of elements across this column (used in aggregation)
        :return: Attribute
        """
        return self._aggregate('count')

    def avg(self):
        """
        Select average element across this column (used in aggregation)
        :return: Attribute
        """
        return self._aggregate('avg')

    def min(self):
        """
        Select minimum element across this column (used in aggregation)
        :return: Attribute
        """
        return self._aggregate('min')

    def max(self):
        """
        Select maximum element across this column (used in aggregation)
        :return: Attribute
        """
        return self._aggregate('max')

    def label(self, label):
        """
        Rename column in the resulting object
        :param label: New name for this field
        :return: Attribute
        """
        return self._spawn(label=label)


class Entity(MetadataQuery):
    __child_key__ = 'attribute_id'
    __child_class__ = Attribute
    __query_path__ = 'metadata/{platform_id}/{network_id}/{entity_id}/attributes'

    def query(self, *args) -> DataQuery:
        """
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
        return DataQuery(self.api, **kwargs)


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
        return DataQuery(self.api, **kwargs)


class Platform(MetadataQuery):
    __child_key__ = 'network_id'
    __child_class__ = Network
    __query_path__ = 'metadata/{platform_id}/networks'


class ConseilClient(MetadataQuery):
    __child_key__ = 'platform_id'
    __child_class__ = Platform
    __query_path__ = 'metadata/platforms'
