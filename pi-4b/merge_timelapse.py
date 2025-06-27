import os
import json
from datetime import datetime

CONFIG_PATH = "config.json"
OUTDIR = "static/video"
MOTIONDIR = "static/motion"
LOG_PATH = "merge_timelapse.log"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def log(msg):
    with open(LOG_PATH, "a") as f:
        now = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
        f.write(now + msg + "\n")

def main():
    cfg = load_config()
    TIMELAPSE_MINUTES = int(cfg.get("timelapse_minutes", 30))
    today = datetime.now().strftime("%Y-%m-%d")
    hourly_files = [f"{OUTDIR}/{today}_h{h:02d}.mp4" for h in range(24) if os.path.exists(f"{OUTDIR}/{today}_h{h:02d}.mp4")]
    if not hourly_files:
        log("Keine Stundenvideos zum Zusammenführen gefunden!")
        return

    with open("inputs.txt", "w") as f:
        for name in hourly_files:
            f.write(f"file '{os.path.abspath(name)}'\n")

    temp_full_day = f"{OUTDIR}/{today}_full.mp4"
    timelapse_path = f"{OUTDIR}/{today}.mp4"

    # Füge Videos zusammen
    os.system(f"ffmpeg -y -f concat -safe 0 -i inputs.txt -c copy {temp_full_day}")

    # Zeitraffer
    speed_factor = (24*3600) / (TIMELAPSE_MINUTES*60)
    os.system(f"ffmpeg -y -i {temp_full_day} -filter:v 'setpts=PTS/{speed_factor}' -an {timelapse_path}")

    log(f"Timelapse erstellt: {timelapse_path}")

    # Motion-Daten aggregieren
    all_events = []
    for h in range(24):
        mfile = f"{MOTIONDIR}/{today}_h{h:02d}.json"
        if os.path.exists(mfile):
            with open(mfile) as f:
                events = json.load(f)
                # Passe die Zeiten auf die Stunde an
                for ev in events:
                    ev["start"] = f"{h:02d}:" + ev["start"]
                    ev["end"] = f"{h:02d}:" + ev["end"]
                all_events.extend(events)
    # Schreibe Gesamt-Motion-JSON
    with open(f"{MOTIONDIR}/{today}.json", "w") as f:
        json.dump(all_events, f, indent=2)

    # Clean
    os.remove("inputs.txt")
    os.remove(temp_full_day)
    log("Motion-JSON zusammengefasst und Temp gelöscht.")

if __name__ == "__main__":
    main()
