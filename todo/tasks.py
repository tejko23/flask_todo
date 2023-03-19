from flask import (
    Blueprint, session, flash, g, redirect, render_template, request, url_for
)

from todo.auth import login_required
from todo.db import get_db

bp = Blueprint('tasks', __name__)

@bp.route('/')
@login_required
def index():
    user_id = session.get('user_id')
    db = get_db()
    tasks_list = db.execute(
        "SELECT * FROM tasks WHERE user_id = ?", (user_id,)
        ).fetchall()
    return render_template('tasks/index.html', tasks_list=tasks_list)


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