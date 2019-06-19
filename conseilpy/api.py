import requests
from requests.exceptions import Timeout
from loguru import logger
from typing import List
from enum import Enum
from cachetools import cached, TTLCache

from .exceptions import ConseilException


__all__ = ["ConseilApi"]


class ConseilApi:
    __url__ = "https://conseil-dev.cryptonomic-infra.tech"

    def __init__(self, api_key: str, api_version=None,  timeout=None):
        self._api_key = api_key
        self._api_version = api_version if api_version is not None else 2
        self._timeout = timeout if timeout is not None else 15       

    def get(self, command, **kwargs):
        request_data = {key: value for key, value in kwargs.items() if value is not None}
        url = f'{self.__url__}/v{self._api_version}/{command}'

        headers = {
            'apiKey': self._api_key
        }

        try:
            response = requests.get(url, params=request_data, headers=headers, timeout=self._timeout)
            if response.status_code != 200:
                raise ConseilException(f'Invalid response: {response.text} ({response.status_code})')
            return response.json()
        except Exception as e:
            raise ConseilException(e)
    
    def post(self, command, data):
        url = f'{self.__url__}/v{self._api_version}/{command}'

        headers = {
            'apiKey': self._api_key
        }

        try:
            response = requests.post(url, json=data, headers=headers, timeout=self._timeout)
            if response.status_code != 200:
                raise ConseilException(f'Invalid response: {response.text} ({response.status_code})')
            return response.json()
        except Exception as e:
            raise ConseilException(e)