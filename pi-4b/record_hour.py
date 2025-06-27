import cv2
import time
import json
import os
from datetime import datetime

CONFIG_PATH = "config.json"
LOG_PATH = "record_hour.log"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def log(msg):
    with open(LOG_PATH, "a") as f:
        now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        f.write(now + msg + "\n")

def main():
    cfg = load_config()
    VIDEO_URL = f"http://{cfg['pi_zero_ip']}:8081"
    WIDTH, HEIGHT = int(cfg.get("width", 1280)), int(cfg.get("height", 720))
    FPS = int(cfg.get("fps", 30))
    OUTDIR = "static/video"
    MOTIONDIR = "static/motion"
    today = datetime.now().strftime("%Y-%m-%d")
    hour = datetime.now().strftime("%H")
    os.makedirs(OUTDIR, exist_ok=True)
    os.makedirs(MOTIONDIR, exist_ok=True)
    videoname = f"{OUTDIR}/{today}_h{hour}.mp4"
    motionname = f"{MOTIONDIR}/{today}_h{hour}.json"

    log(f"Start Aufnahme {videoname} (Auflösung: {WIDTH}x{HEIGHT} @ {FPS}fps)")

    cap = cv2.VideoCapture(VIDEO_URL)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(videoname, fourcc, FPS, (WIDTH, HEIGHT))

    motion_events = []
    _, prev_frame = cap.read()
    if prev_frame is not None:
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)
    else:
        prev_gray = None

    start_time = time.time()
    frames = 0
    motion_active = False
    motion_start = None

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.5)
            continue
        out.write(frame)
        frames += 1
        if prev_gray is not None:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            delta = cv2.absdiff(prev_gray, gray)
            thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
            motion = cv2.countNonZero(thresh)
            if motion > 3000:
                if not motion_active:
                    motion_start = datetime.now().strftime("%H:%M:%S")
                    motion_active = True
            else:
                if motion_active:
                    motion_end = datetime.now().strftime("%H:%M:%S")
                    motion_events.append({"start": motion_start, "end": motion_end})
                    motion_active = False
            prev_gray = gray
        if time.time() - start_time > 3600:
            break

    cap.release()
    out.release()

    with open(motionname, "w") as f:
        json.dump(motion_events, f, indent=2)

    log(f"Stunde {hour} fertig. Frames: {frames}. Motion-Events: {len(motion_events)}.")

if __name__ == "__main__":
    main()
