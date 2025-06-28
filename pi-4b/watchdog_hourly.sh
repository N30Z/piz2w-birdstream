#!/bin/bash
cd /home/captain/piz2w-birdstream/pi-4b || { echo "Directory Failure"; exit 1; }
LOG="watchdog_hourly.log"
PGREP=$(pgrep -f record_hour.py)
if [ -z "$PGREP" ]; then
  echo "$(date) Start record_hour.py" >> $LOG
  nohup python3 record_hour.py >> $LOG 2>&1 &
else
  echo "$(date) Läuft schon, skip." >> $LOG
fi
