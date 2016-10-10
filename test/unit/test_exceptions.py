from users import exceptions


def test_UserExistsError_error_message():
    msg = exceptions.UserExistsError().args[0]
    assert msg == 'provided username already exists'
