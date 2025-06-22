import cv2
import numpy as np
import datetime
import os
import json
import subprocess

# Config
WIDTH, HEIGHT = 1280, 720
FPS = 30
VIDEO_DIR = "static/video"
MOTION_DIR = "static/motion"
DAILY_DURATION_SEC = 24 * 3600  # 24 Stunden

os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(MOTION_DIR, exist_ok=True)

def get_today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def main():
    today = get_today_str()
    video_temp = os.path.join(VIDEO_DIR, f"{today}_temp.mp4")
    video_out = os.path.join(VIDEO_DIR, f"{today}.mp4")
    motion_json = os.path.join(MOTION_DIR, f"{today}.json")

    # Video Capture (E-RS012 Kamera, evtl. anpassen je nach Treiber)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_temp, fourcc, FPS, (WIDTH, HEIGHT))

    ret, frame1 = cap.read()
    ret, frame2 = cap.read()

    motion_events = []
    motion_start = None

    start_time = datetime.datetime.now()

    while (datetime.datetime.now() - start_time).total_seconds() < DAILY_DURATION_SEC:
        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        motion = False
        for contour in contours:
            if cv2.contourArea(contour) < 500:
                continue
            motion = True
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame1, (x,y), (x+w, y+h), (0,255,0), 2)

        now = datetime.datetime.now()

        if motion and motion_start is None:
            motion_start = now.strftime("%H:%M:%S")
        if not motion and motion_start is not None:
            motion_end = now.strftime("%H:%M:%S")
            motion_events.append({"start": motion_start, "end": motion_end})
            motion_start = None

        out.write(frame1)

        frame1 = frame2
        ret, frame2 = cap.read()
        if not ret:
            break

    if motion_start is not None:
        motion_end = datetime.datetime.now().strftime("%H:%M:%S")
        motion_events.append({"start": motion_start, "end": motion_end})

    cap.release()
    out.release()

    # Geschwindigkeit erhöhen (24h → 30min ~48x Speedup)
    speed_factor = DAILY_DURATION_SEC / 1800  # 1800s = 30min
    subprocess.run([
        "ffmpeg", "-y", "-i", video_temp,
        "-filter:v", f"setpts=PTS/{speed_factor}",
        "-c:v", "libx264", "-preset", "fast", "-r", "30",
        video_out
    ])

    os.remove(video_temp)

    with open(motion_json, "w") as f:
        json.dump(motion_events, f)

if __name__ == "__main__":
    main()
