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
def test_login_required(app, client, path):
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


def test_create(client,auth, app):
    # Залогиниться
    auth.login()
    # Проверка кода соединения
    assert client.get('/create').status_code == 200
    # Создаем пост
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        # Устанавливаем соединение с базой
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    # Проверяем, что изменение в заголовке поста сохраняются в БД.
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id =1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
# Проверка на валидность введенных данных - нельзя передавать пустую строку
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'Title is required.' in response.data


# Тестирование удаления поста
def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers['Location'] == '/'

    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id =1').fetchone()
        assert post is None
