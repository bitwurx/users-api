import copy
import json

from unittest import mock

from users.api import make_response, parse_json_body
from users.api import (
    UsersResourceV1
)
from users.exceptions import BadRequestError, ConflictError


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
    MockUser().create.return_value = user
    request = mock.Mock()
    request.body = json.dumps(data).encode()
    resource = UsersResourceV1(mock.MagicMock(), mock.Mock())
    resource.request = request
    resource.write = mock.Mock()
    resource.post()
    MockUser.assert_called_with(**{'username': 'joe',
                                   'password': 'test',
                                   'email': 'joe@schmoe.com'})

    response = json.loads(resource.write.mock_calls[0][1][0])
    assert response['code'] == 200
    assert response['status'] == 'success'
    assert response['data'] == {
        'id': 28918,
        'username': 'joe',
        'password': 'test',
        'email': 'joe@schmoe.com'
    }


def test_UsersResource_post_sends_decode_error_on_exception():
    request = mock.Mock()
    request.body = b'[}]'
    resource = UsersResourceV1(mock.MagicMock(), request)
    resource.write = mock.Mock()
    resource.post()
    response = json.loads(resource.write.mock_calls[0][1][0])
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
    resource.post()
    response = json.loads(resource.write.mock_calls[0][1][0])
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
    resource.post()
    response = json.loads(resource.write.mock_calls[0][1][0])
    assert response['code'] == 400
    assert response['status'] == 'error'
    assert response['message'] == json.dumps(errors)
    assert response['data'] == 'ValidationError'
