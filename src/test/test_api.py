import copy
import json

from unittest import mock

from users.api import make_response, parse_json_body
from users.api import (
    SessionsResourceV1,
    UsersResourceV1
)
from users.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError
)


def test_parse_json_body_returns_successfully_parsed_json_body():
    body = parse_json_body('{"name": "Joe"}')
    assert body['name'] == "Joe"


def test_parse_json_body_writes_malformed_request_body():
    error = None

    try:
        parse_json_body('[}')
    except Exception as e:
        error = e

    assert error.data == 'JSONDecodeError'
    assert error.message == 'Expecting value: line 1 column 2 (char 1)'


def test_make_response_creates_a_success_response_object():
    response = make_response(code=200, data={'message': 'Hello, World!'})
    assert response == {'code': 200,
                        'status': 'success',
                        'data': {'message': 'Hello, World!'}}


@mock.patch('users.api.User')
def test_UsersResource_post_creates_user_document(MockUser):
    data = {'username': 'joe', 'password': 'test', 'email': 'joe@schmoe.com'}
    user = copy.deepcopy(data)
    user['id'] = 28918
    del user['password']
    MockUser().create.return_value = user
    request = mock.Mock()
    request.body = json.dumps(data).encode()
    resource = UsersResourceV1(mock.MagicMock(), mock.Mock())
    resource.request = request
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post()
    MockUser.assert_called_with(**{'username': 'joe',
                                   'password': 'test',
                                   'email': 'joe@schmoe.com'})

    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(200)
    assert response['code'] == 200
    assert response['status'] == 'success'
    assert response['data'] == {
        'id': 28918,
        'username': 'joe',
        'email': 'joe@schmoe.com'
    }


def test_UsersResource_post_sends_decode_error_on_exception():
    request = mock.Mock()
    request.body = b'[}]'
    resource = UsersResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post()
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(400)
    assert response['code'] == 400
    assert response['status'] == 'error'
    assert response['message'] == 'Expecting value: line 1 column 2 (char 1)'
    assert response['data'] == 'JSONDecodeError'


@mock.patch('users.api.User')
def test_UsersResource_post_sends_conflict_error_on_exception(MockUser):
    def mock_create(*args, **kwargs):
        raise ConflictError(fields=('username',))
    MockUser().create.side_effect = mock_create
    request = mock.Mock()
    request.body = b'{}'
    resource = UsersResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post()
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(409)
    assert response['code'] == 409
    assert response['status'] == 'error'
    assert response['message'] == 'username field(s) must be unique'
    assert response['data'] == 'ConflictError'


@mock.patch('users.api.User')
def test_UsersResource_post_sends_valiation_error_on_exception(MockUser):
    def mock_create(*args, **kwargs):
        raise BadRequestError(json.dumps(errors), 'ValidationError')

    MockUser().create.side_effect = mock_create
    errors = {'email': ['null value not allowed']}
    request = mock.Mock()
    request.body = b'{"username": "joe", "password": "password1"}'
    resource = UsersResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post()
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(400)
    assert response['code'] == 400
    assert response['status'] == 'error'
    assert response['message'] == json.dumps(errors)
    assert response['data'] == 'ValidationError'


@mock.patch('users.api.Session')
def test_SessionsResource_get_gets_user_session_details(MockSession):
    def mock_read(token):
        if token == 'abc123':
            return {'username': 'jane', 'email': 'jane@doe.com'}

    MockSession().read.side_effect = mock_read
    resource = SessionsResourceV1(mock.MagicMock(), mock.Mock())
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.get('abc123')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(200)
    assert response['code'] == 200
    assert response['status'] == 'success'
    assert response['data'] == {'username': 'jane', 'email': 'jane@doe.com'}


@mock.patch('users.api.Session')
def test_SessionResource_get_returns_404_if_session_not_exists(MockSession):
    def mock_read(*args, **kwargs):
        raise NotFoundError('session token')

    MockSession().read.side_effect = mock_read
    resource = SessionsResourceV1(mock.MagicMock(), mock.Mock())
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.get('testing')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(404)
    assert response['code'] == 404
    assert response['status'] == 'error'
    assert response['data'] == 'NotFoundError'
    assert response['message'] == 'session token not found'
