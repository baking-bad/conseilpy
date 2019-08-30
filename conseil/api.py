import requests


class ConseilException(Exception):
    pass


class ConseilApi:

    def __init__(self, api_key, api_host, api_version, timeout=15):
        self._api_key = api_key
        self.host = api_host
        self.version = api_version
        self.timeout = timeout

    def __repr__(self):
        res = [
            super(ConseilApi, self).__repr__(),
            '\nProvider',
            f'{self.host} (v{self.version})'
        ]
        return '\n'.join(res)

    def _request(self, method, path, json=None):
        response = requests.request(
            method=method,
            url=f'{self.host}/v{self.version}/{path}',
            headers={'apiKey': self._api_key},
            json=json,
            timeout=self.timeout
        )
        if response.status_code != 200:
            raise ConseilException(f'[{response.status_code}]: {response.text}')

        return response

    def get(self, path):
        return self._request(method='GET', path=path)

    def post(self, path, json):
        return self._request(method='POST', path=path, json=json)
