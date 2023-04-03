import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db

# Создание экземпляра класса Blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
# Регистрация пользователя.
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # Проверка валидности вводимых данных.
        if not username:
            error = 'Необходимо ввести имя пользователя.'
        elif not password:
            error = 'Необходимо ввести пароль.'

        # Если введены имя пользователя и пароль, без ошибки.
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"Пользователь с именем {username} уже зарегистрирован."
            else:
                # Перекинуть на страницу входа.
                return redirect(url_for("auth.login"))
        # Если валидация не прошла показать ошибку.
        flash(error)

    return render_template('auth/register.html')


# Вход на сайт.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # После введения логина и пароля, установить соединение
        db = get_db()
        error = None
        # Осуществить выборку из БД по введенному имени пользователя.
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Неверное имя пользователя.'
        elif not check_password_hash(user['password'], password):
            error = 'Неверный пароль.'

        # При прохождении валидации.
        if error is None:
            session.clear()
            # В текущую сессию запихнуть id пользователя.
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# Передача id пользователя перед запросом.
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    # Если пользователь не залогинился.
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# Выйти
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Если для совершения действий необходимо войти на сайт. Создаем декоратор.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # Не залогинившийся - перенаправить на страницу входа.
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view