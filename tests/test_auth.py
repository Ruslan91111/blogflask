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
    assert response.headers['location'] == "/auth/login"

    # Проверить имеется ли запись в БД с указанным пользователем.
    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username ='a'",
        ).fetchone() is not None


# Проверяем работу регистрации при неправильном вводе данных (не ввели имя, не ввели пароль).
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', 'Необходимо ввести имя пользователя.'),
    ('a', '', 'Необходимо ввести пароль.'),
    ('test', 'test', f"Пользователь с именем test уже зарегистрирован.")
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    # Находятся ли перечисленные в parametrize сообщения в ответе.
    assert message in response.get_data(as_text=True)

# data содержит ответ в байтах. Байты сравниваются с байтами.
# Если нужно сравнить текст, то следует использовать
# !!! get_data(as_text=True).


# Тестируем работу входа.
def test_login(client, auth):
    # Проверка соединения
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    # Проверка перенаправления
    assert response.headers["Location"] == "/"

    # Работа клиента.
    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


# Тестируем вхождение на сайт, параметризуя данные.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', 'Неверное имя пользователя.'),
    ('test', 'a', 'Неверный пароль.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.get_data(as_text=True)


# Тестирование выхода из учетной записи.
def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session




