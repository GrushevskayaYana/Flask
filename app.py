from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

app.config['SECRET_KEY'] = "my super secret key that no one is supposed to know"


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name", validators=[DataRequired()])
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


if __name__ == '__main__':
    app.run(
        debug=True,
        use_reloader=False,
        port=5001,
    )
