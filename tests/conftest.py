# Конфигурация для тестов - для создания тестового приложения и тестовой БД.
import os
import tempfile

import pytest
from blog import create_app
from blog.db import get_db, init_db


# Через контекстный менеджер открыть файл с временной конфигурацией 'data.sql'
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


# Создать тестовое приложение
@pytest.fixture
def app():
    # Создать временную папку для приложения и временный путь для БД.
    # По окончании теста, временный файл будет закрыт и удален
    db_fd, db_path = tempfile.mktemp()

    app = create_app(
        {
            'TESTING': True,
            'DATABASE': db_path,
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.close(db_path)


# Тестовый клиент: запросы к приложению без запуска сервера.
@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# Проверка аутентификации
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)




