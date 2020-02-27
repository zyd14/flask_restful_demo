from flask import make_response, jsonify, request, Response
from flask_restful import Resource


class Cat(Resource):

    says = 'meow'

    def get(self) -> Response:
        response = make_response(jsonify(says=Cat.says, code=200), 200)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response

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

