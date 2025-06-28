from flask import Flask, Response, request, jsonify
from picamera2 import Picamera2
import cv2
import time
import threading
import numpy as np

app = Flask(__name__)

# Default settings
settings = {
    "width": 1920,
    "height": 1080,
    "fps": 30,
    "crop": [0, 0, 1920, 1080],  # [x, y, w, h]
    "rotate": 0  # 0, 90, 180, 270
}

picam = None
stream_lock = threading.Lock()


def setup_camera():
    global picam
    with stream_lock:
        if picam:
            picam.close()
        picam = Picamera2()
        picam.preview_configuration.main.size = (settings["width"], settings["height"])
        picam.preview_configuration.main.format = "RGB888"
        picam.preview_configuration.controls.FrameRate = settings["fps"]
        picam.configure("preview")
        picam.start()
        time.sleep(1)  # Warmup


def mjpeg_stream():
    global picam
    while True:
        with stream_lock:
            frame = picam.capture_array()
        # --- CROP ---
        x, y, w, h = settings["crop"]
        frame = frame[y:y + h, x:x + w]
        # --- ROTATE ---
        if settings["rotate"] == 90:
            frame = np.rot90(frame)
        elif settings["rotate"] == 180:
            frame = np.rot90(frame, 2)
        elif settings["rotate"] == 270:
            frame = np.rot90(frame, 3)
        # --- ENCODE ---
        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(1 / settings["fps"])


# Passe /set an, damit crop und rotate gesetzt werden können:
@app.route('/set', methods=['POST'])
def set_params():
    global settings
    data = request.json
    changed = False
    # width/height/fps wie gehabt
    for key in ["width", "height", "fps"]:
        if key in data and int(data[key]) != settings[key]:
            settings[key] = int(data[key])
            changed = True
    # crop
    if "crop" in data:
        # prüfe Format
        c = data["crop"]
        if isinstance(c, list) and len(c) == 4 and all(isinstance(i, int) for i in c):
            settings["crop"] = c
            changed = True
    # rotate
    if "rotate" in data:
        r = int(data["rotate"])
        if r in [0, 90, 180, 270]:
            settings["rotate"] = r
            changed = True
    if changed:
        setup_camera()
    return jsonify({"status": "ok", "settings": settings})


@app.route('/video')
def video():
    return Response(mjpeg_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/status')
def status():
    return jsonify(settings)


if __name__ == "__main__":
    setup_camera()
    app.run(host="0.0.0.0", port=8081, debug=False)
