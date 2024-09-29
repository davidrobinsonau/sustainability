#!/usr/bin/env python3

import time
import datetime
import sys
import os
from gpiozero import Button, LED, OutputDevice
import pygame
from pygame.locals import *
from pyvidplayer2 import Video

# Constants
PI_HIGH = 1
PI_LOW = 0

# Global Game States
SOLAR = 0  # 0 = No Sun, 1 = LOW Sunlight, 2 = Full Sun
WATER = 0  # 0 = No Water, 1 = LOW Water, 2 = Full Water
WIND = 0  # 0 = No Wind, 1 = LOW Wind, 2 = Full Wind

# Define GPIO pins using gpiozero components
SUNSET_BUTTON = Button(20)
SUNBEHIND_BUTTON = Button(21)
BUTTON1 = Button(19)
BUTTON2 = Button(26)

# LEDs for houses
HOUSE1 = LED(1)
HOUSE2 = LED(7)
HOUSE3 = LED(8)
HOUSE4 = LED(25)

# Output devices for motors
WATER_MOTOR = OutputDevice(2, initial_value=True)  # Water Turbine motor
WIND_MOTOR = OutputDevice(3, initial_value=True)  # Wind Turbine motor

# Has STATE Changed?
STATE_CHANGED = False


def load_images():
    images = {
        "start": "images/renewableenergy01.png",
        "startbg": "images/renewableenergybg01.jpg",
        "sunshade": "images/renewableenergy07.png",
        "sunshadebg": "images/renewableenergybg07.jpg",
        "sunout": "images/renewableenergy03.png",
        "sunoutbg": "images/renewableenergybg03.jpg",
        "sunset": "images/renewableenergybg10.jpg",
        "sunsetcontrols": "images/renewableenergy09.png",
        "sunrise": "images/dawn.png",
        "leftscreen": "images/leftmonitor.jpeg",
        "hydro": "images/renewableenergy02.png",
        "hydrobg": "images/renewableenergybg08.jpg",
        "wind": "images/renewableenergy05.png",
        "windbg": "images/renewableenergybg05.jpg",
    }
    loaded_images = {}
    for name, image_path in images.items():
        try:
            loaded_image = pygame.image.load(image_path)
            if loaded_image is None:
                print(f"Image {image_path} did not load correctly")
            else:
                print(f"Image {image_path} loaded successfully")
            loaded_images[name] = loaded_image
        except pygame.error:
            print(f"Failed to load image: {image_path}")
    return loaded_images


def load_movies():
    movies = {
        "hydro": "images/howdoeshydropowerwork1080p.mp4",
    }
    loaded_movies = {}
    for name, movie_path in movies.items():
        try:
            loaded_movie = Video(movie_path)
            loaded_movie.mute()
            loaded_movies[name] = loaded_movie
        except Exception as e:
            print(f"Failed to load movie: {movie_path}")
            print(e)
    return loaded_movies


def load_sounds():
    sounds = {
        "hydro": "sounds/waterfallmono.wav",
        "wind": "sounds/wind.wav",
    }
    loaded_sounds = {}
    for name, sound_path in sounds.items():
        try:
            loaded_sound = pygame.mixer.Sound(sound_path)
            loaded_sound.set_volume(0.5)
            loaded_sounds[name] = loaded_sound
        except Exception as e:
            print(f"Failed to load sound: {sound_path}")
            print(e)
    return loaded_sounds


def FindDisplayDriver():
    # "x11" won't go full screen on a Raspberry Pi
    os.environ["SDL_VIDEO_WINDOW_POS"] = "0,0"
    for driver in ["kmsdrm", "fbcon", "directfb", "svgalib", "x11"]:
        if not os.getenv("SDL_VIDEODRIVER"):
            os.putenv("SDL_VIDEODRIVER", driver)
        try:
            pygame.display.init()
            return True
        except pygame.error:
            pass
    return False


def setup_pygame():
    if not FindDisplayDriver():
        print("Failed to initialise display driver")
        sys.exit(1)
    # Set the display to fullscreen
    pygame.init()
    info = pygame.display.Info()
    width = info.current_w
    height = info.current_h
    total_width = width * 2
    total_height = height
    screen = pygame.display.set_mode(
        (total_width, total_height), pygame.NOFRAME, display=0
    )
    pygame.display.flip()
    return screen


water_started = datetime.datetime.now()
wind_started = datetime.datetime.now()


def workflow_engine():
    global SOLAR, WATER, WIND, pygame_screen, pygame_images, pygame_sounds, water_started, wind_started

    if SOLAR == 0 and WATER == 0 and WIND == 0:
        HOUSE1.off()
        HOUSE2.off()
        HOUSE3.off()
        HOUSE4.off()
        pygame_screen.blit(pygame_images["sunset"], (1921, 0))
        pygame_screen.blit(pygame_images["sunsetcontrols"], (1921, 0))
        pygame.display.update()
    elif SOLAR == 1 and WATER == 0 and WIND == 0:
        HOUSE1.on()
        HOUSE2.off()
        HOUSE3.off()
        HOUSE4.off()
        pygame_screen.blit(pygame_images["sunshadebg"], (1921, 0))
        pygame_screen.blit(pygame_images["sunshade"], (1921, 0))
        pygame.display.update()
    elif SOLAR == 2 and WATER == 0 and WIND == 0:
        HOUSE1.on()
        HOUSE2.on()
        HOUSE3.on()
        HOUSE4.on()
        pygame_screen.blit(pygame_images["sunoutbg"], (1921, 0))
        pygame_screen.blit(pygame_images["sunout"], (1921, 0))
        pygame.display.update()
    elif WATER == 1:
        if datetime.datetime.now() - water_started > datetime.timedelta(seconds=8):
            WATER_MOTOR.on()
            WATER = 0
            pygame_sounds["hydro"].stop()
        else:
            HOUSE1.on()
            HOUSE2.on()
            HOUSE3.on()
            HOUSE4.on()
            pygame_screen.blit(pygame_images["hydrobg"], (1921, 0))
            pygame_screen.blit(pygame_images["hydro"], (1921, 0))
            pygame.display.update()
            WATER_MOTOR.off()
            pygame_sounds["hydro"].play()
    elif WIND == 1:
        if datetime.datetime.now() - wind_started > datetime.timedelta(seconds=8):
            WIND_MOTOR.on()
            WIND = 0
            pygame_sounds["wind"].stop()
        else:
            HOUSE1.on()
            HOUSE2.on()
            HOUSE3.on()
            HOUSE4.on()
            pygame_screen.blit(pygame_images["windbg"], (1921, 0))
            pygame_screen.blit(pygame_images["wind"], (1921, 0))
            pygame.display.update()
            WIND_MOTOR.off()
            pygame_sounds["wind"].play()


def sunrise_sunset_action():
    global SOLAR
    SOLAR = 0 if SUNSET_BUTTON.is_pressed else 2


def sunshade_action():
    global SOLAR
    SOLAR = 1 if SUNBEHIND_BUTTON.is_pressed else 2


def hydro_action():
    global WATER, water_started
    WATER = 1
    water_started = datetime.datetime.now()


def wind_action():
    global WIND, wind_started
    WIND = 1
    wind_started = datetime.datetime.now()


def main():
    global pygame_screen, pygame_images, pygame_sounds

    pygame_screen = setup_pygame()
    pygame_images = load_images()
    pygame_sounds = load_sounds()

    SUNSET_BUTTON.when_pressed = sunrise_sunset_action
    SUNBEHIND_BUTTON.when_pressed = sunshade_action
    BUTTON1.when_pressed = hydro_action
    BUTTON2.when_pressed = wind_action

    running = True
    last_time = datetime.datetime.now()

    while running:
        if datetime.datetime.now() - last_time > datetime.timedelta(seconds=0.1):
            last_time = datetime.datetime.now()
            workflow_engine()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False

        pygame.time.wait(15)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
