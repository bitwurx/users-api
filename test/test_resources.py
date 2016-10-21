from unittest import mock

from users.resources import UsersResource


@mock.patch('users.resources.sessionmaker')
@mock.patch('users.resources.get_engine')
def test_initialize_UsersResource(mock_get_engine, mock_sessionmaker):
    mock_sessionmaker()().is_active = True
    resource = UsersResource()
    assert mock.call(bind=mock_get_engine()) in mock_sessionmaker.mock_calls
    assert resource.session.is_active is True
    assert UsersResource.on_get is not None


def test_on_get_returns_all_users():
    pass
