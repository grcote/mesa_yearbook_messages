import sendgrid, time
from flask import Flask, request, g, redirect, url_for, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.heroku import Heroku

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/yb_messages'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'Iwck15VnR4106SfLUyXAZTki3SUsg0Ab'
heroku = Heroku(app)
db = SQLAlchemy(app)


class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    teacher = db.Column(db.String(40))
    parent = db.Column(db.String(40))
    student = db.Column(db.String(40))
    message = db.Column(db.String(120))
    comments = db.Column(db.String(240))


def send_email(email, yb_message):
    client = sendgrid.SendGridClient("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")
    message = sendgrid.Mail()

    message.add_to("grcote@gmail.com")
    message.set_from("grcote@gmail.com")
    message.set_subject("Mesa Yearbook Message")
    message.set_html("{0},{1},{2}".format(email, yb_message, time.time()))

    client.send(message)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/new', methods=['GET'])
def new_message():
    return render_template('new_message.html')


@app.route('/create', methods=['POST'])
def create_message():
    try:
        new_message = Message(
            email=request.form['email'],
            teacher=request.form['teacher'],
            parent=request.form['parent'],
            student=request.form['student'],
            message=request.form['message'],
            comments=request.form['comments']
        )
        db.session.add(new_message)
        db.session.commit()
        flash("You're all done!")
        return redirect(url_for('show_message', email=request.form['email'], message=request.form['message']))
    except Exception as e:
        flash("You already have a message created. You're all done or you can edit your message.")
        email = request.form['email']
        endpoint_url = '/edit_message/' + email + '/edit'
        return redirect(endpoint_url)


@app.route('/show', methods=['GET'])
def show_message():
    send_email(email=request.args['email'], yb_message=request.args['message'])
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
    try:
        message = Message.query.filter_by(email=email).first()
        return render_template('edit_message.html', message=message.message, email=email)
    except Exception as e:
        flash("No message associated with email: {0}. Create new message below.".format(email))
        return redirect(url_for('new_message'))


@app.route('/update', methods=['POST'])
def update_message():
    edited_message = request.form['message']
    owner_email = request.form['email']

    message = Message.query.filter_by(email=owner_email).first()
    message.message = edited_message
    db.session.commit()

    message = Message.query.filter_by(email=owner_email).first()

    flash("You're all done!")
    return redirect(url_for('show_message', email=message.email, message=message.message))


@app.route('/delete/<email>')
def delete_message(email):
    owner_email = email

    message = Message.query.filter_by(email=owner_email).first()
    db.session.delete(message)
    db.session.commit()

    return redirect(url_for('new_message'))


@app.route('/marcey_report')
def marcey_report():
    entries = Message.query.all()
    return render_template('marcey_report.html', entries=entries)

if __name__ == '__main__':
    app.debug = True
    app.run()


