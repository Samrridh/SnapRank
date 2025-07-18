from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


image_data = {}

@app.route("/")
def index():
    tiers = {"BUCKET": [], "S": [], "A": [], "B": [], "C": [], "D": []}
    for img, tier in image_data.items():
        tiers[tier].append(img)
    return render_template("index.html", tiers=tiers)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["image"]
    if file:
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        image_data[filename] = "BUCKET"
        emit("image_added", {"image": filename, "tier": "BUCKET"}, namespace='/', broadcast=True)
    return redirect(url_for("index"))

@socketio.on("move_image")
def handle_move_image(data):
    image = data["image"]
    to_tier = data["to"]
    if image in image_data:
        image_data[image] = to_tier
        emit("update_image", {"image": image, "to": to_tier}, broadcast=True)

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)

