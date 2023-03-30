from flask import (
    Blueprint, session, flash, g, redirect, render_template, request, url_for,
    get_template_attribute
)
from werkzeug.exceptions import abort

from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('tasks', __name__)

@bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    db = get_db()
    tasks_list = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND completed = ?", (user_id, 0,)
        ).fetchall()
    return render_template('tasks/index.html', tasks_list=tasks_list)


@bp.route('/tables', methods=['POST'])
@login_required
def tables():
    user_id = session.get('user_id')
    db = get_db()
    table = request.form['table']
    if table == "todo":
        tasks_list = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND completed = ?", (user_id, 0,)
            ).fetchall()
        todo = get_template_attribute('tasks/tables.html', 'todo')
        return todo(tasks_list)
        
    elif table == "completed":
        tasks_list = db.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND completed = ?", (user_id, 1,)
            ).fetchall()
        completed = get_template_attribute('tasks/tables.html', 'completed')
        return completed(tasks_list)
    else:
        return None


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        task = request.form['task']
        error = None

        if not task:
            error = 'You need to add text in the task field.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO tasks (user_id, task) VALUES (?, ?)", 
                (g.user['id'], task)
            )
            db.commit()
            return redirect(url_for('tasks.index'))

    return render_template('tasks/create.html')


def get_task(id, check_author=True):
    task = get_db().execute(
        'SELECT t.task_id, user_id, task' 
        ' FROM tasks t JOIN user u ON t.user_id = u.id '
        ' WHERE t.task_id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Post id {id} doesn't exist.")
    
    if check_author and task['user_id'] != g.user['id']:
        abort(403)

    return task


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task_data = get_task(id)

    if request.method == 'POST':
        task = request.form['task']
        error = None

        if not task:
            error = 'You need to add text in the task field.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE tasks SET task = ? WHERE task_id = ?", 
                (task, id)
            )
            db.commit()
            return redirect(url_for('tasks.index'))

    return render_template('tasks/update.html', task_data=task_data)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM tasks WHERE task_id = ?', (id,))
    db.commit()
    return redirect(url_for('tasks.index'))


@bp.route('/<int:id>/done', methods=('POST',))
@login_required
def complete(id):
    get_task(id)
    db = get_db()
    db.execute('UPDATE tasks SET completed = 1 WHERE task_id = ?', (id,))
    db.commit()
    return redirect(url_for('tasks.index'))