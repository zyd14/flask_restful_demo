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

### Running in Docker
A basic `Dockerfie` has been provided in the root directory which will install the source application into the root of 
the container, then run the application via the `main.py` entrypoint when the docker container is run.  To build the 
image run the following in a terminal window from the root of the project:

```docker build -t flask_demo .```

Once the container is built you can run it using the `docker run` command, and mapping your host port to the container's
default flask port (5000). To do this you would run the following in the root of your project:
```docker run -d -p 5000:5000 flask_demo```
This will run an instance of the latest version of the flask_demo container in your local registry, which you should now
 be able to access at `http://0.0.0.0:5000/cat`.
 
Once your applications are containerized, it becomes relatively straightforward to scale resources horizontally by adding
more instances in services like AWS Elastic Container Service, docker-compose, or pick-your-favorite Kubernetes provider. 
But that goes beyond the scope of this post.

### Deploying to AWS Lambda wth Zappa
[Zappa](https://github.com/Miserlou/Zappa) is an open-source python framework for building and deploying Lambda functions, with or without API Gateways attached
 to the. It has particularly good integration with Django and Flask applications, making it easy to turn existing web 
 applications into serverless applications.  
 By providing a `zappa_settings.json` file in the root of the project, one can configure a pretty wide variety of deployment
 options, including auto load balancers, event handlers (very handy), exception handlers, and callback functions.  Here
 we'll just set up a basic deployment of a `'dev'` stage which will create an API Gateway pointing to a Lambda function 
 created from the source application code.
 
 Note: As any call to the `flask_restful_demo` url could spawn a new lambda instance, the POST method of the `/cat` method
 may not always work as expected.  To properly store state an external data store is needed (DynamoDB, RDS, S3).

### Serving static HTML content
While I've mostly build REST APIs with Flask as a data sourcing layer between a database and a frontend client you can most
certainly serve up any type of content you want, including rendered HTML templates.  It's possible to build entire websites 
out of lambda functions with API Gateways and Application Load Balancers, although it can get a bt tricky if the site is 
particularly dynamic or highly concurrent.

### Lambda Deployments: Persisting state in a database
When persisting state in a flask application you have a few options. You can store items on the app itself, which will
be global for the lifespan of that application instance.  The `request` object will also be globally present and will 
contain all the information provided to the endpoint.  
When someone wants to update what a cat says, we should make sure that all instances of our application are aware of this
configuration change and will use the updated value.  The first three things that come to mind are:
1. json in S3 - kinda slow, but straightforward to use. No concurrent transaction control.
2. DynamoDb - interface is kinda cumbersome, but pretty easy to get off the ground
3. RDS - decent amount of work to get going, higher administrative overhead

### Swagger documentation
By putting a little more time up front documenting your Resource classes the `flask-restx` library can help generate great
Swagger documents viewable in a web browser. <Example Here>

### Request validation strategies