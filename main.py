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

# Import Pygame Library
import pygame
from pygame.locals import *


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

    # Set the Line Sensor GPIO pins to pull up
    GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Set the Relay for Motors GPIO Pins to Output and set to HIGH
    GPIO.setup(2, GPIO.OUT, initial=GPIO.HIGH)  # Water Turbine
    GPIO.setup(3, GPIO.OUT, initial=GPIO.HIGH)  # Wind Turbine
    # Set GPIO 19 and 26 to be an input for the 2 buttons
    GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Set GPIO 1,7,8,25 to be outputs for the LEDS on the houses
    GPIO.setup(1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(7, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(25, GPIO.OUT, initial=GPIO.LOW)

    # Watch the PIN status every 1 second
    while True:
        # Check the status of the PIN
        if GPIO.input(20) == PI_LOW:
            print("Sunset")
            # Set all the houses to LOW
            GPIO.output(1, GPIO.LOW)
            GPIO.output(7, GPIO.LOW)
            GPIO.output(8, GPIO.LOW)
            GPIO.output(25, GPIO.LOW)
        elif GPIO.input(21) == PI_LOW:
            print("Sun behind Clouds or Hill")
            # Set 2 houses to LOW
            GPIO.output(8, GPIO.LOW)
            GPIO.output(25, GPIO.LOW)
        else:
            print("Sunrise - ALL Houses Lights ON")
            # Set all the houses to HIGH
            GPIO.output(1, GPIO.HIGH)
            GPIO.output(7, GPIO.HIGH)
            GPIO.output(8, GPIO.HIGH)
            GPIO.output(25, GPIO.HIGH)
        if GPIO.input(19) == PI_LOW:
            print("Button 1 Pressed")
            # Set the Relay for Water Motors GPIO Pins to LOW
            GPIO.output(2, GPIO.LOW)
        else:
            # Set the Relay for Water Motors GPIO Pins to HIGH
            GPIO.output(2, GPIO.HIGH)
        if GPIO.input(26) == PI_LOW:
            print("Button 2 Pressed")
            # Set the Relay for Wind Motors GPIO Pins to LOW
            GPIO.output(3, GPIO.LOW)
        else:
            # Set the Relay for Wind Motors GPIO Pins to HIGH
            GPIO.output(3, GPIO.HIGH)
        print("Waiting... 1 second.")
        time.sleep(1)


# call the main function
if __name__ == "__main__":
    main()
