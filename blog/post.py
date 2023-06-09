from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from .auth import login_required
from .db import get_db


bp = Blueprint('post', __name__)


@bp.route('/')
# Главная страница
def index():
    # Подключиться к БД
    db = get_db()
    # Осуществить выборку всех постов из БД
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('post/index.html', posts=posts)


# Создание постов
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Заголовок не должен быть пустым.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('post.index'))

    return render_template('post/create.html')


# Вывод одного поста.
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Пост с id {id} не существует")

    # Если не тот пользователь.
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


# Редактирование поста.
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    # Получить нужный пост.
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Заголовок не должен быть пустым.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('post.index'))

    return render_template('post/update.html', post=post)


# Удалить пост.
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # Получить пост.
    get_post(id)
    # Установить соединение с БД
    db = get_db()
    # Удалить
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('post.index'))

