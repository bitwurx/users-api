import asyncio

from unittest import mock

from users import crud
from users import exceptions


@mock.patch('users.crud.bcrypt')
def test_create_writes_record_to_database(mock_bcrypt):
    mock_cursor = mock.MagicMock()
    mock_cursor.execute.return_value = 1
    mock_cursor.fetchone.return_value = {'id': 1,
                                         'username': 'joe',
                                         'email': 'joe@schmoe.com',
                                         'password': 'abcxyz'}
    mock_bcrypt.hashpw.return_value = 'abcxyz'
    coro = crud.create(mock_cursor, 'joe', 'joe@schmoe.com', 'password1')
    result = asyncio.get_event_loop().run_until_complete(coro)
    mock_cursor.execute.assert_has_calls([
        mock.call('''\
INSERT INTO `users`
    (`username`, `email`, `password`)
VALUES
    (%s, %s, %s);
''', ('joe', 'joe@schmoe.com', 'abcxyz',)),
        mock.call('''\
SELECT
    *
FROM
    `users`
WHERE
    id = %s;
''', (1))
    ])

    assert result == {'id': 1,
                      'username': 'joe',
                      'email': 'joe@schmoe.com',
                      'password': 'abcxyz'}


def test_create_throws_exception_if_username_exists():
    def raise_exists(*args):
        raise exceptions.UserExistsError()

    message = None
    mock_cursor = mock.MagicMock()
    mock_cursor.execute.side_effect = raise_exists
    coro = crud.create(mock_cursor, 'joe', 'joe@schmoe.com', 'password1')

    try:
        asyncio.get_event_loop().run_until_complete(coro)
    except exceptions.UserExistsError as e:
        message = e.args[0]

    assert message == 'provided username already exists'
