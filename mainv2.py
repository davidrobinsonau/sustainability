#!/usr/bin/env python3

# This script will run on a Raspberry Pi 5 using the newer GPIO chipset. It will monitor the state of the below buttons:
# 1. Button1 GPIO 19 - this will be used to start the Hydro Display
# 2. Button2 GPIO 26 - this will be used to start the Wind Display
# There are 2 other INPUTS that tell the program where the SUN is located on the display. These are:
# 1. Sun1 GPIO 20 - When this is LOW the Sun has set and is no longer visible
# 2. Sun2 GPIO 21 - When this is LOW the Sun is behind the hill or clouds and is only partially visible
# The OUTPUTS are:
# OUTPUT GPIO Houses - These are used to turn on the lights in the houses. The lights will be on when the GPIO is HIGH
# HOUSE1_GPIO = 1
# HOUSE2_GPIO = 7
# HOUSE3_GPIO = 8
# HOUSE4_GPIO = 25
# Output for the Motors to turn the Windmill and Waterwheel
# WATER_GPIO = 2
# WIND_GPIO = 3
# The display will demonstate the following:
# When the sun is up the lgihts in the houses will be on to show power is being generated from the solar panels
# When the sun is down the lights in the houses will be off
# When the sun is behind the hill or clouds, only some of the lights will be on to show only a small portion of the power is being generated
# When GPIO button 19 is pressed the Hydro motor will run and the lights will come on to show power is being generated from the waterwheel
# When GPIO button 26 is pressed the Wind motor will run and the lights will come on to show power is being generated from the windmill
# The motors will run for 10 seconds and then stop
#!/usr/bin/env python3

import gpiod
import time
import datetime
import sys
import os
import pygame
from pygame.locals import *
from pyvidplayer2 import Video

# GPIO setup using libgpiod
chip = gpiod.Chip("gpiochip0")  # Adjust if using a different gpiochip

# Define the lines for each GPIO pin used
LINES = {
    "sunset": chip.get_line(20),
    "sunbehind": chip.get_line(21),
    "button1": chip.get_line(19),
    "button2": chip.get_line(26),
    "house1": chip.get_line(1),
    "house2": chip.get_line(7),
    "house3": chip.get_line(8),
    "house4": chip.get_line(25),
    "water": chip.get_line(2),
    "wind": chip.get_line(3),
}

# Request the lines with appropriate settings
LINES["sunset"].request(
    consumer="sunset",
    type=gpiod.LINE_REQ_DIR_IN,
    flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
)
LINES["sunbehind"].request(
    consumer="sunbehind",
    type=gpiod.LINE_REQ_DIR_IN,
    flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
)
LINES["button1"].request(
    consumer="button1",
    type=gpiod.LINE_REQ_DIR_IN,
    flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
)
LINES["button2"].request(
    consumer="button2",
    type=gpiod.LINE_REQ_DIR_IN,
    flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,
)
for house in ["house1", "house2", "house3", "house4", "water", "wind"]:
    LINES[house].request(consumer=house, type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])

PI_HIGH = 1
PI_LOW = 0

# Global Game States
SOLAR = 0  # 0 = No Sun, 1 = LOW Sunlight, 2 = Full Sun
WATER = 0  # 0 = No Water, 1 = LOW Water, 2 = Full Water
WIND = 0  # 0 = No Wind, 1 = LOW Wind, 2 = Full Wind

# Pygame setup functions here...


def workflow_engine():
    global SOLAR, WATER, WIND, pygame_screen, pygame_images, pygame_sounds, water_started, wind_started

    if SOLAR == 0 and WATER == 0 and WIND == 0:
        # Turn all house lights OFF
        for house in ["house1", "house2", "house3", "house4"]:
            LINES[house].set_value(PI_LOW)
    elif SOLAR == 1 and WATER == 0 and WIND == 0:
        # Half Power - Turn 3 houses lights OFF
        LINES["house1"].set_value(PI_HIGH)
        for house in ["house2", "house3", "house4"]:
            LINES[house].set_value(PI_LOW)
    elif SOLAR == 2 and WATER == 0 and WIND == 0:
        # Full Sun - Turn all houses lights ON
        for house in ["house1", "house2", "house3", "house4"]:
            LINES[house].set_value(PI_HIGH)
    elif WATER == 1:
        if datetime.datetime.now() - water_started > datetime.timedelta(seconds=8):
            LINES["water"].set_value(PI_HIGH)
            WATER = 0
        else:
            # Hydro Power - Turn 2 houses lights ON
            for house in ["house1", "house2", "house3", "house4"]:
                LINES[house].set_value(PI_HIGH)
            LINES["water"].set_value(PI_LOW)
    elif WIND == 1:
        if datetime.datetime.now() - wind_started > datetime.timedelta(seconds=8):
            LINES["wind"].set_value(PI_HIGH)
            WIND = 0
        else:
            # Wind Power - Turn 1 house lights ON
            for house in ["house1", "house2", "house3", "house4"]:
                LINES[house].set_value(PI_HIGH)
            LINES["wind"].set_value(PI_LOW)


def sunrise_sunset_action():
    global SOLAR
    if LINES["sunset"].get_value() == PI_LOW:
        SOLAR = 0
    else:
        SOLAR = 2


def sunshade_action():
    global SOLAR
    if LINES["sunbehind"].get_value() == PI_LOW:
        SOLAR = 1
    else:
        SOLAR = 2


def hydro_action():
    global WATER, water_started
    WATER = 1
    water_started = datetime.datetime.now()


def wind_action():
    global WIND, wind_started
    WIND = 1
    wind_started = datetime.datetime.now()


def main():
    global SOLAR, WATER, WIND, pygame_screen, pygame_images, pygame_sounds

    # Get Pygame setup
    pygame_screen = setup_pygame()
    pygame_images = load_images()
    pygame_sounds = load_sounds()

    running = True
    last_time = datetime.datetime.now()

    while running:
        for event in pygame.event.get():
            if (
                event.type == pygame.QUIT
                or event.type == pygame.KEYDOWN
                and event.key == pygame.K_s
            ):
                running = False

        # Check button states
        if LINES["button1"].get_value() == PI_LOW:
            hydro_action()
        if LINES["button2"].get_value() == PI_LOW:
            wind_action()

        # Workflow engine to update display based on state
        if datetime.datetime.now() - last_time > datetime.timedelta(seconds=0.1):
            last_time = datetime.datetime.now()
            workflow_engine()

        pygame.time.wait(15)

    pygame.quit()
    sys.exit()


# Call main function
if __name__ == "__main__":
    main()
