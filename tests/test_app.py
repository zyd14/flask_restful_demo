import json

class TestCatEndpoints:

    def test_cat_get_initial(self, client):

        response = client.get('/cat')
        assert response.status_code == 200
        body = response.get_json()
        assert body['says'] == 'meow'

    def test_cat_post(self, client):

        response = client.post('/cat', data=json.dumps({'says': 'hello there'}), content_type='application/json')
        assert response.status_code == 200
        assert response.get_json()['says'] == 'hello there'

    def test_cat_get_after_post(self, client):

        response = client.post('/cat', data=json.dumps({'says': 'ginger'}), content_type='application/json')
        assert response.status_code == 200

        response = client.get('/cat')
        assert response.status_code == 200
        assert response.get_json()['says'] == 'ginger'

    def test_bad_request_missing_key(self, client):

        response = client.post('/cat', data=json.dumps({'something': 'else'}), content_type='application/json')
        assert response.status_code == 400
