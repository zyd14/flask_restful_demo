from flask import Flask
from flask_restx import Api, fields

from src.views import Cat, CatPics

# Create Flask app instance
app = Flask('A wonderful test App')

# Create restful API to which we will tie url endpoints and their views
api = Api(app)
ns = api.namespace('cat', description='Cat Things')
ns.add_resource(Cat, '/')
ns.add_resource(CatPics, '/pics')

cat_model = api.model('Model', {
    "says": fields.String(readonly=True)
})