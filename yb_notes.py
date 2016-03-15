__author__ = 'gerard_cote'

import sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash
from contextlib import closing


DATABASE = 'yb_notes.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'gerard_cote'
password = '2Boys235'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/new', methods=['GET'])
def new_message():
    return render_template('new_message.html')


@app.route('/create', methods=['POST'])
def create_message():
    try:
        g.db.execute("insert into yb_notes (parent, email, student, teacher, message, comments) values (?, ?, ?, ?, ?, ?);",
                 [
                     request.form['parent'], request.form['email'], request.form['student'],
                     request.form['teacher'], request.form['message'], request.form['comments']
                 ])
        g.db.commit()
        flash("New message was successfully added. You're all done!")
        return redirect(url_for('show_message', email=request.form['email'], message=request.form['message']))
    except Exception as e:
        flash("You already have a message created. You're all done or you can edit your message.")
        email = request.form['email']
        endpoint_url = '/edit_message/' + email + '/edit'
        return redirect(endpoint_url)


@app.route('/show', methods=['GET'])
def show_message():
    return render_template('show_message.html', email=request.args['email'], message=request.args['message'])


@app.route('/find_message', methods=['GET', 'POST'])
def find_message():
    if request.method == 'POST':
        email = request.form['email']
        endpoint_url = '/edit_message/' + email + '/edit'
        return redirect(endpoint_url)
    else:
        return render_template('find_message.html')


@app.route('/edit_message/<email>/edit', methods=['GET'])
def edit_message(email):
    cur = g.db.execute("select message from yb_notes where email = ?", [email])
    entry = [dict(message=row[0]) for row in cur.fetchall()]
    return render_template('edit_message.html', message=entry[0]['message'], email=[email][0])


@app.route('/update', methods=['POST'])
def update_message():
    edited_message = request.form['message']
    owner_email = request.form['email']

    g.db.execute("update yb_notes set message = ? where email = ?;", [edited_message, owner_email])
    g.db.commit()

    cur = g.db.execute("select message from yb_notes where email = ?;", [owner_email])
    entry = [dict(message=row[0]) for row in cur.fetchall()]

    flash("Entry was successfully edited. You're all done!")
    return redirect(url_for('show_message', email=owner_email, message=entry[0]['message']))


@app.route('/delete/<email>')
def delete_message(email):
    owner_email = email

    g.db.execute("delete from yb_notes where email = ?;", [owner_email])
    g.db.commit()

    return redirect(url_for('new_message'))


@app.route('/marcey_report')
def marcey_report():
    cur = g.db.execute("select * from yb_notes;")
    entries = [dict(
        id=row[0],
        email=row[1],
        teacher=row[2],
        parent=row[3],
        student=row[4],
        message=row[5],
        comments=row[6]
    ) for row in cur.fetchall()]
    return render_template('marcey_report.html', entries=entries)


if __name__ == '__main__':
    app.run()

