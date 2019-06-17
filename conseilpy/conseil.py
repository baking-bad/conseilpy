import requests
from requests.exceptions import Timeout
from loguru import logger
from typing import List
from enum import Enum
from cachetools import cached, TTLCache

from .data_types import Attribute, Entity
from .exceptions import ConseilException
from .api import ConseilApi
from .utils import prepare_name


__all__ = ["OutputType", "AggMethod", "Conseil"]


class OutputType(Enum):
    CSV = "csv"
    JSON = "json"


class AggMethod(Enum):
    SUM = "sum"
    COUNT = "count"
    MAX = "max"
    MIN = "min"
    AVG = "avg"


class Conseil:
    __url__ = "https://conseil-dev.cryptonomic-infra.tech"

    def __init__(self, api: ConseilApi, platform=None, network=None):
        self._api = api
        self._default_platform = platform
        self._default_network = network
        self._init_entities()
        self._reset_temp()        

    def _reset_temp(self):
        self._query_platform = None
        self._query_network = None
        self._temp_request = ''
        self._temp_query = {
            'fields': [],
            'predicates': [],
            'limit': 5
        }
        self._temp_entity = None

    def _init_entities(self):
        entities = self.entities()
        for x in entities:
            self.__setattr__(prepare_name(x['displayName']), Entity(self._api, self._default_platform, self._default_network, **x))

    @cached(cache=TTLCache(maxsize=4096, ttl=600))
    def platforms(self):
        return self._api.get('metadata/platforms')
    
    @cached(cache=TTLCache(maxsize=4096, ttl=600))
    def networks(self, platform_name=None):
        if platform_name is None:
            platform_name = self._default_platform
        return self._api.get(f'metadata/{platform_name}/networks')
    
    @cached(cache=TTLCache(maxsize=4096, ttl=600))
    def entities(self, platform_name=None, network=None):
        if platform_name is None:
            platform_name = self._default_platform
        if network is None:
            network = self._default_network
        return self._api.get(f'metadata/{platform_name}/{network}/entities')

    @cached(cache=TTLCache(maxsize=4096, ttl=600))
    def attributes(self, entity: str, platform_name=None, network=None):
        if platform_name is None:
            platform_name = self._default_platform
        if network is None:
            network = self._default_network
        return self._api.get(f'metadata/{platform_name}/{network}/{entity}/attributes')

    @cached(cache=TTLCache(maxsize=4096, ttl=600))
    def attribute_values(self, entity: str, attribute: str, platform_name=None, network=None):
        if platform_name is None:
            platform_name = self._default_platform
        if network is None:
            network = self._default_network
        return self._api.get(f'metadata/{platform_name}/{network}/{entity}/{attribute}/kind')
    
    @cached(cache=TTLCache(maxsize=4096, ttl=600))
    def attribute_values_with_prefix(self,
        entity: str, 
        attribute: str,
        prefix: str,
        platform_name=None, 
        network=None):
        if platform_name is None:
            platform_name = self._default_platform
        if network is None:
            network = self._default_network
        return self._api.get(f'metadata/{platform_name}/{network}/{entity}/{attribute}/{prefix}')

    def platform(self, name: str):
        self._query_platform = name
        return self

    def network(self, name: str):
        self._query_network = name
        return self
    
    def query(self, entity: Entity):
        if self._query_platform is None:
            if self._default_platform is None:
                raise ValueError('You must set platform. Please set `platform` in constructor or use Conseil.platform() method') 
            self._query_platform = self._default_platform
        
        if self._query_network is None:
            if self._default_network is None:
                raise ValueError('You must set network. Please set `network` in constructor or use Conseil.network() method') 
            self._query_network = self._default_network
        
        self._temp_request = f'data/{self._query_platform}/{self._query_network}/{entity.name}'
        self._temp_entity = entity
        return self

    def select(self, fields: List[Attribute]):
        self._temp_query['fields'] = [
            x.name 
            for x in fields 
            if self._temp_entity.name == x.entity 
        ]
        return self
    
    def limit(self, limit: int):
        self._temp_query['limit'] = limit
        return self

    def output(self, output_type: OutputType):
        self._temp_query['output'] = output_type.value
        return self

    def agg(self, field: Attribute, method: AggMethod):
        if 'aggregation' not in self._temp_query:
            self._temp_query['aggregation'] = list()
        
        self._temp_query['aggregation'].append({
            'field': field.name,
            'function': method.value
        })
        return self

    def order_by(self, field: Attribute, direction="asc"):
        if direction not in ["asc", "desc"]:
            raise ConseilException(f'Invalid sort direction: {direction}. Value must be "asc" or "desc"')

        if 'orderBy' not in self._temp_query:
            self._temp_query['orderBy'] = list()

        self._temp_query['orderBy'].append({
            'field': field.name,
            'direction': direction
        })
        return self

    def in_(self, field: Attribute, check_list: list, inverse=False, precision=None):
        if len(check_list) < 2:
            raise ConseilException("'in' requires two or more elements in check list")
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        req = {
            'field': field.name,
            'operation': 'in',
            'set': check_list,
            'inverse': inverse
        }
        if precision is not None:
            req['precision'] = precision
        self._temp_query['predicates'].append(req)
        return self
    
    def between(self, field: Attribute, check_list: list, inverse=False, precision=None):
        if len(check_list) != 2:
            raise ConseilException("'between' must have exactly two elements in check list")

        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        req = {
            'field': field.name,
            'operation': 'between',
            'set': check_list,
            'inverse': inverse
        }
        if precision is not None:
            req['precision'] = precision
        self._temp_query['predicates'].append(req)
        return self

    def like(self, field: Attribute, template: str, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'like',
            'set': [template],
            'inverse': inverse
        })
        return self
    
    def less_than(self, field: Attribute, value: object, inverse=False, precision=None):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        req = {
            'field': field.name,
            'operation': 'lt',
            'set': [value],
            'inverse': inverse
        }
        if precision is not None:
            req['precision'] = precision
        self._temp_query['predicates'].append(req)
        return self
    
    def greater_than(self, field: Attribute, value: object, inverse=False, precision=None):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        req = {
            'field': field.name,
            'operation': 'gt',
            'set': [value],
            'inverse': inverse
        }
        if precision is not None:
            req['precision'] = precision
        self._temp_query['predicates'].append(req)
        return self

    def equals(self, field: Attribute, value: object, inverse=False, precision=None):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        req = {
            'field': field.name,
            'operation': 'eq',
            'set': [value],
            'inverse': inverse
        }
        if precision is not None:
            req['precision'] = precision
        self._temp_query['predicates'].append(req)
        return self
    
    def startsWith(self, field: Attribute, value: str, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'startsWith',
            'set': [value],
            'inverse': inverse
        })
        return self
    
    def endsWith(self, field: Attribute, value: str, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'endsWith',
            'set': [value],
            'inverse': inverse
        })
        return self

    def before(self, field: Attribute, value: int, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'before',
            'set': [value],
            'inverse': inverse
        })
        return self

    def after(self, field: Attribute, value: int, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'after',
            'set': [value],
            'inverse': inverse
        })
        return self

    def isnull(self, field: Attribute, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'isnull',
            'set': [],
            'inverse': inverse
        })
        return self

    def get(self):
        logger.debug(f'Request: {self._temp_request}')
        logger.debug(f'Query: {self._temp_query}')
        data = list()
        try:
            data = self._api.post(self._temp_request, self._temp_query)
        except ConseilException as e:
            logger.exception(e)
        finally:
            self._reset_temp()
        return data
