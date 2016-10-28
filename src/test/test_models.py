from unittest import mock

from arango.exceptions import (
    CollectionCreateError,
    DatabaseCreateError
)

from users.models import connect_arango
from users.models import User


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
def test_connect_arango_creates_collection(MockArangoClient):
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


def test_User_has_expected_validation_model_schema():
    assert User.schema == {'username': {'type': 'string'},
                           'password': {'type': 'string'},
                           'email': {'type': 'string'}}


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
    user = User(username='joe', password='test', email='joe@schmoe.com')
    mock_gensalt.return_value = b'$2b$12$buE1MyflUVhDp92MkjQV3O'
    mock_users.insert.return_value = {'_key': 27643}
    pwhash = '$2b$12$buE1MyflUVhDp92MkjQV3OqXCVBhtMZk1bUywn6dTTBmTgy4WbEpe'
    assert user.create() == {'username': 'joe',
                             'password': pwhash,
                             'email': 'joe@schmoe.com',
                             'id': 27643}
    mock_users.insert.assert_called_with({'username': 'joe',
                                          'password': pwhash,
                                          'email': 'joe@schmoe.com'})
