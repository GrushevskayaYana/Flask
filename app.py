from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Secret key
app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"

# Initialize The Database
db = SQLAlchemy(app)
# Migrate
migrate = Migrate(app, db)


# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    favorite_color = db.Column(db.String(120))
    date_added = db.Column(db.DateTime, default=datetime.now())
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create A String
    def repr(self):
        return f'Name {self.name}'


# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField(
        'Password',
        validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):
    email = StringField("What's Your Email", validators=[DataRequired()])
    password_hash = PasswordField("What's Your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route("/user/<user_name>")
def user(user_name):
    return render_template(
        "user.html",
        user_name=user_name,
    )


@app.route('/')
def index():
    return render_template(
        'index.html',
        favorite_pizza=["Pepperoni", "Cheese", "Mushrooms", 41],
    )


# Invalid URL
@app.errorhandler(500)
def page_not_found(error):
    return render_template("500.html", error=error), 500


# Internal Server Error
@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html", error=error), 404


# Create Name Page
@app.route('/name', methods=['GET', 'POST'])
def _name():
    name = None
    form = NamerForm()
    # Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!")

    return render_template("name.html",
                           name=name,
                           form=form)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    if form.validate_on_submit():

        # Find user by email
        user_item = Users.query.filter_by(email=form.email.data).first()
        if user_item is None:
            # Hash the password!!!
            hashed_password = generate_password_hash(form.password_hash.data)
            # Create a new user
            user_item = Users(
                name=form.name.data,
                email=form.email.data,
                favorite_color=form.favorite_color.data,
                password_hash=hashed_password,
            )
            db.session.add(user_item)
            db.session.commit()

        name = form.name.data

        # Clear form fields
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash.data = ''

        flash("User Added Successfully!")

    # Users list from DB
    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",
                           form=form,
                           name=name,
                           our_users=our_users)


# Update Database Record
@app.route('/update/<int:user_id>', methods=['GET', 'POST'])
def update(user_id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(user_id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']
        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template(
                "update.html",
                form=form,
                name_to_update=name_to_update,
            )
        except Exception:
            flash("Error!  Looks like there was a problem...try again!")
            return render_template(
                "update.html",
                form=form,
                name_to_update=name_to_update,
            )
    else:
        return render_template(
            "update.html",
            form=form,
            name_to_update=name_to_update,
            user_id=user_id,
        )


@app.route('/delete/<int:user_id>')
def delete(user_id):
    """User deletion"""

    name = None
    form = UserForm()

    # Users object
    user_item = Users.query.get_or_404(user_id)

    # Users list
    our_users = Users.query.order_by(Users.date_added)

    try:
        db.session.delete(user_item)
        db.session.commit()
        flash("User Deleted Successfully!!")

        return render_template(
            "add_user.html",
            form=form,
            name=name,
            our_users=our_users,
        )

    except Exception:
        flash("Whoops! There was a problem deleting user, try again...")
        return render_template(
            "add_user.html",
            form=form,
            name=name,
            our_users=our_users,
        )


@app.route('/test_password', methods=['GET', 'POST'])
def test_password():
    email = None
    password = None
    user_item = None
    passed = None
    form = PasswordForm()

    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        # Clear the form
        form.email.data = ''
        form.password_hash.data = ''

        # Lookup User By Email Address
        user_item = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        if user_item:
            passed = check_password_hash(user_item.password_hash, password)

    return render_template(
        template_name_or_list="test_password.html",
        email=email,
        password=password,
        user_item=user_item,
        passed=passed,
        form=form,
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(
        debug=True,
        use_reloader=False,
        port=5001,
    )
