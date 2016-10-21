from unittest import mock

from users.models import User


@mock.patch('users.models.create_engine')
def test_table_is_users(mock_create_engine):
    user = User(password='test')
    assert user.__tablename__ == 'users'


@mock.patch('users.models.create_engine')
def test_string_representation_is_correct(mock_create_engine):
    user = User(username='joe', password='test', email='joe@test.com')
    assert str(user) == '<User: joe, joe@test.com>'


@mock.patch('users.models.create_engine')
@mock.patch('users.models.bcrypt.gensalt')
def test_hash_password_hashes_password(mock_gensalt, mock_create_engine):
    mock_gensalt.return_value = b'$2b$12$0n/2SwRAZIZFnlaLgdvswO'
    user = User(password='test')
    pwhash = b'$2b$12$0n/2SwRAZIZFnlaLgdvswOf6pnulheGIPr2xfiTEiYzdP7j.xeQ8S'
    assert user.password == pwhash
