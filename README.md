# Intro to Flask for building RESTful APIs

## What is Flask?

Flask is a web 'microframework'.  At its core it's provides a fairly basic server instance capable of responding to url
routes with http responses. Flask was built to be extendable, so that you would only add the web utilities you need for
your service.  Popular flask extensions include `Flask-OAuth`,`Flask-Login`, `Flask-SQLAlchemy`, `'flask-RESTful`, plus 
many more.  This post will focus on using `'flask-RESTful` for building RESTful APIs, and will make use of the `zappa`
framework to deploy the API to AWS where it is hosted as a serverless lambda function with an API Gateway attached to 
provide a host url.

### Getting started

To get a server up a running, one just needs to instantiate a Flask object, then use the `.run()` method on that object.

```python
from flask import Flask

app = Flask('ShowApp')
app.run()
```

This will start a process on localhost port 5000 by default (http://127.0.0.1:5000/), but the host and port can be overriden
using keyword parameters.  A debug mode is also possible using the debug flag, which can show much more detail about how
problem requests are being handled on the server.  

Now this server doesn't do anything yet, because we haven't tied any resources to it yet.  To begin adding endpoints to
our REST API we first need to use the flask-RESTful extension to create an `Api` object.

```python
from flask import Flask
from flask_restful import Api

app = Flask('ShowApp')
api = Api(app)
```

I usually declare my app and api variables at a global level, ideally as singletons, early on in the program and 
reference them as needed from other modules.  

Now we can start creating rest `Resource` objects that we can tie to different URL endpoints in our application. First,
let's create a resource. 

```python
from flask import make_response, jsonify, request
from flask_restful import Resource


class Cat(Resource):

    says = 'meow'

    def get(self):
        return make_response(jsonify(says=Cat.says, code=200))

    def post(self):

        Cat.says = request.get_json()['says']
        return make_response(jsonify(says=Cat.says, code=200))
```

We've just created a resource with both GET and POST request handlers.  The GET handler will create a response of 
`{'says': 'meow', 'code': 200}`.  The POST handler will take a parse a parameter `says` from the body of the POST request
and set the Resource `says` class variable to the request-provided parameter.  This way subsequent calls to the GET handler
should now return the new value set by the POST endpoint (this only holds true for this particular application server instance).

Without being tied to the application, our `Cat` Resource doesn't have any way of interacting with the outside world.  To 
tie it to our application we can do the following in our `app.py`:

```python
from flask import Flask
from flask_restful import Api

from src.views import Cat

# Create Flask app instance
app = Flask('A wonderful test App')

# Create restful API to which we will tie url endpoints and their views
api = Api(app)
api.add_resource(Cat, '/cat')
```  
This just tied our `Cat` Resource to the /cat endpoint of the application server.  For instance, when running locally and
with defaults, this endpoint will be available at http://127.0.0.1:5000/cat.  If deployed via a lambda function, a docker 
image, or another hosting option your host name and port will need to change.