from flask.testing import FlaskClient
import pytest

@pytest.fixture(scope='function')
def client() -> FlaskClient:
    from src.setupapp import app
    app.config['TESTING'] = True
    yield app.test_client()
