from unittest import mock

from users.models import User, get_engine


def test_table_is_users():
    user = User(password='test')
    assert user.__tablename__ == 'users'


def test_string_representation_is_correct():
    user = User(username='joe', password='test', email='joe@test.com')
    assert str(user) == '<User: joe, joe@test.com>'


@mock.patch('users.models.bcrypt.gensalt')
def test_hash_password_hashes_password(mock_gensalt):
    mock_gensalt.return_value = b'$2b$12$0n/2SwRAZIZFnlaLgdvswO'
    user = User(password='test')
    pwhash = b'$2b$12$0n/2SwRAZIZFnlaLgdvswOf6pnulheGIPr2xfiTEiYzdP7j.xeQ8S'
    assert user.password == pwhash


@mock.patch('users.models.os')
@mock.patch('users.models.create_engine')
def test_get_engine_creates_all_models(mock_create_engine, mock_os):
    mock_os.environ.get.side_effect = lambda k: {
        'MYSQL_ROOT_PASSWORD': 'password1',
        'MYSQL_DATABASE': 'alicia'
    }[k]
    get_engine()
    mock_create_engine.assert_called_with(
        'mysql+pymysql://root:password1@mariadb/alicia'
    )
