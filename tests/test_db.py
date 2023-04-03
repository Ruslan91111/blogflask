import sqlite3
import pytest

from blog.db import get_db


# Проверка соединения и разрыва соединения с БД.
def test_get_close_db(app):
    with app.app_context():
        # Установить соединение
        db = get_db()
        # Проверка установлено или нет
        assert db is get_db()

    # Вызвать исключение в контекстном менеджере.
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')
    # Проверить закрыто ли соединение
    assert 'closed' in str(e.value)


# Проверка инициализации БД.
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('blog.db.init_db', fake_init_db)

    # Вызвать функцию командой init-db при помощи фикстуры runner.
    result = runner.invoke(args=['init-db'])
    # Проверка на сообщение об инициализации данных в терминале.
    assert 'База данных инициализирована' in result.output
    assert Recorder.called

