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
def test_UsersResourceV1_post_creates_user_document(MockUser):
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


def test_UsersResourceV1_post_sends_decode_error_on_exception():
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
def test_UsersResourceV1_post_sends_conflict_error_on_exception(MockUser):
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
def test_UsersResourceV1_post_sends_validation_error_on_exception(MockUser):
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
def test_SessionsResourceV1_get_gets_user_session_details(MockSession):
    def mock_read(*args, **kwargs):
        if token == 'abc123':
            return {'username': 'jane', 'email': 'jane@doe.com'}

    token = 'abc123'
    MockSession().read.side_effect = mock_read
    resource = SessionsResourceV1(mock.MagicMock(), mock.Mock())
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.get(token)
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(200)
    assert response['code'] == 200
    assert response['status'] == 'success'
    assert response['data'] == {'username': 'jane', 'email': 'jane@doe.com'}


@mock.patch('users.api.Session')
def test_SessionsResourceV1_get_returns_404_if_session_not_exists(MockSession):
    def mock_read(*args, **kwargs):
        raise NotFoundError('session token')

    MockSession().read.side_effect = mock_read
    resource = SessionsResourceV1(mock.MagicMock(), mock.Mock())
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.get('xyz890')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(404)
    assert response['code'] == 404
    assert response['status'] == 'error'
    assert response['data'] == 'NotFoundError'
    assert response['message'] == 'session token not found'


@mock.patch('users.api.Session')
def test_SessionsResourceV1_post_creates_user_session(MockSession):
    MockSession().create.return_value = {'token': '1a2b3c'}
    request = mock.Mock()
    request.body = b'{"username": "test", "password": "password1"}'
    resource = SessionsResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post('')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(200)
    assert response['code'] == 200
    assert response['status'] == 'success'
    assert response['data'] == {'token': '1a2b3c'}


@mock.patch('users.api.Session')
def test_SessionsResourceV1_post_sends_decode_error(MockSession):
    request = mock.Mock()
    request.body = b'[{'
    resource = SessionsResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post('')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(400)
    assert response['code'] == 400
    assert response['status'] == 'error'
    assert response['data'] == 'JSONDecodeError'
    assert response['message'] == \
        'Expecting property name enclosed in double quotes: line 1 column 3' \
        ' (char 2)'


@mock.patch('users.api.Session')
def test_SessionsResourceV1_post_sends_validation_error_on_exception(
        MockSession):
    def mock_create(*args, **kwargs):
        raise BadRequestError(json.dumps(errors), 'ValidationError')

    MockSession().create.side_effect = mock_create
    errors = {'password': ['null value not allowed']}
    request = mock.Mock()
    request.body = b'{}'
    resource = SessionsResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post('')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(400)
    assert response['code'] == 400
    assert response['status'] == 'error'
    assert response['data'] == 'ValidationError'
    assert response['message'] == json.dumps(errors)


@mock.patch('users.api.Session')
def test_SessionsResourceV1_post_sends_credential_error_with_bad_password(
        MockSession):
    def mock_create(*args, **kwargs):
        raise BadRequestError('incorrect username or password',
                              'InvalidCredentialsError')

    MockSession().create.side_effect = mock_create
    request = mock.Mock()
    request.body = b'{}'
    resource = SessionsResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post('')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(400)
    assert response['code'] == 400
    assert response['status'] == 'error'
    assert response['data'] == 'InvalidCredentialsError'
    assert response['message'] == 'incorrect username or password'


@mock.patch('users.api.Session')
def test_SessionsResourceV1_post_raises_exception_if_token_is_in_url(
        MockSession):
    request = mock.Mock()
    request.body = b'{}'
    resource = SessionsResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.post('abc')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(404)
    assert response['code'] == 404
    assert response['status'] == 'error'
    assert response['data'] == 'NotFoundError'
    assert response['message'] == 'resource not found'


@mock.patch('users.api.Session')
def test_SessionsResourceV1_put_updates_session_token(MockSession):
    MockSession().update.return_value = {'token': 'abc123'}
    resource = SessionsResourceV1(mock.MagicMock(), mock.Mock())
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.put('abc123')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(200)
    assert response['code'] == 200
    assert response['status'] == 'success'
    assert response['data'] == {'token': 'abc123'}


@mock.patch('users.api.Session')
def test_SessionsResourceV1_put_raises_exception_if_token_not_exists(
        MockSession):
    def mock_update(*args, **kwargs):
        raise NotFoundError('session token')

    MockSession().update.side_effect = mock_update
    resource = SessionsResourceV1(mock.MagicMock(), mock.Mock())
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.put('abc123')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(404)
    assert response['code'] == 404
    assert response['status'] == 'error'
    assert response['data'] == 'NotFoundError'
    assert response['message'] == 'session token not found'


@mock.patch('users.api.Session')
def test_SessionsResourceV1_delete_removes_session_token(MockSession):
    MockSession().delete.return_value = {}
    resource = SessionsResourceV1(mock.MagicMock(), mock.Mock())
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.delete('abc123')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(200)
    assert response['code'] == 200
    assert response['status'] == 'success'
    assert response['data'] == {}


@mock.patch('users.api.Session')
def test_SessionsResourceV1_delete_raises_exception_if_token_not_exists(
        MockSession):
    def mock_delete(*args, **kwargs):
        raise NotFoundError('session token')

    MockSession().delete.side_effect = mock_delete
    resource = SessionsResourceV1(mock.MagicMock(), mock.Mock())
    resource.write = mock.Mock()
    resource.set_status = mock.Mock()
    resource.delete('abc123')
    response = resource.write.mock_calls[0][1][0]
    resource.set_status.assert_called_with(404)
    assert response['code'] == 404
    assert response['status'] == 'error'
    assert response['data'] == 'NotFoundError'
    assert response['message'] == 'session token not found'
