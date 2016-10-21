from users.models import engine


def test_create_all_models():
    assert 'users' in engine.table_names()
