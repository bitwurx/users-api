from users.exceptions import (
    BaseError,
    BadRequestError,
    ConflictError,
    NotFoundError
)


def test_BaseError_response_returns_rest_compliant_response_body():
    try:
        raise BaseError()
    except BaseError as e:
        e.code = 404
        e.message = 'something went wrong'
        e.data = 'ResourceNotFound'
        response = e.response()

    assert response == {'code': 404,
                        'status': 'error',
                        'message': 'something went wrong',
                        'data': 'ResourceNotFound'}


def test_BadRequestError_error_code():
    assert BadRequestError.code == 400


def test_BadRequestError_error_message_and_data():
    try:
        raise BadRequestError(message='test error', data='TestError')
    except BadRequestError as e:
        data = e.data
        message = e.message

    assert data == 'TestError'
    assert message == 'test error'


def test_ConflictError_error_code():
    assert ConflictError.code == 409


def test_ConflictError_error_message_and_data():
    try:
        raise ConflictError(fields=('username',))
    except ConflictError as e:
        data = e.data
        message = e.message

    assert data == 'ConflictError'
    assert message == 'username field(s) must be unique'


def test_NotFoundError_error_code():
    assert NotFoundError.code == 404


def test_NotFoundError_error_message_and_data():
    try:
        raise NotFoundError(resource='user')
    except NotFoundError as e:
        data = e.data
        message = e.message

    assert data == 'NotFoundError'
    assert message == 'user not found'
