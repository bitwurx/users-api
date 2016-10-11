from users import exceptions


def test_UserExistsError_error_message():
    msg = exceptions.UserExistsError().args[0]
    assert msg == 'provided username already exists'


def test_UserNotFoundError_error_message():
    msg = exceptions.UserNotFoundError().args[0]
    assert msg == 'provided user id does not exist'
