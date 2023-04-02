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

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username ='a'",
        ).fetchone() is not None


