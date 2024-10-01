#!/bin/sh

# This script will start the Python script and restart it if it crashes
# /home/hive/Workspace/sustainability/main.py
cd /home/hive/Workspace/sustainability
# Move the log file so that we don't fill up all space.
mv /home/hive/Workspace/sustainability/log.txt /home/hive/Workspace/sustainability/log_last_reboot.txt
while true; do
    /home/hive/Workspace/sustainability/maingpiozero.py >> /home/hive/Workspace/sustainability/log.txt 2>&1
    sleep 30
done

