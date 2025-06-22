# Pi Zero 2W Timelapse & Live-Stream

## Setup

1. Python-Umgebung vorbereiten:

pip3 install flask opencv-python

2. Webserver starten:

python3 app.py

3. Tägliche Aufnahme via Cron (siehe `crontab.txt`)

4. Live-Stream über Port 8081 (z.B. via libcamera + ffmpeg starten)

---

## Funktion

- 720p @ 30fps Videoaufnahme (24h)
- Geschwindigkeit auf ~30min komprimiert (Zeitraffer)
- Bewegungserkennung (rote Zeitstrahl-Markierungen)
- Webinterface mit Video + interaktivem Zeitstrahl + Live-Stream
