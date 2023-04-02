import pytest
from flask import g, session
from blog.db import get_db


# Тестируем регистрацию пользователя.
def test_register(client, app):
    # Проверка соединения по определенному url
    assert client.get('/auth/register').status_code == 200

    # Вводим имя пользователя и пароль при регистрации. Получаем ответ.
    response = client.post(
        'auth/register', data={'username': 'a', 'password': 'a'}
    )
    # Проверяем перенаправление после регистрации на страницу входа.
    assert response.headers['location'] == "auth/login"

    # Проверить имеется ли запись в БД с указанным пользователем.
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username ='a'",
        ).fetchone() is not None


# Проверяем работу регистрации при неправильном вводе данных.
@pytest.mark.parametrize(('username', 'password', 'message'),(
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
# Подставляем поочереди данные(username, password), указанные выше в parametrize.
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


# Тестируем работу входа.
def test_login(client, auth):
    # Проверка соединения
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    # Проверка перенаправления
    assert response.headers['location'] == '/'

    # Работа клиента.
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


# Тестируем вхождение на сайт, параметризуя данные.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


# Тестирование выхода из учетной записи.
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session




