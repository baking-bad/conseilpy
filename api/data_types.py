class DataType:
    __type__ = ""

    def __init__(self, name: str, entity: str, unique=False, **kwargs):
        self.name = name
        self.unique = unique
        self.entity = entity
        for k, v in kwargs.items():
            self.__setattr__(k, v)


class AccountAddress(DataType):
    __type__ = "AccountAddress"

    def __init__(self, name: str, entity: str, unique=False, **kwargs):
        super(AccountAddress, self).__init__(name, entity, unique, **kwargs)


class String(DataType):
    __type__ = "String"

    def __init__(self, name: str, entity: str, unique=False, **kwargs):
        super(String, self).__init__(name, entity, unique, **kwargs)
