from flask import Flask
from flask_restful import Api

from src.views import Cat, CatPics

# Create Flask app instance
app = Flask('A wonderful test App')

# Create restful API to which we will tie url endpoints and their views
api = Api(app)
api.add_resource(Cat, '/cat')
api.add_resource(CatPics, '/cat/pics')

