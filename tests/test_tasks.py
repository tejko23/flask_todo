import pytest
from todo.db import get_db
from jinja2 import Environment, PackageLoader
from flask import url_for

from datetime import datetime

def test_index(client, auth):
    response = client.get('/')
    assert b"Redirecting" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'2024-01-01' in response.data
    assert b'test task' in response.data
    assert b'href="/create"' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
    '/1/done',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"

def test_author_required(app, client, auth):
    with app.app_context():
        db = get_db()
        db.execute('UPDATE tasks SET user_id = 2 WHERE user_id = 1')
        db.commit()

    auth.login()
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    assert client.post('/1/done').status_code == 403
    assert b'href="/1/update"' not in client.get('/').data

@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
    '/2/done',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

def test_tables(app):
    with app.test_client() as client:
        with app.app_context():
            with client.session_transaction() as session:
                session['user_id'] = 1
            
            for table in ["todo", "todo_today", "completed", "all", "invalid_table"]:
                response = client.post('/tables', data={'table': table})
                assert response.status_code == 200

                db = get_db()
                match table:
                    case "todo":
                        tasks_list = db.execute(
                            "SELECT * FROM tasks WHERE user_id = ? AND completed = ?", 
                            (1, 0)).fetchall()
                    case "todo_today":
                        today = datetime.today().date()
                        tasks_list = db.execute(
                            "SELECT * FROM tasks WHERE user_id = ? AND completed = ? AND due_date = ?", 
                            (1, 0, today,)).fetchall()
                    case "completed":
                        tasks_list = db.execute(
                            "SELECT * FROM tasks WHERE user_id = ? AND completed = ?", 
                            (1, 1,)).fetchall()
                    case "all":
                        tasks_list = db.execute(
                            "SELECT * FROM tasks WHERE user_id = ?", (1,)).fetchall()
                    case "invalid_table":
                        tasks_list = []
                        
                env = Environment(loader=PackageLoader('todo', 'templates'))
                env.globals.update({
                    'url_for': url_for
                })
                tasks_table = env.get_template('tasks/tables.html').module.tasks_table
                expected_html = ""
                if tasks_list:
                    expected_html = tasks_table(tasks_list)
                    assert response.get_data(as_text=True).count('<tr>') == len(tasks_list) + 1
                else:
                    expected_html = "No tasks to show"
                    assert response.get_data(as_text=True).count('<tr>') == len(tasks_list)

                assert expected_html in response.get_data(as_text=True)
                

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    response = client.post(
        '/create',
        data={
            'task': 'created',
            'due-date': '2023-05-01'
        },
        content_type='multipart/form-data'
    )
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(task_id) FROM tasks').fetchone()[0]
        assert count == 2

def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    response = client.post(
        '/1/update',
        data={
            'task': 'updated',
            'due-date': '2023-05-01'
        },
        content_type='multipart/form-data'
    )

    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        task = db.execute('SELECT * FROM tasks WHERE task_id = 1').fetchone()
        assert task['task'] == 'updated'
        assert task['due_date'] == '2023-05-01'

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'task': '', 'due-date': ''})
    assert b'You need to add text in the task field.' in response.data

    response = client.post(path, data={'task': 'date', 'due-date': '2020-01-01'})
    assert b'The date cannot be earlier than today.' in response.data

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        task = db.execute('SELECT * FROM tasks WHERE task_id = 1').fetchone()
        assert task is None

def test_complete(client, auth, app):
    auth.login()
    response = client.post('/1/done')
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with app.app_context():
        db = get_db()
        task = db.execute('SELECT * FROM tasks WHERE task_id = 1').fetchone()
        assert task['completed'] == 1

def test_complete_without_login(client):
    response = client.post('/1/done')
    assert response.status_code == 302
    assert response.headers['Location'] == '/auth/login'