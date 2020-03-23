from flask import make_response, jsonify, request, Response, send_from_directory, render_template, url_for
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

class CatPics(Resource):

    def get(self):
        #return send_from_directory('templates', 'home.html')
        return send_from_directory('static', 'kitty.png')

class GCCount(Resource):

    def post(self):

        try:
            seq = request.get_json()['sequence']
        except KeyError:
            error_msg = 'User did not provide "sequence" keyword in JSON body'
            response = make_response(jsonify(error_msg=error_msg, code=400), 400)


class HomePage(Resource):

    name = 'asdf'

    def get(self):
        return send_from_directory('templates', 'home.html')

    def post(self):

        try:
            HomePage.user = request.get_json()['name']
            response = make_response(jsonify(says=HomePage.name, code=200), 200)
        except KeyError:
            error_msg = 'User did not provide "name" keyword in JSON body'
            response = make_response(jsonify(error_msg=error_msg, code=400), 400)

        response.headers['Content-Type'] = 'application/json'
        response.headers['Access-Control-Allow-Origin'] = '*'

        return render_template('home.html', name=HomePage.name)
