import json

from unittest import mock

from arango.exceptions import (
    CollectionCreateError,
    DatabaseCreateError,
    DocumentInsertError
)

from users.models import connect_arango
from users.models import Session, User


@mock.patch('users.models.arango.ArangoClient')
def test_connect_arango_creates_database_client(MockArangoClient):
    connect_arango()
    MockArangoClient.assert_called_with(
        protocol='http',
        host='arangodb',
        port=8529,
        username='root',
        password='IXocx/FJV7jwVQ+DS0RagxeZiUD24Vlrp0LL6UpRfOHx',
        enable_logging=True
    )


@mock.patch('users.models.arango.ArangoClient')
def test_connect_arango_creates_database(MockArangoClient):
    connect_arango()
    MockArangoClient().create_database.assert_called_with('alicia')


@mock.patch('users.models.arango.ArangoClient')
def test_connect_arango_handles_existing_database_exception(MockArangoClient):
    def database_exists(name):
        if name == 'alicia':
            raise DatabaseCreateError(None)

    MockArangoClient().create_database.side_effect = database_exists
    connect_arango()
    MockArangoClient().database.assert_called_with('alicia')


@mock.patch('users.models.arango.ArangoClient')
def test_connect_arango_creates_users_collection(MockArangoClient):
    connect_arango()
    db = MockArangoClient().create_database()
    db.create_collection.assert_called_with('users')


@mock.patch('users.models.arango.ArangoClient')
def test_connect_arango_handles_existing_collection_exception(
        MockArangoClient):
    def collection_exists(name):
        if name == 'users':
            raise CollectionCreateError(None)

    db = MockArangoClient().create_database()
    db.create_collection.side_effect = collection_exists
    connect_arango()
    db.collection.assert_called_with('users')


@mock.patch('users.models.arango.ArangoClient')
def test_connect_creates_unique_username_hash_index(MockArangoClient):
    connect_arango()
    coll = MockArangoClient().create_database().create_collection()
    coll.add_hash_index.assert_called_with(fields=('username',), unique=True)


def test_User_unique_fields():
    assert User.unique == ('username',)


def test_User_has_expected_validation_model_schema():
    assert User.schema == {'username': {'type': 'string', 'required': True},
                           'password': {'type': 'string', 'required': True},
                           'email': {'type': 'string', 'required': True}}


def test_User_passes_validation():
    u = User(username='joe', password='password1', email='joe@schcmoe.com')
    u.validate()


def test_User_validate_raises_exception_if_parameter_is_missing():
    error = None

    try:
        User(username='joe', password='password1').validate()
    except Exception as e:
        error = e

    assert error.data == 'ValidationError'
    assert error.message == {'email': ['null value not allowed']}


@mock.patch('users.models.users')
@mock.patch('users.models.bcrypt.gensalt')
def test_User_create_adds_user_to_database(mock_gensalt, mock_users):
    mock_gensalt.return_value = b'$2b$12$buE1MyflUVhDp92MkjQV3O'
    mock_users.insert.return_value = {'_key': 27643}
    pwhash = '$2b$12$buE1MyflUVhDp92MkjQV3OqXCVBhtMZk1bUywn6dTTBmTgy4WbEpe'
    user = User(username='joe', password='test', email='joe@schmoe.com')
    assert user.create() == {'username': 'joe',
                             'email': 'joe@schmoe.com',
                             'id': 27643}
    mock_users.insert.assert_called_with({'username': 'joe',
                                          'password': pwhash,
                                          'email': 'joe@schmoe.com'})


@mock.patch('users.models.users')
@mock.patch('users.models.bcrypt')
def test_User_create_raises_excpetion_if_user_exists(mock_bcrypt, mock_users):
    def mock_insert(*args, **kwargs):
        raise DocumentInsertError(None)

    mock_users.insert.side_effect = mock_insert
    user = User(username='joe', password='test', email='joe@schmoe.com')
    error = None

    try:
        user.create()
    except Exception as e:
        error = e

    assert error.message == 'username field(s) must be unique'


def test_Session_schema():
    assert Session.schema == {'username': {'type': 'string', 'required': True},
                              'password': {'type': 'string', 'required': True}}


@mock.patch('users.models.redis')
@mock.patch('users.models.users')
@mock.patch('users.models.bcrypt')
def test_Session_create_gets_user_from_database(
        mock_bcrypt,
        mock_users,
        mock_redis):
    mock_users.find.return_value = [{'username': 'joe',
                                     'password': 'test',
                                     '_key': 12345}]
    mock_bcrypt.hashpw.return_value = b'test'
    session = Session(username='joe', password='test')
    session.create()
    mock_users.find.assert_called_with({'username': 'joe'})


@mock.patch('users.models.users')
@mock.patch('users.models.bcrypt')
def test_Session_create_raises_exception_if_username_not_exists(
        mock_bcrypt,
        mock_users):
    mock_users.find.return_value = []
    session = Session(username='joe', password='test')
    error = None

    try:
        session.create()
    except Exception as e:
        error = e

    assert error.data == 'NotFoundError'
    assert error.message == 'user not found'


@mock.patch('users.models.redis')
@mock.patch('users.models.users')
@mock.patch('users.models.bcrypt')
def test_Session_create_checks_password(mock_bcrypt, mock_users, mock_redis):
    mock_users.find.return_value = [{'password': 'abc123',
                                     'username': 'joe',
                                     '_key': 12345}]
    mock_bcrypt.hashpw.return_value = b'abc123'
    session = Session(username='jane', password='abc123')
    session.create()
    mock_bcrypt.hashpw.assert_called_with(b'abc123', b'abc123')


@mock.patch('users.models.os')
@mock.patch('users.models.base64')
@mock.patch('users.models.redis.Redis')
@mock.patch('users.models.users')
@mock.patch('users.models.bcrypt')
def test_Session_create_session_token(
        mock_bcrypt,
        mock_users,
        MockRedis,
        mock_base64,
        mock_os):
    mock_users.find.return_value = [{'password': 'password!',
                                     '_key': 12345}]
    mock_bcrypt.hashpw.return_value = b'password!'
    mock_base64.b64encode.return_value = \
        b'YXC+oPIbOKNH6jGu6BFDXyPEReDbC6Pc0hsJ6lRF6E50'
    mock_os.urandom.return_value = 'abc123'
    session = Session(username='joe', password='password!')
    assert session.create() == {
        'token': 'YXC+oPIbOKNH6jGu6BFDXyPEReDbC6Pc0hsJ6lRF6E50'
    }
    mock_os.urandom.assert_called_with(33)
    mock_base64.b64encode.assert_called_with('abc123')
    MockRedis().setex.assert_called_with(
        b'YXC+oPIbOKNH6jGu6BFDXyPEReDbC6Pc0hsJ6lRF6E50',
        json.dumps({'user_id': 12345}),
        3600
    )


@mock.patch('users.models.users')
@mock.patch('users.models.bcrypt')
def test_Session_create_raises_exception_if_password_is_invalid(
        mock_bcrypt,
        mock_users):
    mock_bcrypt.hashpw.return_value = b'abc123'
    mock_users.find.return_value = [{'username': 'joe', 'password': 'xyz123'}]
    session = Session(username='joe', password='xyz123')
    error = None

    try:
        session.create()
    except Exception as e:
        error = e

    assert error.data == 'InvalidCredentialsError'
    assert error.message == 'incorrect username or password'


@mock.patch('users.models.users')
def test_Session_validate_raises_exception_if_parameter_is_missing(mock_users):
    session = Session(username='jane')
    error = None

    try:
        session.validate()
    except Exception as e:
        error = e

    assert error.message == {'password': ['null value not allowed']}


@mock.patch('users.models.users')
@mock.patch('users.models.redis.Redis')
def test_Session_read_gets_user_session_details(MockRedis, mock_users):
    MockRedis().get.return_value = b'{"user_id": 12345}'
    mock_users.get.return_value = {'username': 'joe',
                                   'password': 'password1!',
                                   'email': 'jared.patrick@gmail.com'}
    session = Session(token='1a2b3c')
    user = session.read()
    assert user['username'] == 'joe'
    assert user['email'] == 'jared.patrick@gmail.com'
    assert user.get('password', None) is None


@mock.patch('users.models.users')
@mock.patch('users.models.redis.Redis')
def test_Session_read_raises_exception_if_token_not_found(
        MockRedis,
        mock_users):
    MockRedis().get.return_value = None
    error = None

    try:
        Session(token='xyz').read()
    except Exception as e:
        error = e

    assert error.data == 'NotFoundError'
    assert error.message == 'session token not found'


@mock.patch('users.models.users')
@mock.patch('users.models.redis.Redis')
def test_Session_update_resets_existing_session(MockRedis, mock_users):
    MockRedis().get.return_value = '{"user_id": 12345}'
    session = Session(token='abc123')
    assert session.update() == {'token': 'abc123'}
    MockRedis().get.assert_called_with('abc123')
    MockRedis().setex.assert_called_with('abc123', '{"user_id": 12345}', 3600)


@mock.patch('users.models.users')
@mock.patch('users.models.redis.Redis')
def test_Session_update_raises_exceptions_if_token_not_found(
        MockRedis,
        mock_users):
    MockRedis().get.return_value = None
    session = Session(token='xyz321')
    error = None

    try:
        session.update()
    except Exception as e:
        error = e

    assert error.data == 'NotFoundError'
    assert error.message == 'session token not found'


@mock.patch('users.models.users')
@mock.patch('users.models.redis.Redis')
def test_Session_delete_session_token(MockRedis, mock_users):
    session = Session(token='abc123')
    assert session.delete() == {}
    MockRedis().delete.assert_called_with('abc123')


@mock.patch('users.models.users')
@mock.patch('users.models.redis.Redis')
def test_Session_delete_raises_exception_if_token_not_found(
        MockRedis,
        mock_users):
    MockRedis().get.return_value = None
    session = Session(token='1a2b3c')
    error = None

    try:
        session.delete()
    except Exception as e:
        error = e

    assert error.data == 'NotFoundError'
    assert error.message == 'session token not found'
