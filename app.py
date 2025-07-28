from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["SECRET_KEY"] = "testing"  
socketio = SocketIO(app)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

room_data = {}  

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code = request.form["room_code"]
        if not code.isdigit() or len(code) != 4:
            return render_template("join.html", error="Enter a 4-digit code.")
        
        if code not in room_data:
            room_data[code] = {}
            os.makedirs(os.path.join(UPLOAD_FOLDER, code), exist_ok=True)

        return redirect(url_for("room", code=code))
    
    return render_template("join.html")

@app.route("/room/<code>")
def room(code):
    if code not in room_data:
        return "Room not found", 404

    tiers = {tier: [] for tier in ["BUCKET", "S", "A", "B", "C", "D"]}
    for img, tier in room_data[code].items():
        tiers[tier].append(img)

    return render_template("index.html", code=code, tiers=tiers)

@app.route("/room/<code>/upload", methods=["POST"])
def upload(code):
    if code not in room_data:
        return "Room not found", 404

    files = request.files.getlist("image")
    room_path = os.path.join(UPLOAD_FOLDER, code)

    for file in files:
        filename = secure_filename(file.filename)
        save_path = os.path.join(room_path, filename)
        file.save(save_path)
        room_data[code][filename] = "BUCKET"
        
        socketio.emit("new_image", {"image": filename, "tier": "BUCKET"}, room=code)

    return redirect(url_for("room", code=code))

@app.route("/room/<code>/move", methods=["POST"])
def move(code):
    if code not in room_data:
        return {"status": "error", "message": "Room not found"}, 404

    data = request.json
    image = data["image"]
    to_tier = data["to"]

    if image in room_data[code]:
        room_data[code][image] = to_tier
        socketio.emit("image_moved", {"image": image, "to_tier": to_tier}, room=code)

    return {"status": "success"}

@socketio.on("join")
def on_join(data):
    room_code = data["room"]
    join_room(room_code)
    print(f"Client joined room: {room_code}")
    emit("status", {"msg": f"You have joined room {room_code}."})

@socketio.on("leave")
def on_leave(data):
    room_code = data["room"]
    leave_room(room_code)
    print(f"Client left room: {room_code}")
    emit("status", {"msg": f"You have left room {room_code}."})

# if __name__ == "__main__":
#     socketio.run(host="0.0.0.0", port=5000)
    # socketio.run(app, port=port, debug=True, use_reloader=False)