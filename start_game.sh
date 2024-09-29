#!/bin/sh

# This script will start the Python script and restart it if it crashes
# /home/hive/Workspace/sustainability/main.py
cd /home/hive/Workspace/sustainability
while true; do
    /home/hive/Workspace/sustainability/maingpiozero.py
    sleep 30
done

