import requests
from requests.exceptions import Timeout
from loguru import logger
from typing import List
from enum import Enum

from .entity import Entity
from .data_types import DataType
from .exceptions import ConseilException


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

    def __init__(self, api_key: str, api_version=None,  timeout=None):
        self._api_key = api_key
        self._api_version = api_version if api_version is not None else 2
        self._timeout = timeout if timeout is not None else 15
        self._reset_temp()        

    def _reset_temp(self):
        self._temp_request = ''
        self._temp_query = {
            'fields': [],
            'predicates': [],
            'limit': 5
        }
        self._temp_entity = None

    def _get(self, command, **kwargs):
        request_data = {key: value for key, value in kwargs.items() if value is not None}
        url = f'{self.__url__}/v{self._api_version}/{command}'

        headers = {
            'apiKey': self._api_key
        }
        try:
            response = requests.get(url, params=request_data, headers=headers, timeout=self._timeout)
            if response.status_code != 200:
                raise ConseilException(f'Invalid status code: {response.status_code}')
            return response.json()
        except Exception as e:
            raise ConseilException(e)
    
    def _post(self, command, data):
        url = f'{self.__url__}/v{self._api_version}/{command}'

        headers = {
            'apiKey': self._api_key
        }
        try:
            response = requests.post(url, json=data, headers=headers, timeout=self._timeout)
            if response.status_code != 200:
                raise ConseilException(f'Invalid status code: {response.status_code}')
            return response.json()
        except Exception as e:
            raise ConseilException(e)

    def platforms(self):
        return self._get('metadata/platforms')
    
    def networks(self, platform_name: str):
        return self._get(f'metadata/{platform_name}/networks')
    
    def entities(self, platform_name: str, network: str):
        return self._get(f'metadata/{platform_name}/{network}/entities')

    def attributes(self, platform_name: str, network: str, entity: str):
        return self._get(f'metadata/{platform_name}/{network}/{entity}/attributes')

    def attribute_values(self, platform_name: str, network: str, entity: str, attribute: str):
        return self._get(f'metadata/{platform_name}/{network}/{entity}/{attribute}/kind')
    
    def attribute_values_with_prefix(self, 
        platform_name: str, 
        network: str, 
        entity: str, 
        attribute: str,
        prefix: str):
        return self._get(f'metadata/{platform_name}/{network}/{entity}/{attribute}/{prefix}')

    def platform(self, name: str):
        self._temp_request = f'data/{name}'
        return self

    def network(self, name: str):
        self._temp_request = f'{self._temp_request}/{name}'
        return self
    
    def query(self, entity: Entity):
        self._temp_request = f'{self._temp_request}/{entity.__entity_name__}'
        self._temp_entity = entity
        return self

    def select(self, fields: List[DataType]):
        self._temp_query['fields'] = [
            x.name 
            for x in fields 
            if self._temp_entity.__entity_name__ == x.entity 
        ]
        return self
    
    def limit(self, limit: int):
        self._temp_query['limit'] = limit
        return self

    def output(self, output_type: OutputType):
        self._temp_query['output'] = output_type.value
        return self

    def agg(self, field: DataType, method: AggMethod):
        self._temp_query['aggregation'] = {
            'field': field.name,
            'function': method.value
        }
        return self

    def order_by(self, field: DataType, direction="asc"):
        if direction not in ["asc", "desc"]:
            raise ConseilException(f'Invalid sort direction: {direction}. Value must be "asc" or "desc"')

        if 'orderBy' not in self._temp_query:
            self._temp_query['orderBy'] = list()

        self._temp_query['orderBy'].append({
            'field': field.name,
            'direction': direction
        })
        return self

    def in_(self, field: DataType, check_list: list, inverse=False, precision=8):
        if len(check_list) < 2:
            raise ConseilException("'in' requires two or more elements in check list")
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'in',
            'set': check_list,
            'inverse': inverse,
            'precision': precision
        })
        return self
    
    def between(self, field: DataType, check_list: list, inverse=False, precision=8):
        if len(check_list) != 2:
            raise ConseilException("'between' must have exactly two elements in check list")

        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'between',
            'set': check_list,
            'inverse': inverse,
            'precision': precision
        })
        return self

    def like(self, field: DataType, template: str, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'like',
            'set': [template],
            'inverse': inverse
        })
        return self
    
    def less_than(self, field: DataType, value: object, inverse=False, precision=8):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'lt',
            'set': [value],
            'inverse': inverse,
            'precision': precision
        })
        return self
    
    def greater_than(self, field: DataType, value: object, inverse=False, precision=8):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'gt',
            'set': [value],
            'inverse': inverse,
            'precision': precision
        })
        return self

    def equals(self, field: DataType, value: object, inverse=False, precision=8):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'eq',
            'set': [value],
            'inverse': inverse,
            'precision': precision
        })
        return self
    
    def startsWith(self, field: DataType, value: str, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'startsWith',
            'set': [value],
            'inverse': inverse
        })
        return self
    
    def endsWith(self, field: DataType, value: str, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'endsWith',
            'set': [value],
            'inverse': inverse
        })
        return self

    def before(self, field: DataType, value: int, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'before',
            'set': [value],
            'inverse': inverse
        })
        return self

    def after(self, field: DataType, value: int, inverse=False):
        if 'predicates' not in self._temp_query:
            self._temp_query['predicates'] = list()
        
        self._temp_query['predicates'].append({
            'field': field.name,
            'operation': 'after',
            'set': [value],
            'inverse': inverse
        })
        return self

    def isnull(self, field: DataType, inverse=False):
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
        logger.info(self._temp_request)
        logger.debug(self._temp_query)

        logger.debug(self._post(self._temp_request, self._temp_query))

        self._reset_temp()

