from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Store which tier each image belongs to, default: "BUCKET"
image_data = {}  # filename -> tier

@app.route("/")
def index():
    # Organize images by tier
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
    return redirect(url_for("index"))

@app.route("/move", methods=["POST"])
def move():
    data = request.json
    image = data["image"]
    to_tier = data["to"]
    if image in image_data:
        image_data[image] = to_tier
    return {"status": "success"}

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
