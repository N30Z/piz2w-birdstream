from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)
VIDEO_DIR = "static/video"
MOTION_DIR = "static/motion"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video/<filename>")
def video(filename):
    return send_from_directory(VIDEO_DIR, filename)

@app.route("/motion/<filename>")
def motion(filename):
    return send_from_directory(MOTION_DIR, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
