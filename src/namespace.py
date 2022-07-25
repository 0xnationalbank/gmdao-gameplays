# namespaces

from src.instance.flask_app import api

home_page_api = api.namespace('altaars', path="/", description='gameplays related to altaars')
harvesters_api = api.namespace('harvesters-reservoirs', path="/", description='gameplays related to harvesters-reservoir')


