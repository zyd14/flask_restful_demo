from flask import make_response, jsonify, request, Response, send_from_directory
from flask_restx import Resource, fields
from src.setupapp import api

cat_model = api.model('Model', {
    "says": fields.String(readonly=True)
})


class Cat(Resource):

    says = 'meow'

    def get(self) -> Response:
        response = make_response(jsonify(says=Cat.says, code=200), 200)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

    @api.expect(cat_model)
    def post(self) -> Response:

        try:
            Cat.says = request.get_json()['says']
            response = make_response(jsonify(says=Cat.says, code=200), 200)
        except KeyError:
            error_msg = 'User did not provide "says" keyword in JSON body'
            response = make_response(jsonify(error_msg=error_msg, code=400), 400)

        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'

        return response


class CatPics(Resource):

    def get(self):
        return send_from_directory('static', 'kitty.png')

