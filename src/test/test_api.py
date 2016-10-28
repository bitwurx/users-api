import copy
import json

from unittest import mock

from users.api import make_response, parse_json_body
from users.api import (
    UsersResourceV1
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
    assert '"code": 200' in \
        str(resource.write.mock_calls[0])
    assert '"status": "success"' in \
        str(resource.write.mock_calls[0])
    assert '"username": "joe"' in \
        str(resource.write.mock_calls[0])
    assert '"password": "test"' in \
        str(resource.write.mock_calls[0])
    assert '"email": "joe@schmoe.com"' in \
        str(resource.write.mock_calls[0])


def test_UsersResource_post_sends_error_on_exception():
    request = mock.Mock()
    request.body = b'[}]'
    resource = UsersResourceV1(mock.MagicMock(), mock.Mock())
    resource.request = request
    resource.write = mock.Mock()
    resource.post()
    assert '"code": 400' in \
        str(resource.write.mock_calls[0])
    assert '"message": "Expecting value: line 1 column 2 (char 1)"' in \
        str(resource.write.mock_calls[0])
    assert '"data": "JSONDecodeError"' in \
        str(resource.write.mock_calls[0])
    assert '"status": "error"' in \
        str(resource.write.mock_calls[0])
