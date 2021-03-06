import bcrypt

from flask import Flask, session, redirect, render_template, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

from FlaskForms import LoginForm, RegisterForm
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'allo'
login_manager = LoginManager()
login_manager.init_app(app)
# without setting the login_view, attempting to access @login_required endpoints will result in an error
# this way, it will redirect to the login page
login_manager.login_view = 'login'
app.config['USE_SESSION_FOR_NEXT'] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data/usersdb.db"

db = SQLAlchemy(app)


class DBUser(db.Model):
    __tablename__ = 'users'
    username = db.Column(db.Text(), primary_key=True)
    email = db.Column(db.Text(), nullable=False)
    password = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return "<User {}: {} {}>".format(self.username, self.email)


# from app import db
# db.create_all()
# db.session.commit()

class SessionUser(UserMixin):
    def __init__(self, username, email, password=None):
        self.id = username
        self.email = email
        self.password = password

@app.route('/')
def plain():
    return render_template("Main.html")

@app.route('/main')
def main():
    return render_template("Main.html")

@app.route('/purpose')
def purpose():
    return render_template("Assignement-1-SOEN-287.html")

@app.route('/players')
def players():
    return render_template("Players.html")

@app.route('/schedule')
def schedule():
    return render_template("Schedule.html")

@app.route('/ranking')
def ranking():
    return render_template("Standings.html")

# this is used by flask_login to get a user object for the current user
@login_manager.user_loader
def load_user(user_id):
    user = find_user(user_id)
    # user could be None
    if user:
        # if not None, hide the password by setting it to None
        user.password = None
    return user


def find_user(username):
    user = DBUser.query.filter_by(username=username).first()
    if user:
        user = SessionUser(user.username, user.email, user.password)
    return user


@app.route('/1')
def index():
    return render_template('index2.html', username=session.get('username'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = find_user(form.username.data)
        # user could be None
        # passwords are kept in hashed form, using the bcrypt algorithm
        if user and bcrypt.checkpw(form.password.data.encode(), user.password.encode()):
            login_user(user)
            flash('Logged in successfully.')

            # check if the next page is set in the session by the @login_required decorator
            # if not set, it will default to '/'
            next_page = session.get('next', '/')
            # reset the next page to default '/'
            session['next'] = '/'
            return redirect(next_page)
        else:
            flash('Incorrect username/password!')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    # flash(str(session))
    return redirect('/')


@app.route('/signup2', methods=['GET', 'POST'])
def signup2():
    form = RegisterForm()
    if form.validate_on_submit():
        # check first if user already exists
        user = find_user(form.username.data)
        if not user:
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(form.password.data.encode(), salt)
            user = DBUser(username=form.username.data, email=form.email.data,
                          password=password.decode())
            db.session.add(user)
            db.session.commit()
            flash('Registered successfully.')
            return redirect('/login')
        else:
            flash('This username already exists, choose another one')

    return render_template('signup2.html', form=form)


@app.route('/protected')
@login_required
def protected():
    return render_template('protected.html')


@app.route('/non_protected')
def non_protected():
    return render_template('non_protected.html')


if __name__ == '__main__':
    app.run()
