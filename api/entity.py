from .data_types import AccountAddress, String


class Entity:
    __entity_name__ = "default"


class Account(Entity):
    __entity_name__ = "accounts"

    account_id = AccountAddress(
        name="account_id", 
        unique=True, 
        entity="accounts",
        dysplayName="Address", 
        description="Sometimes referred to as 'public key hash', the address is a unique account identifier",
        placeholder="tz1...")

    script = String(
        name="script",
        dysplayName="Script", 
        unique=False,
        entity="accounts")