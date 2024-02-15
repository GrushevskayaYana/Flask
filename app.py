from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template(
        "index.html",
    )


@app.route("/user/<user_name>")
def user(user_name):
    return render_template(
        "index.html",
    )


if __name__ == '__main__':
    app.run(
        debug=True,
        use_reloader=False,
        port=5001,
    )
