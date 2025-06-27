from flask import Flask, Response, request, jsonify
from picamera2 import Picamera2
import cv2
import time
import threading

app = Flask(__name__)

# Default settings
settings = {
    "width": 1280,
    "height": 720,
    "fps": 15
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
        ret, jpeg = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if ret:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        time.sleep(1 / settings["fps"])


@app.route('/video')
def video():
    return Response(mjpeg_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/set', methods=['POST'])
def set_params():
    global settings
    data = request.json
    changed = False
    for key in ["width", "height", "fps"]:
        if key in data and int(data[key]) != settings[key]:
            settings[key] = int(data[key])
            changed = True
    if changed:
        setup_camera()
    return jsonify({"status": "ok", "settings": settings})


@app.route('/status')
def status():
    return jsonify(settings)


if __name__ == "__main__":
    setup_camera()
    app.run(host="0.0.0.0", port=8081, debug=False)
