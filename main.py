#!/usr/bin/env python3

# This script will control two HDMI displays connected to the Raspberry Pi 5. The left screen on HDMI 1 will be interactive with the user being able to control the power sources.
# The right screen on HDMI 2 will display information about the power source, ie Wind, Solar, Hydro, and Pumped Hydro.
#
# Pi Inputs from the sustainability display.
# Sun Location Sunrise & Sunset - High/Low
# Sun Location behind Hills or Clouds - High/Low
# Push Button for user to activate the Wind Turbines - On/Off
#
# Pi Outputs to the sustainability display.
# Wind Turbines - On/Off
# Houses LEDs - On/Off
# Pumped Hydro - On/Off
# Building Lights - On/Off
#

# Import Raspberry Pi Library
import RPi.GPIO as GPIO
import time
import datetime
import subprocess

import sys
import os

PI_HIGH = 1
PI_LOW = 0


def main():
    # Monitor GPIO20 - Sunset
    # GPIO21 - Sun behind clouds.

    # Set the GPIO mode
    GPIO.setmode(
        GPIO.BCM
    )  # The GPIO.BCM option means that you are referring to the pins by the "Broadcom SOC channel" number, these are the numbers after "GPIO".
    GPIO.setwarnings(False)

    # Set the GPIO pins to pull up
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Watch the PIN status every 1 second
    while True:
        # Check the status of the PIN
        if GPIO.input(20) == PI_LOW:
            print("Sunset")
        if GPIO.input(21) == PI_LOW:
            print("Sun behind Clouds")
        print("Waiting... 1 second.")
        time.sleep(1)


# call the main function
if __name__ == "__main__":
    main()
