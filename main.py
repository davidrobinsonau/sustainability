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

# Game States
SOLAR = 0  # 0 = No Sun, 1 = LOW Sunlight, 2 = Full Sun
WATER = 0  # 0 = No Water, 1 = LOW Water, 2 = Full Water
WIND = 0  # 0 = No Wind, 1 = LOW Wind, 2 = Full Wind


def FindDisplayDriver():
    for driver in ["fbcon", "directfb", "svgalib", "x11"]:
        if not os.getenv("SDL_VIDEODRIVER"):
            os.putenv("SDL_VIDEODRIVER", driver)
        try:
            pygame.display.init()
            return True
        except pygame.error:
            pass
    return False


# Setup PyGame for Full screen
def setup_pygame():
    if not FindDisplayDriver():
        print("Failed to initialise display driver")
        sys.exit(1)
    # Set the display to fullscreen
    pygame.init()
    # pygame.mouse.set_visible(False)
    # Get the display information
    # info = pygame.display.Info()

    # Calculate the combined resolution (example for two 1920x1080 monitors side by side)
    # combined_width = info.current_w
    # combined_height = info.current_h

    # Set the display mode to the combined resolution in fullscreen mode
    # screen = pygame.display.set_mode(
    #    (combined_width, combined_height), pygame.FULLSCREEN
    # )
    #
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

    # screen.display.set_caption("Sustainability Display")
    # screen.font.init()
    # Set the background color
    # screen = pygame.display.get_surface()
    screen.fill((0, 0, 0))
    pygame.display.flip()
    return screen


# Function to draw text on the screen in large font
def draw_text(screen, text, x, y):
    font = pygame.font.Font(None, 96)
    text = font.render(text, 1, (255, 255, 255))
    screen.blit(text, (x, y))
    pygame.display.flip()


# Function to get the screen resolution using Pygame
def get_screen_resolution():
    # Get the screen resolution
    screen = pygame.display.Info()
    return (screen.current_w, screen.current_h)


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
    # Get Pygame setup
    pygame_screen = setup_pygame()
    # Draw the text "Coming soon" on the screen
    draw_text(pygame_screen, "Coming soon", 100, 100)
    # Display the screen resolution on the display for debugging
    draw_text(pygame_screen, str(get_screen_resolution()), 200, 200)

    # Watch the PIN status every 1 second
    while True:
        # Check the status of the PIN
        if GPIO.input(20) == PI_LOW:
            print("Sunset")
            # Set all the houses to LOW
            SOLAR = 0
        elif GPIO.input(21) == PI_LOW:
            print("Sun behind Clouds or Hill")
            SOLAR = 1
        else:
            print("Sunrise")
            # Set all the houses to HIGH
            SOLAR = 2
        if GPIO.input(19) == PI_LOW:
            print("Button 1 Pressed")
            # Set the Relay for Water Motors GPIO Pins to LOW
            GPIO.output(2, GPIO.LOW)
            WATER = 2
            # If
        else:
            # Set the Relay for Water Motors GPIO Pins to HIGH
            GPIO.output(2, GPIO.HIGH)
            WATER = 0
        if GPIO.input(26) == PI_LOW:
            print("Button 2 Pressed")
            # Set the Relay for Wind Motors GPIO Pins to LOW
            GPIO.output(3, GPIO.LOW)
            WIND = 2
        else:
            # Set the Relay for Wind Motors GPIO Pins to HIGH
            GPIO.output(3, GPIO.HIGH)
            WIND = 0

        # Display Houses Lights based on SOLAR, Hydro, and Wind power.
        # Full Power
        if SOLAR == 0 and WATER == 0 and WIND == 0:
            print("No power - Turn all houses lights OFF")
            GPIO.output(1, GPIO.LOW)
            GPIO.output(7, GPIO.LOW)
            GPIO.output(8, GPIO.LOW)
            GPIO.output(25, GPIO.LOW)
        elif WATER > 0 or WIND > 0:
            print("We have Wind or Water power - Turn all houses lights ON")
            GPIO.output(1, GPIO.HIGH)
            GPIO.output(7, GPIO.HIGH)
            GPIO.output(8, GPIO.HIGH)
            GPIO.output(25, GPIO.HIGH)
        elif SOLAR == 1:
            print("Half Power - Turn 3 houses lights OFF")
            GPIO.output(1, GPIO.HIGH)
            GPIO.output(7, GPIO.LOW)
            GPIO.output(8, GPIO.LOW)
            GPIO.output(25, GPIO.LOW)
        elif SOLAR == 2:
            print("Full Power - Turn all houses lights ON")
            GPIO.output(1, GPIO.HIGH)
            GPIO.output(7, GPIO.HIGH)
            GPIO.output(8, GPIO.HIGH)
            GPIO.output(25, GPIO.HIGH)
        else:
            print("Ummmm")
        print("Waiting... 1 second.")
        time.sleep(1)


# call the main function
if __name__ == "__main__":
    main()
