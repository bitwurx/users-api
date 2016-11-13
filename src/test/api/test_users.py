import arango
import json
import os

import tornado.gen
import tornado.httpclient
import tornado.ioloop

from users.models import connect_arango


connect_arango()
users = client = arango.ArangoClient(
    protocol='http',
    host='arangodb',
    port=8529,
    username='root',
    password=os.environ['ARANGO_ROOT_PASSWORD'],
    enable_logging=True
).db('alicia').collection('users')


def test_users_POST_creates_user():
    @tornado.gen.coroutine
    def create_user():
        body = {'username': 'joe',
                'password': 'test',
                'email': 'joe@schmoe.com'}
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/users',
            body=json.dumps(body)
        )
        response = yield client.fetch(request)
        data = json.loads(response.body.decode())

        assert data['code'] == 200
        assert data['status'] == 'success'
        assert data['data']['id']
        assert data['data']['username'] == 'joe'
        assert data['data']['email'] == 'joe@schmoe.com'
        assert data['data'].get('password') is None

    users.truncate()
    tornado.ioloop.IOLoop.current().run_sync(create_user)


def test_users_POST_returns_bad_request_with_invalid_json():
    @tornado.gen.coroutine
    def create_user():
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/users',
            body='[{'
        )

        try:
            yield client.fetch(request)
        except Exception as e:
            data = json.loads(e.response.body.decode())

        assert data['code'] == 400
        assert data['status'] == 'error'
        assert data['data'] == 'JSONDecodeError'
        assert data['message'] == 'Expecting property name enclosed in double'\
                                  ' quotes: line 1 column 3 (char 2)'

    users.truncate()
    tornado.ioloop.IOLoop.current().run_sync(create_user)


def test_users_POST_returns_conflict_error_if_users_exists():
    @tornado.gen.coroutine
    def create_user():
        body = {'username': 'joe',
                'password': 'test',
                'email': 'joe@schmoe.com'}
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/users',
            body=json.dumps(body)
        )
        try:
            yield client.fetch(request)
            yield client.fetch(request)
        except Exception as e:
            data = json.loads(e.response.body.decode())

        assert data['code'] == 409
        assert data['status'] == 'error'
        assert data['data'] == 'ConflictError'
        assert data['message'] == 'username field(s) must be unique'

    users.truncate()
    tornado.ioloop.IOLoop.current().run_sync(create_user)


def test_users_POST_returns_bad_request_with_invalid_parameters():
    @tornado.gen.coroutine
    def create_user():
        body = {'username': 'joe',
                'email': 'joe@schmoe.com'}
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/users',
            body=json.dumps(body)
        )
        try:
            yield client.fetch(request)
        except Exception as e:
            data = json.loads(e.response.body.decode())

        assert data['code'] == 400
        assert data['status'] == 'error'
        assert data['data'] == 'ValidationError'
        assert data['message'] == {'password': ['null value not allowed']}

    users.truncate()
    tornado.ioloop.IOLoop.current().run_sync(create_user)
