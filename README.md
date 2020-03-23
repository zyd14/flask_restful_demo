# Intro to Flask for building RESTful APIs

## What is Flask?

Flask is a web 'microframework'.  At its core it's provides a fairly basic server instance capable of responding to url
routes with HTTP responses. Flask was built to be extendable, so that you would only add the web utilities you need for
your service.  Popular flask extensions include `Flask-OAuth`,`Flask-Login`, `Flask-SQLAlchemy`, `'flask-RESTful`, and 
many more.  This post will focus on using `'flask-RESTful` for building RESTful APIs, and will show how to make use of 
the `zappa` framework to deploy the API to AWS where it is hosted as a serverless lambda function with an API Gateway 
attached to provide a host url.    

It is important to note that while `Flask-RESTful` can serve basic static webpages, was not built to serve dynamic content and
it better suited to serving as a framework API for frontend applications to communicate with.  It is common practice to 
connect an nginx or other frontend in your desired language for dynamic rendering of HTML templates using data pulled from 
a Flask-RESTful backend. Flask-RESTful is best suited to providing a gateway to backend resources like databases and compute applications so your 
frontend can remain isolated from the backend implementation details and focus on presentation. This has the added benefit
of allowing you to evolve your frontend separately and even choose a different language to develop it in (JavaScript for example).
It also also for the possibility of having multiple clients, such as different frontends or remote API users to use the same
interface for accessing a set of resources (such as a database). Lastly, Flask-RESTful can be very easily designed in a 
stateless manner, making it easy to deploy in redundancy or as a serverless application if you are working in cloud, lowering
your cost of infrastructure management. 

####Follow along:
The source code for all the examples below can be found and downloaded here: 

### Getting started

To get a server up a running, one just needs to instantiate a Flask object, then use the `.run()` method on that object.

```python
from flask import Flask

app = Flask('ShowApp')
app.run()
```

This will start a process on localhost port 5000 by default (http://127.0.0.1:5000/), but the host and port can be overriden
using keyword parameters.  A debug mode is also possible using the debug flag which will print much more detailed information
regarding calls which cause unexpected crashes within the web app.  

Now this server doesn't do anything yet, because we haven't tied any resources to it yet.  To begin adding endpoints to
our REST API we first need to use the flask-RESTful extension to create an `Api` object.

```python
from flask import Flask
from flask_restful import Api

app = Flask('ShowApp')
api = Api(app)
```

I usually declare my app and api variables at a global level early on in the program and reference them as needed from 
other modules.  

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

(Note: `jsonify` is a Flask-imported method which creates JSON-formatted string objects from a set of keyword arguments, handling any necessary esacaping.
       `make_response` is a Flask-imported method which takes a JSON-formatted string and creates a `Response` object with the necessary 
       headers and other attributes needed to be passed over the internet back to the client.)   

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
This just mapped our `Cat` Resource to the /cat endpoint of the application server.  For instance, when running locally and
with defaults, this endpoint will be available at http://127.0.0.1:5000/cat.  If deployed via a API Gateway / Lambda function, a docker 
image, or another hosting option your host name and port will need to change.

### Running locally
To run an application the user must create instances of Flask App and Api, and then execute the `Api.app.run()` method. 
In this project the `main.py` file provides a simple entry point to start the application locally via `python main.py`. 
This entry point is executed by importing our `api` object created in `/src/app.py`, and executing its `api.app.run()` method.
This essentially launches an instance of your application which runs on a loop, listening to input from port 5000 of your 
localhost address (usually 127.0.0.1).  The address and port to which your application will publish is customizable within
the `api.app.run()` call.

Once you're running locally, you should be able to hit your endpoints using a web browser, `curl` or any other http 
method using the base URL. 

### Testing
Requests against your rest endpoints can be easily simulated using Flask's application test client. 
To create a test client, you can import your Flask `app` object created earlier in the tutorial from your test file, then use
the `app.test_client()` method to return a mocked flask application with all the same endpoints and functionality (demonstrated
in the companion repo file `tests/conftest.py`). Once you have a test client, you can use its `.post()`, `.get()`, `.put()` etc.
methods within your tests to throw requests of the given type at your endpoint resources.  

If you are using `pytest`, a common pattern is to create a test client fixture
 which you can then import into any functions testing against your endpoints.  
 
 Example:
(tests/conftest.py)
```python
from flask.testing import FlaskClient
import pytest
@pytest.fixture(scope='function')
def client() -> FlaskClient:
    from src.app import app
    app.config['TESTING'] = True
    yield app.test_client()

```

(tests/test_app.py)
```python
from flask.testing import FlaskClient
def test_cat_get_initial(client: FlaskClient):

    response = client.get('/cat')
    assert response.status_code == 200
    body = response.get_json()
    assert body['says'] == 'meow'
```
(Can be found in the accompanying repo, `tests/test_app.py`).  Here we have a test which performs a `/get` request against a 
test client, defined in `tests/conftest.py`.  We are then able to check the status code of the response and that the body
 contains the information we expected.  This comes in super handy for end-to-end or request / response testing.

### Running in Docker
Basic Dockerfile:
```dockerfile
FROM python:3.8.2-slim

WORKDIR /

COPY src /src
COPY main.py .
COPY static /static
COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV DOCKER_EXE=True

ENTRYPOINT ["python", "main.py"]
```


This basic dockerfile will install the source application into the root of the container, then run the application via 
the `main.py` entrypoint when the docker container is run.  To build the image run the following in a terminal window from the root of the project:

```docker build -t flask_demo .```

Once the container is built you can run it using the `docker run` command, and mapping your host port to the container's
default flask port (5000). To do this you would run the following in the root of your project:
```docker run -d -p 5000:5000 flask_demo```
This will run an instance of the latest version of the flask_demo container in your local registry, which you should now
 be able to access at `http://0.0.0.0:5000/cat` and `http://0.0.0.0:5000/cat/pics`.
 
Once your applications are containerized, it becomes relatively straightforward to scale application resources horizontally 
by adding more instances in services like AWS Elastic Container Service, docker-compose, or pick-your-favorite Kubernetes 
provider. But that goes beyond the scope of this post.

**Note**: The WSGI server provided by the underlying `Werzkeug` library that Flask heavily leverages is not meant to host 
production traffic.  If you plan on hosting a website with Flask and expect any sort of traffic you will want to look into 
solutions like `gunicorn` and `nginx`, both of which can be easily integrated into your docker container. 

### Deploying to AWS Lambda wth Zappa
[Zappa](https://github.com/Miserlou/Zappa) is an open-source python framework for building and deploying Lambda functions, with or without API Gateways attached
 to the. It has particularly good integration with Django and Flask applications, making it easy to turn existing web 
 applications into serverless applications.  
 By providing a `zappa_settings.json` file in the root of the project, one can configure a pretty wide variety of deployment
 options, including auto load balancers, event handlers (very handy), exception handlers, and callback functions.  Here
 we'll just set up a basic deployment of a `'dev'` stage which will create an API Gateway pointing to a Lambda function 
 created from the source application code. There are some pretty nifty things you can do with some of the more interesting
 configurations in `zappa`, so if you get interested in using it definitely spend some time going through the docs.
 
 To deploy the lambda function for the first time, enter  
 `zappa deploy dev`  
 This will create the lambda handler and API Gateway, and will return the API Gateway URL in the output, which is now the
 base URL for calls to any endpoints in the flask application.
 
 If you want to update a previously deployed function, use the command  
 `zappa update dev`  
 
 Note: As any call to the `flask_restful_demo` url could spawn a new lambda instance, the POST method of the `/cat` method
 may not always work as expected.  To properly store state an external data store is needed (DynamoDB, RDS, S3).

### Serving static HTML content
While I've mostly build REST APIs with Flask as a data sourcing layer between a database and a frontend client you can most
certainly serve up any type of content you want, including rendered HTML templates. It's possible to build entire websites 
out of lambda functions with API Gateways and Application Load Balancers and backing S3 stores for static content, 
although it can get a bt tricky if the site is particularly dynamic.

### Persisting state
When persisting state in a flask application you have a few options. You can store items on the app itself, which will
be global for the lifespan of that application instance.  The `request` object will also be globally present and will 
contain all the information provided to the endpoint for the lifespan of the request. Flask-Session is a Flask extension 
library which allows for the persistence of state between multiple requests for the lifespan of a user session, by creating
a temporary file containing persistent data in the project directory.  
To persist beyond the lifespan of the application you have the usual mechanisms - write to disk, S3, database, etc.  I've 
found `flask_restful` to work great for providing an API for interacting with a database, isolating clients / other services
from needing to know the structure of the database.    

### Swagger documentation
By putting a little more time up front documenting your Resource classes the [flask-restx](https://github.com/python-restx/flask-restx) library can help generate great
Swagger documents viewable in a web browser. <Example Here>

### Request validation strategies  
I really like the [marshmallow](https://marshmallow.readthedocs.io/en/stable/) library for parsing incoming JSON from 
requests, although there are a number of good alternatives out there.  `flask_restful` has an in-box request parser called
`reqparse`, but I haven't had the best experiences parsing data with nested structures using it.

### Flask use cases
- Building lightweight serverless websites with `flask-RESTful`
- Provide a shared API for a datastore (relational / non-relational / filesystem-based)
- Provide shared serverless utility functionality, including highly parallelizable stateless analytics operations (with some restrictions on data size and timeout)
- Creating side-car controller containers in multi-container deployments (ECS, Batch, Kuberetes).
- Create hybrid applications with both RESTful endpoints as well as subscribed message / event handlers.

### Non-flask zappa use cases
Zappa provides a simple mechanism for creating Lambda functions which can be subscribed to AWS events, SNS & SQS messages,
and DynamoDB & Kinesis streams. These don't require any flask application - you write a regular Lambda handler, provide 
a path to it in your `zappa_settings.json` file as well as the event source and then the `zappa deploy/update` commands
will handle the creation of the function and any necessary CloudWatch Rules or subscriptions. This allows your function 
to execute asynchronously whenever it sees a message in a queue / topic / event source it is subscribed to. Functions can 
also be scheduled to run periodically like a cron job.
 
Event sourcing / subscription processing is a really interesting topic I will probably expand on quite a bit more in 
another post.

### Limitations  
When using `flask-RESTful` to build serverless applications on AWS there are some restrictions to keep in mind:
- Maximum RAM allowed on a Lambda instance is 3GB, and maximum execution length is 15 minutes. State is not necessarily kept between
calls to the lambda function so you have to store state in S3 or a database (fyi AWS doesn't charge for transferring data between 
S3 and other services). 
- When paired with Lambda calls via API Gateway will time-out after 30 seconds.  The function will keep running after 30
seconds, but the caller will get a TimeOut exception response, and will not receive anything from the function after that. 
To get around this you can deploy your Lambda behind an Automatic Load Balancer (configurable in `zappa_settings.json`), 
or perform asynchronous invocations of your lambda function (zappa provides a great `@task` wrapper for this, importable 
from `zappa.asynchronous`).
- Maximum payload that can be received via a call to Lambda is 6MB.  To pass larger datasets you can pass an S3 location 
and load the data from the Lambda instance (provided it can fit in the ~3GB of allotted memory). Maximum response size 
for API Gateway is 10MB, but the same technique can be used to pass around details of where larger datasets live.
- Highly bursty / concurrent loads on a Lambda function can take a bit longer to provision and responsiveness will degrade
relatively quickly in relation to a burst of concurrent executions without configuring Provisioned Concurrency for your 
function. 