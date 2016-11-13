import arango
import json
import os

import redis

import tornado.gen
import tornado.httpclient
import tornado.ioloop

from users.models import connect_arango


connect_arango()
redis_client = redis.Redis('redis', 6379)
users = client = arango.ArangoClient(
    protocol='http',
    host='arangodb',
    port=8529,
    username='root',
    password=os.environ['ARANGO_ROOT_PASSWORD'],
    enable_logging=True
).db('alicia').collection('users')


def test_sessions_GET_returns_session_details():
    @tornado.gen.coroutine
    def get_session():
        body = {'username': 'joe',
                'password': 'test',
                'email': 'joe@schmoe.com'}
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/users',
            body=json.dumps(body)
        )
        yield client.fetch(request)
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/sessions',
            body=json.dumps({'username': 'joe', 'password': 'test'})
        )
        response = yield client.fetch(request)
        session = json.loads(response.body.decode())
        request = tornado.httpclient.HTTPRequest(
            method='GET',
            url='http://localhost/sessions/%s' % session['data']['token'],
        )
        response = yield client.fetch(request)
        data = json.loads(response.body.decode())
        assert data['code'] == 200
        assert data['status'] == 'success'
        assert data['data']['username'] == 'joe'
        assert data['data']['email'] == 'joe@schmoe.com'

    users.truncate()
    redis_client.flushall()
    tornado.ioloop.IOLoop.current().run_sync(get_session)


def test_sessions_GET_returns_not_found_error():
    @tornado.gen.coroutine
    def get_session():
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='GET',
            url='http://localhost/sessions/abc123',
        )

        try:
            yield client.fetch(request)
        except Exception as e:
            data = json.loads(e.response.body.decode())

        assert data['code'] == 404
        assert data['status'] == 'error'
        assert data['data'] == 'NotFoundError'
        assert data['message'] == 'session token not found'

    users.truncate()
    redis_client.flushall()
    tornado.ioloop.IOLoop.current().run_sync(get_session)


def test_sessions_POST_creates_user_session():
    @tornado.gen.coroutine
    def create_session():
        body = {'username': 'joe',
                'password': 'test',
                'email': 'joe@schmoe.com'}
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/users',
            body=json.dumps(body)
        )
        yield client.fetch(request)
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/sessions',
            body=json.dumps({'username': 'joe', 'password': 'test'})
        )
        response = yield client.fetch(request)
        data = json.loads(response.body.decode())

        assert data['code'] == 200
        assert data['status'] == 'success'
        assert data['data']['token']

    users.truncate()
    redis_client.flushall()
    tornado.ioloop.IOLoop.current().run_sync(create_session)


def test_sessions_POST_returns_bad_request_with_invalid_json():
    @tornado.gen.coroutine
    def create_session():
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/sessions',
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

    redis_client.flushall()
    tornado.ioloop.IOLoop.current().run_sync(create_session)


def test_sessions_POST_returns_bad_request_with_invalid_parameters():
    @tornado.gen.coroutine
    def create_session():
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/sessions',
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

    redis_client.flushall()
    tornado.ioloop.IOLoop.current().run_sync(create_session)


def test_sessions_POST_returns_bad_request_with_bad_password():
    @tornado.gen.coroutine
    def create_session():
        body = {'username': 'joe',
                'password': 'test',
                'email': 'joe@schmoe.com'}
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/users',
            body=json.dumps(body)
        )
        yield client.fetch(request)
        body['password'] = 'password1!'
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/sessions',
            body=json.dumps(body)
        )

        try:
            yield client.fetch(request)
        except Exception as e:
            data = json.loads(e.response.body.decode())

        assert data['code'] == 400
        assert data['status'] == 'error'
        assert data['data'] == 'InvalidCredentialsError'
        assert data['message'] == 'incorrect username or password'

    users.truncate()
    redis_client.flushall()
    tornado.ioloop.IOLoop.current().run_sync(create_session)


def test_sessions_PUT_returns_extends_session():
    @tornado.gen.coroutine
    def update_session():
        body = {'username': 'joe',
                'password': 'test',
                'email': 'joe@schmoe.com'}
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/users',
            body=json.dumps(body)
        )
        yield client.fetch(request)
        request = tornado.httpclient.HTTPRequest(
            method='POST',
            url='http://localhost/sessions',
            body=json.dumps({'username': 'joe', 'password': 'test'})
        )
        response = yield client.fetch(request)
        session = json.loads(response.body.decode())
        request = tornado.httpclient.HTTPRequest(
            method='PUT',
            url='http://localhost/sessions/%s' % session['data']['token'],
            body=''
        )
        response = yield client.fetch(request)
        data = json.loads(response.body.decode())
        assert data['code'] == 200
        assert data['status'] == 'success'
        assert data['data']['token'] == session['data']['token']

    users.truncate()
    redis_client.flushall()
    tornado.ioloop.IOLoop.current().run_sync(update_session)


def test_sessions_PUT_returns_not_found_error_if_session_not_found():
    @tornado.gen.coroutine
    def update_session():
        client = tornado.httpclient.AsyncHTTPClient()
        request = tornado.httpclient.HTTPRequest(
            method='PUT',
            url='http://localhost/sessions/a1b2c3',
            body=''
        )

        try:
            yield client.fetch(request)
        except Exception as e:
            data = json.loads(e.response.body.decode())

        assert data['code'] == 404
        assert data['status'] == 'error'
        assert data['data'] == 'NotFoundError'
        assert data['message'] == 'session token not found'

    users.truncate()
    redis_client.flushall()
    tornado.ioloop.IOLoop.current().run_sync(update_session)
