import json

from unittest import mock

from arango.exceptions import (
    CollectionCreateError,
    DatabaseCreateError
)

from users.api import connect_arango
from users.api import (
    UsersResourceV1
)


@mock.patch('users.api.arango.ArangoClient')
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


@mock.patch('users.api.arango.ArangoClient')
def test_connect_arango_creates_database(MockArangoClient):
    connect_arango()
    MockArangoClient().create_database.assert_called_with('alicia')


@mock.patch('users.api.arango.ArangoClient')
def test_connect_arango_handles_existing_database_exception(MockArangoClient):
    def database_exists(name):
        if name == 'alicia':
            raise DatabaseCreateError(None)

    MockArangoClient().create_database.side_effect = database_exists
    connect_arango()
    MockArangoClient().database.assert_called_with('alicia')


@mock.patch('users.api.arango.ArangoClient')
def test_connect_arango_creates_collection(MockArangoClient):
    connect_arango()
    db = MockArangoClient().create_database()
    db.create_collection.assert_called_with('users')


@mock.patch('users.api.arango.ArangoClient')
def test_connect_arango_handle_existing_collection_exception(MockArangoClient):
    def collection_exists(name):
        if name == 'users':
            raise CollectionCreateError(None)

    db = MockArangoClient().create_database()
    db.create_collection.side_effect = collection_exists
    connect_arango()
    db.collection.assert_called_with('users')


@mock.patch('users.api.bcrypt.gensalt')
@mock.patch('users.api.users')
def test_UsersResource_post_creates_user_document(mock_users, mock_gensalt):
    user = {'username': 'joe', 'password': 'test', 'email': 'joe@schmoe.com'}
    mock_gensalt.return_value = b'$2b$12$buE1MyflUVhDp92MkjQV3O'
    request = mock.Mock()
    request.body = json.dumps(user).encode()
    resource = UsersResourceV1(mock.MagicMock(), mock.Mock())
    resource.request = request
    resource.post()
    pwhash = b'$2b$12$buE1MyflUVhDp92MkjQV3OqXCVBhtMZk1bUywn6dTTBmTgy4WbEpe'
    mock_users.insert.assert_called_with({'username': 'joe',
                                          'password': pwhash,
                                          'email': 'joe@schmoe.com'})


@mock.patch('users.api.bcrypt.gensalt')
@mock.patch('users.api.cerberus.Validator')
def test_UsersResource_post_validates_request_data(
        MockValidator,
        mock_gensalt):
    mock_gensalt.return_value = b'$2b$12$buE1MyflUVhDp92MkjQV3O'
    user = {'username': 'joe', 'password': 'test', 'email': 'joe@schmoe.com'}
    resource = UsersResourceV1(mock.MagicMock(), mock.Mock())
    resource.request.body = json.dumps(user).encode()
    resource.post()
    assert resource.schema == {
        'username': {'type': 'string'},
        'password': {'type': 'string'},
        'email': {'type': 'string'}
    }
    pwhash = b'$2b$12$buE1MyflUVhDp92MkjQV3OqXCVBhtMZk1bUywn6dTTBmTgy4WbEpe'
    MockValidator().validate.assert_called_with({
        'email': user['email'],
        'username': user['username'],
        'password': pwhash
    }, resource.schema)
