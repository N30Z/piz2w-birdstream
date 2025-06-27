import subprocess
import threading
from flask import Flask, request, jsonify

app = Flask(__name__)

settings = {
    "width": 1280,
    "height": 720,
    "fps": 30
}
proc = None
lock = threading.Lock()

def start_stream():
    global proc
    stop_stream()
    cmd = [
        "libcamera-vid",
        "-t", "0",
        "--inline",
        "--width", str(settings["width"]),
        "--height", str(settings["height"]),
        "--framerate", str(settings["fps"]),
        "--nopreview",
        "-o", "-"
    ]
    ffmpeg_cmd = [
        "ffmpeg", "-re", "-i", "-",
        "-f", "mpegts",
        "-codec:v", "mpeg1video",
        "-b:v", "1000k",
        "-r", str(settings["fps"]),
        "http://0.0.0.0:8081"
    ]
    proc = subprocess.Popen(
        " ".join(cmd) + " | " + " ".join(ffmpeg_cmd),
        shell=True
    )

def stop_stream():
    global proc
    if proc and proc.poll() is None:
        proc.terminate()
        proc.wait()
    proc = None

@app.route("/set", methods=["POST"])
def set_stream():
    data = request.json
    changed = False
    with lock:
        for key in ["width", "height", "fps"]:
            if key in data and data[key] != settings[key]:
                settings[key] = data[key]
                changed = True
        if changed:
            start_stream()
    return jsonify({"status": "ok", "settings": settings})

@app.route("/status")
def status():
    return jsonify(settings)

if __name__ == "__main__":
    start_stream()
    app.run(host="0.0.0.0", port=5001)
