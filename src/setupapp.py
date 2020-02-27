from flask import Flask
from flask_restx import Api, fields
from werkzeug.contrib.fixers import ProxyFix

# Create Flask app instance
app = None
api = None
if not app or not api:
    app = Flask('A wonderful test App')
    #app.wsgi_app = ProxyFix(app.wsgi_app)
    # Create restful API to which we will tie url endpoints and their views
    api = Api(app)


def tie_resources():
    from src.views import Cat, CatPics
    ns_cat = api.namespace('cat')
    ns_cat.add_resource(Cat, '')
    ns_cat.add_resource(CatPics, '/pics')

tie_resources()