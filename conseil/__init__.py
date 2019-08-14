from conseil.api import ConseilApi
from conseil.core import Client

conseil_dev = Client(ConseilApi(
    api_key='bakingbad',
    api_host='https://conseil-dev.cryptonomic-infra.tech',
    api_version=2
))
conseil_prod = Client(ConseilApi(
    api_key='bakingbad',
    api_host='https://conseil-prod.cryptonomic-infra.tech',
    api_version=2
))
conseil = conseil_dev
