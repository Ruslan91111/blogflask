import pytest
from blog.db import get_db


# Тестирование главной страницы.
def test_index(client, auth):
    # Ответ для неавторизованного пользователя
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    # Залогиниться. Функция auth определена в conftest.py.
    auth.login()
    # Ответ для авторизованного пользователя.
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2023-04-03' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data


# Незалогинившегося пользователя при попытке создать, обновить, удалить пост
# должно выкидывать на страницу '/auth/login'.
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == '/auth/login'


# Пост должен менять только его автор.
def test_author_required(app, client, auth):
    with app.app_context():
        # Соединение с БД.
        db = get_db()
        # Меняем автора поста на id = 2
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    # Логинимся.
    auth.login()
    # Текущий пользователь не может изменять или удалять посты другого пользователя
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # Текущий пользователь не должен видеть ссылки на редактирование поста
    assert b'href="/1/update"' not in client.get('/').data


# Поста не существует - поэтому при попытке изменить или удалить должна быть ошибка 404.
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    # Залогинился.
    auth.login()
    # Не может найти пост.
    assert client.post(path).status_code == 404


# Создание поста.
def test_create(client, auth, app):
    # Залогиниться
    auth.login()
    # Проверка кода соединения. 200 - OK
    assert client.get('/create').status_code == 200
    # Создаем пост
    client.post('/create', data={'title': 'created', 'body': ''})

    with app.app_context():
        # Устанавливаем соединение с базой
        db = get_db()
        # Один пост написали выше, один создается в data.sql
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        # Поэтому количество постов в БД должно быть два.
        assert count == 2


# Обновить пост
def test_update(client, auth, app):
    # Логинимся
    auth.login()
    # Код соединения
    assert client.get('/1/update').status_code == 200
    # Меняем что-то в посте.
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    # Проверяем, что изменение в заголовке поста сохраняются в БД.
    # Формируем контекст приложения.
    with app.app_context():
        db = get_db()
        # Выбираем измененный пост
        post = db.execute('SELECT * FROM post WHERE id =1').fetchone()
        # Проверяем ожидаемый заголовок
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
# Передаем при создании и обновлении пустую строку в 'title' - а в ответ текст ошибки.
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert 'Заголовок не должен быть пустым.' in response.get_data(as_text=True)


# Тестирование удаления поста
def test_delete(client, auth, app):
    # Логинимся
    auth.login()
    # Ответ после удаления
    response = client.post('/1/delete')
    # Перенаправление после удаления.
    assert response.headers['Location'] == '/'

    with app.app_context():
        db = get_db()
        # При выборке удаленного поста
        post = db.execute(' SELECT * FROM post WHERE id =1 ').fetchone()
        # Он отсутствует
        assert post is None
