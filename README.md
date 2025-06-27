# Birdstream – Zwei-Pi-Lösung für Livestream & Zeitraffer

Pi Zero 2 W als Kamera-Streamer, Pi 4B als Webserver, Bewegungserkennung und Zeitraffer-Recorder

---

## Inhalt

- [Aufbau](#aufbau)
- [Installation Pi Zero 2 W (Streamer)](#installation-pi-zero-2w-streamer)
- [Installation Pi 4B (Webserver, Zeitraffer, Erkennung)](#installation-pi-4b-webserver-zeitraffer-erkennung)
- [Inbetriebnahme & Betrieb](#inbetriebnahme--betrieb)
- [Wichtige Hinweise](#wichtige-hinweise)

---

## Aufbau

```text
piz2w-birdstream/
├── pi-zero2w/
│   ├── virtualcam.py
│   ├── virtualcam.service
│   └── requirements.txt
└── pi-4b/
    ├── record_hour.py
    ├── merge_timelapse.py
    ├── watchdog_hourly.sh
    ├── config.json
    ├── static/
    │   ├── video/
    │   └── motion/
    └── (weitere Services/Web-Frontend falls gewünscht)
```

---

## Installation Pi Zero 2 W (Streamer)

1. **Vorbereitung:**
    ```bash
    sudo apt update
    sudo apt install python3-pip libcamera-apps ffmpeg
    ```
2. **Projekt kopieren:**
    ```bash
    cd ~
    git clone https://github.com/N30Z/piz2w-birdstream.git
    cd piz2w-birdstream/pi-zero2w
    ```
3. **Python-Abhängigkeiten installieren:**
    ```bash
    pip3 install -r requirements.txt
    ```
4. **Service einrichten und starten:**
    ```bash
    sudo cp virtualcam.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable virtualcam.service
    sudo systemctl start virtualcam.service
    ```
5. **Fertig!**
    - Der Stream läuft jetzt auf `http://<PiZero-IP>:8081`
    - API zur Steuerung auf `http://<PiZero-IP>:5001`

---

## Installation Pi 4B (Webserver, Zeitraffer, Erkennung)

1. **Vorbereitung:**
    ```bash
    sudo apt update
    sudo apt install python3-pip ffmpeg python3-opencv
    ```
2. **Projekt kopieren:**
    ```bash
    cd ~
    git clone https://github.com/N30Z/piz2w-birdstream.git
    cd piz2w-birdstream/pi-4b
    ```
3. **Python-Abhängigkeiten installieren:**
    ```bash
    pip3 install flask requests
    ```
4. **Statische Verzeichnisse anlegen:**
    ```bash
    mkdir -p static/video static/motion
    ```
5. **config.json anpassen:**  
    - Trage die **IP des Pi Zero 2 W** unter `pi_zero_ip` ein.
    - Stelle Auflösung, FPS, Zeitraffer-Minuten nach Wunsch ein.

6. **Cronjobs einrichten:**  
    ```bash
    crontab -e
    ```
    **Füge hinzu:**
    ```
    0 * * * * /home/captain/piz2w-birdstream/pi-4b/watchdog_hourly.sh
    10 0 * * * cd /home/captain/piz2w-birdstream/pi-4b && python3 merge_timelapse.py
    ```

7. **(Optional) Web-Interface/Service starten:**
    - Wenn vorhanden, analog zu den anderen Services (siehe web.service).

---

## Inbetriebnahme & Betrieb

- **Starte beide Pis neu**  
- Die Aufnahme beginnt stündlich automatisch auf dem Pi 4B (Cronjob)
- Täglich wird automatisch der Zeitraffer aus allen Stunden erstellt
- Motion-Erkennung und Logfiles werden automatisch geführt
- Auf dem Pi 4B kannst du alle Videos, Logs und Bewegungsdaten einsehen

---

## Wichtige Hinweise

- **Aufnahmen sind stündlich gespeichert:** Datenverlust maximal 1h bei Absturz
- **Konfiguration über `config.json` auf dem Pi 4B**
- **Livestream-Einstellungen (Auflösung/FPS) werden über das Web-Interface oder direkt per API gesetzt**
- **Bei Problemen immer zuerst die Logs prüfen!** (`record_hour.log`, `merge_timelapse.log`, etc.)
- **Stelle sicher, dass Uhrzeit und Zeitzone auf beiden Pis korrekt sind** (`timedatectl`)

---

**Fragen, Anpassungswünsche oder Support?**  
Kopiere diese README mit ins Repo, passe die Usernamen/Pfade an – fertig!

Wenn du noch ein extra Web-Frontend oder Monitoring willst, einfach melden!
