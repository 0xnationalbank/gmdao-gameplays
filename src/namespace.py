# namespaces

from src.instance.flask_app import api

home_page_api = api.namespace('home_page', path="/", description='operations related to home page')

