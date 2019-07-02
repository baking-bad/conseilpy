import requests


class ConseilException(Exception):
    pass


class ConseilApi:

    def __init__(self,
                 api_key='bakingbad',
                 api_host='https://conseil-dev.cryptonomic-infra.tech',
                 api_version=2,
                 timeout=15):
        self._api_key = api_key
        self._api_host = api_host
        self._api_version = api_version
        self._timeout = timeout

    def _request(self, method, path, params=None, json=None):
        if isinstance(params, dict):
            params = {k: v for k, v in params.items() if v is not None}

        response = requests.request(
            method=method,
            url=f'{self._api_host}/v{self._api_version}/{path}',
            params=params,
            headers={'apiKey': self._api_key},
            timeout=self._timeout,
            json=json
        )
        if response.status_code != 200:
            raise ConseilException(f'[{response.status_code}]: {response.text}')

        return response

    def get(self, path, **kwargs):
        return self._request(
            method='GET',
            path=path,
            params=kwargs
        )

    def post(self, path, json):
        return self._request(
            method='POST',
            path=path,
            json=json
        )
