#!/bin/bash

set -e

PROJECT_DIR="$HOME/piz2w-birdstream"

echo "==> System updaten..."
sudo apt update && sudo apt upgrade -y

echo "==> Python3 und pip installieren..."
sudo apt install -y python3 python3-pip

echo "==> Benötigte Python-Pakete installieren..."
pip3 install --upgrade pip
pip3 install flask opencv-python

echo "==> Projektverzeichnis: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"

echo "Repo klonen"
git clone git@github.com:N30Z/piz2w-birdstream.git "$PROJECT_DIR"

echo "==> Cronjob einrichten..."
CRON_CMD="python3 $PROJECT_DIR/record_and_detect.py"
(crontab -l 2>/dev/null | grep -v "$CRON_CMD" || true; echo "0 0 * * * $CRON_CMD") | crontab -

echo "==> Webserver starten (Flask im Hintergrund)..."
nohup python3 "$PROJECT_DIR/app.py" > "$PROJECT_DIR/webserver.log" 2>&1 &

echo "==> Setup fertig! Webserver läuft im Hintergrund."
echo "Starte Cronjob mit: crontab -l"
