from unittest import mock

from arango.exceptions import (
    CollectionCreateError,
    DatabaseCreateError
)

from users.api import connect_arango


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
    mock_db = MockArangoClient().create_database()
    mock_db.create_collection.assert_called_with('users')


@mock.patch('users.api.arango.ArangoClient')
def test_connect_arango_handle_existing_collection_exception(MockArangoClient):
    def collection_exists(name):
        if name == 'users':
            raise CollectionCreateError(None)

    mock_db = MockArangoClient().create_database()
    mock_db.create_collection.side_effect = collection_exists
    connect_arango()
    mock_db.collection.assert_called_with('users')
