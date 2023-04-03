"""Функции определяющие соединение с БД, закрытие соединения,
инициализацию БД"""
import sqlite3
import click
from flask import g, current_app


# Соединение с БД - устанавливается перед каждым запросом,
# заканчивается перед получением ответа.
def get_db():
    # Если соединения нет, то установить.
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db


# Если соединение не закрыто - закрыть.
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


# Добавим функции которые реализуют SQL команды to the db.py

# Инициализировать БД
def init_db():
    # Установим соединение
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# Инициализировать БД командой "flask --app blog init-db"
@click.command('init-db')
def init_db_command():
    """Очистить данные и создать новые таблицы."""
    init_db()
    click.echo('База данных инициализирована')


# Инициализировать приложение
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

