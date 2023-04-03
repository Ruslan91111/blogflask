# Конфигурация для тестов - для создания тестового приложения и тестовой БД.
import os
import tempfile

import pytest
from blog import create_app
from blog.db import get_db, init_db


# Через контекстный менеджер открыть файл с временной конфигурацией DB 'data.sql'
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


# Создать тестовое приложение
@pytest.fixture
def app():
    # Создать временную папку для приложения и временный путь для БД.
    # По окончании теста, временный файл будет закрыт и удален
    db_fd, db_path = tempfile.mkstemp()
    # Создать тестовое приложение. В режиме тест, путь к тестовой БД.
    app = create_app(
        {
            'TESTING': True,
            'DATABASE': db_path,
        }
    )

    with app.app_context():
        # Инициализировать БД
        init_db()
        # Выполнить содержимое 'data.sql'.
        get_db().executescript(_data_sql)

    # Сохранить состояние
    yield app

    # Закрыть приложение, разорвать соединение
    os.close(db_fd)
    os.unlink(db_path)


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




