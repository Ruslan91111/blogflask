import pytest
from blog.db import get_db


# Тестирование главной страницы.
def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2023-02-04' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


# Тестирование создания, обновления и удаления страницы.
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(app, client, auth):
    # Меняем автора поста.
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()
    # Текущий пользователь не может изменять посты другого пользователя
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # Текущий пользователь не должен видеть ссылки на редактирование поста
    assert b'href="/1/update"' not in client.get('/').data


@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

