from flask import Flask, render_template

app = Flask(__name__)


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
def page_not_found(e):
    return render_template("500.html"), 500


# Internal Server Error
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html", error=e), 404


if __name__ == '__main__':
    app.run(
        debug=True,
        use_reloader=False,
        port=5001,
    )
