from flask import Flask, render_template, Blueprint

bp = Blueprint('weather', __name__, url_prefix='/weather')
app = Flask(__name__)
app.register_blueprint(bp)
@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=8000)