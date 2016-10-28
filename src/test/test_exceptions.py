from users.exceptions import (
    BaseError,
    BadRequestError
)


def test_BaseError_response_returns_rest_compliant_response_body():
    try:
        raise BaseError(message='something went wrong',
                        data='ResourceNotFound')
    except BaseError as e:
        e.code = 404
        response = e.response()

    assert response == {'code': 404,
                        'status': 'error',
                        'message': 'something went wrong',
                        'data': 'ResourceNotFound'}


def test_BadRequestError_error_message():
    try:
        raise BadRequestError(message='test error', data='TestError')
    except BadRequestError as e:
        message = e.message

    assert message == 'test error'
