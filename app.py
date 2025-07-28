from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = "testing"

@app.route("/")
def simple_home():
    return "Hello from Render!"