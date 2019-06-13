from cachetools import cached, TTLCache

from .api import ConseilApi
from .utils import prepare_name

__all__ = ["Attribute", "Entity"]


class Attribute:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__setattr__(k, v)
        self.__doc__ = self._build_doc()

    def _build_doc(self):
        s = ''
        if hasattr(self, 'description'):
            s += f'{self.description}\r\n'
        if hasattr(self, 'name'):
            s += f'Attribute name: {self.name}\r\n'
        if hasattr(self, 'dataType'):
            s += f'Data type: {self.dataType}\r\n'
        if hasattr(self, 'cardinality'):
            s += f'Cardinality: {self.cardinality}\r\n'
        if hasattr(self, 'keyType'):
            s += f'Key type: {self.keyType}\r\n'
        if hasattr(self, 'placeholder'):
            s += f'Placeholder: {self.placeholder}\r\n'
        if hasattr(self, 'scale'):
            s += f'Scale: {self.scale}\r\n'
        if hasattr(self, 'valueMap'):
            s += 'Values:\r\n'
            for k, v in self.valueMap.items():
                s += f'\t{k}: {v}\r\n'        
        if hasattr(self, 'dataFormat'):
            s += f'Date format: {self.dataFormat}\r\n'
        return s

    def __str__(self):
        return self.__doc__
    
    __repr__ = __str__

class Entity:
    def __init__(self, api: ConseilApi, platform_name: str, network: str, **kwargs):
        self.platform = platform_name
        self.network = network

        for k, v in kwargs.items():
            self.__setattr__(k, v)

        for x in api.get(f'metadata/{self.platform}/{self.network}/{self.name}/attributes'):
            self.__setattr__(prepare_name(x['displayName']), Attribute(**x))
        
        self.__doc__ = self._build_doc()

    def _build_doc(self):
        s = self.displayName
        if hasattr(self, 'count'):
            s += f' count: {self.count}\r\n'
        return s
    
    def __repr__(self):
        return self.__doc__
    
    def __str__(self):
        return self.displayName
