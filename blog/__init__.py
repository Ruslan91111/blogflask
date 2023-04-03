"""Содержит фабрику приложений."""
import os
from flask import Flask

from . import db, auth, post


# Создает само приложение.
def create_app(test_config=None):  # Принимает на вход конфигурацию.
    # Создать экземпляр Flask
    # instance_relative_config - говорит приложению о том, что файл с конфигурациями
    # находится в папке instance, которая рядом с папкой приложением
    app = Flask(__name__, instance_relative_config=True)

    # Несколько настроек по умолчанию.
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'blog.sqlite')
    )

    # Если есть файл с настройками, перезаписывает их вместо настроек по умолчанию.
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Если нет, то используются настройки по умолчанию, указанные в параметрах функции.
        app.config.from_mapping(test_config)

    # Проверить наличие папки instance
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Приветственная страница.
    @app.route('/hello')
    def hello():
        return 'Hello, man'

    # Инициализируем приложение и БД.
    db.init_app(app)

    # Зарегистрировать blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(post.bp)

    # Представления post не будут иметь префикса.
    app.add_url_rule('/', endpoint='index')

    return app






