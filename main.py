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

# Pygame movie module
from pyvidplayer2 import Video


PI_HIGH = 1
PI_LOW = 0

# Global Game States
SOLAR = 0  # 0 = No Sun, 1 = LOW Sunlight, 2 = Full Sun
WATER = 0  # 0 = No Water, 1 = LOW Water, 2 = Full Water
WIND = 0  # 0 = No Wind, 1 = LOW Wind, 2 = Full Wind

# INPUT GPIO
SUNSET_GPIO = 20
SUNBEHIND_GPIO = 21
BUTTON1_GPIO = 19
BUTTON2_GPIO = 26

# OUTPUT GPIO Houses
HOUSE1_GPIO = 1
HOUSE2_GPIO = 7
HOUSE3_GPIO = 8
HOUSE4_GPIO = 25

# Output for the Motors
WATER_GPIO = 2
WIND_GPIO = 3

# Has STATE Changed?
STATE_CHANGED = False


def load_images():
    # 1920x1080 Pixels for second Screen
    images = {
        "start": "images/renewableenergy01.png",
        "startbg": "images/renewableenergybg01.jpg",
        "sunshade": "images/renewableenergy07.png",
        "sunshadebg": "images/renewableenergybg07.jpg",
        "sunout": "images/renewableenergy03.png",
        "sunoutbg": "images/renewableenergybg03.jpg",
        "sunset": "images/dawn.png",
        "sunrise": "images/dawn.png",
        "leftscreen": "images/leftmonitor.jpeg",
    }
    loaded_images = {}
    for name, image_path in images.items():
        try:
            loaded_image = pygame.image.load(image_path)
            if loaded_image is None:
                print(f"Image {image_path} did not load correctly")
            else:
                print(f"Image {image_path}loaded successfully")
            loaded_images[name] = loaded_image
        except pygame.error:
            print(f"Failed to load image: {image_path}")
    return loaded_images


# Load up the movies to play on the screen
def load_movies():
    # 1920x1080 Pixels for Screen
    movies = {
        "hydro": "images/howdoeshydropowerwork.mp4",
    }
    loaded_movies = {}
    for name, movie_path in movies.items():
        try:
            loaded_movie = Video(movie_path)  # use_pygame_audio=True Failed.
            loaded_movie.mute()
            if loaded_movie is None:
                print(f"Movie {movie_path} did not load correctly")
            else:
                print(f"Movie {movie_path} loaded successfully")
            loaded_movies[name] = loaded_movie
        except Exception as e:
            print(f"Failed to load movie: {movie_path}")
            print(e)
    return loaded_movies


# Load up the sound files to play
def load_sounds():
    sounds = {
        "hydro": "sounds/waterfallmono.wav",
        "wind": "sounds/wind.wav",
    }
    loaded_sounds = {}
    for name, sound_path in sounds.items():
        try:
            loaded_sound = pygame.mixer.Sound(sound_path)
            # Set volume to 30%
            loaded_sound.set_volume(0.5)
            if loaded_sound is None:
                print(f"Sound {sound_path} did not load correctly")
            else:
                print(f"Sound {sound_path} loaded successfully")
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


# Setup PyGame for Full screen
def setup_pygame():
    if not FindDisplayDriver():
        print("Failed to initialise display driver")
        sys.exit(1)
    # Set the display to fullscreen
    pygame.init()

    # Get the dimensions of both displays
    info = pygame.display.Info()
    width = info.current_w
    height = info.current_h

    # Assume both displays are side by side horizontally
    total_width = (
        width * 2
    )  # adjust this if displays are not side by side or have different resolutions
    total_height = height

    # Set the display mode to cover both displays - pygame.FULLSCREEN refuses to work over two monitors on X11.
    screen = pygame.display.set_mode(
        (total_width, total_height), pygame.NOFRAME, display=0
    )

    # screen.display.set_caption("Sustainability Display")
    # screen.font.init()
    # Set the background color
    # screen = pygame.display.get_surface()
    # screen.fill((0, 0, 0))
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


def sunset_action(pygame_screen, pygame_images):
    pygame_screen.blit(pygame_images["startbg"], (1921, 0))
    pygame_screen.blit(pygame_images["start"], (1921, 0))


def sunout_action(pygame_screen, pygame_images):
    pygame_screen.blit(pygame_images["sunoutbg"], (1921, 0))
    pygame_screen.blit(pygame_images["sunout"], (1921, 0))


def sunshade_action(pygame_screen, pygame_images):
    pygame_screen.blit(pygame_images["sunshadebg"], (1921, 0))
    pygame_screen.blit(pygame_images["sunshade"], (1921, 0))


def main():
    # Access Global Variables
    global SOLAR
    global WATER
    global WIND
    global STATE_CHANGED

    # Monitor GPIO20 - Sunset
    # GPIO21 - Sun behind clouds.

    # Set the GPIO mode
    GPIO.setmode(
        GPIO.BCM
    )  # The GPIO.BCM option means that you are referring to the pins by the "Broadcom SOC channel" number, these are the numbers after "GPIO".
    GPIO.setwarnings(False)

    # Set the Line Sensor GPIO pins to pull up
    GPIO.setup(SUNSET_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SUNBEHIND_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Set the Relay for Motors GPIO Pins to Output and set to HIGH
    GPIO.setup(WATER_GPIO, GPIO.OUT, initial=GPIO.HIGH)  # Water Turbine
    GPIO.setup(3, GPIO.OUT, initial=GPIO.HIGH)  # Wind Turbine
    # Set GPIO 19 and 26 to be an input for the 2 buttons
    GPIO.setup(BUTTON1_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON2_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    # Set GPIO 1,7,8,25 to be outputs for the LEDS on the houses
    GPIO.setup(HOUSE1_GPIO, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(HOUSE2_GPIO, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(HOUSE3_GPIO, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(HOUSE4_GPIO, GPIO.OUT, initial=GPIO.LOW)
    # Get Pygame setup
    pygame_screen = setup_pygame()
    # Load the Images
    pygame_images = load_images()
    # Load the Movies
    pygame_movies = load_movies()
    # Load the Sounds
    pygame_sounds = load_sounds()
    # Load the left screen image and display on the left side of the screen
    pygame_screen.blit(pygame_images["leftscreen"], (0, 0))
    # Play the movie on the left screen and keep to 1920x1080
    # Get the movie

    # Play the video
    # for frame in pygame_movie.iter_frames():
    #    pygame_screen.blit(
    #        pygame.image.frombuffer(frame.tostring(), frame.size, "RGB"), (0, 0)
    #    )
    #    pygame.display.flip()
    # Load dawn start image and display on the far right side of the screen
    pygame_screen.blit(pygame_images["startbg"], (1921, 0))
    pygame_screen.blit(pygame_images["start"], (1921, 0))
    # Draw the text "Coming soon" on the screen
    # draw_text(pygame_screen, "Coming soon", 100, 100)
    # draw_text(pygame_screen, "Sustainability Display", 100, 300)
    # draw_text(pygame_screen, "Push Yellow Button for Hydro Power", 2000, 140)
    # draw_text(pygame_screen, "Push Red Button for Wind Power", 2000, 600)
    # Display the screen resolution on the display for debugging
    # draw_text(pygame_screen, str(get_screen_resolution()), 200, 200)

    pygame.display.flip()
    pygame_movie = pygame_movies["hydro"]
    # Set screen size to full screen
    pygame_movie.change_resolution(1080)

    # pygame.time.wait(16)  # around 60 fps
    # Watch the PIN status every 1 second
    running = True

    # Record a timer for th Pi Output check, as we only want to run that loop every 0.5 seconds
    last_time = datetime.datetime.now()
    water_started = datetime.datetime.now()
    wind_started = datetime.datetime.now()
    while running:
        if pygame_movie.active == True:
            if pygame_movie.draw(pygame_screen, (0, 0), force_draw=False):
                pygame.display.update()
        # if pygame_movie.active == False:
        # pygame_movie.restart()
        # Check to see if the time is greater than 0.5 seconds as we only check the Pi Outputs every 0.5 seconds to keep any video happy.
        if datetime.datetime.now() - last_time > datetime.timedelta(seconds=0.5):
            last_time = datetime.datetime.now()
            # Check the status of the PIN
            if GPIO.input(SUNSET_GPIO) == PI_LOW:
                # print("Sunset")
                # Set all the houses to LOW
                SOLAR = 0
                sunset_action(pygame_screen, pygame_images)
            elif GPIO.input(SUNBEHIND_GPIO) == PI_LOW:
                # print("Sun behind Clouds or Hill")
                SOLAR = 1
                sunshade_action(pygame_screen, pygame_images)
            else:
                # print("Sunrise")
                # Set all the houses to HIGH
                SOLAR = 2
                sunout_action(pygame_screen, pygame_images)

            if GPIO.input(BUTTON1_GPIO) == PI_LOW:
                # print("Button 1 Pressed")
                # Set the Relay for Water Motors GPIO Pins to LOW
                GPIO.output(WATER_GPIO, GPIO.LOW)
                # Sleep for 5 seconds to simulate the water turbines spinning up
                # time.sleep(5)
                WATER = 2
                # Set the time to now for the water started
                water_started = datetime.datetime.now()
                # Start Playing the video if not already playing
                if pygame_movie.active == False:
                    pygame_movie.play()
                # Start playing Hydro Water sounds from the beginning
                pygame_sounds["hydro"].play()
            else:
                # If the button is not pressed, check to see if the water has been running for 10 seconds
                # If it has, stop the water
                if WATER == 2:
                    # Check to see if the water has been running for 10 seconds
                    if datetime.datetime.now() - water_started > datetime.timedelta(
                        seconds=10
                    ):
                        # Set the Relay for Water Motors GPIO Pins to HIGH
                        GPIO.output(WATER_GPIO, GPIO.HIGH)
                        WATER = 0
                        # Stop playing the Audio and rewind
                        pygame_sounds["hydro"].stop()

            if GPIO.input(BUTTON2_GPIO) == PI_LOW:
                # print("Button 2 Pressed")
                # Set the Relay for Wind Motors GPIO Pins to LOW
                GPIO.output(WIND_GPIO, GPIO.LOW)
                # Sleep for 5 seconds to simulate the wind turbines spinning up
                # time.sleep(5)
                WIND = 2
                # Set the time to now for the wind started
                wind_started = datetime.datetime.now()
                # Start playing Wind sounds from the beginning
                pygame_sounds["wind"].play()
            else:
                # If the button is not pressed, check to see if the wind has been running for 10 seconds
                # If it has, stop the wind
                if WIND == 2:
                    # Check to see if the wind has been running for 10 seconds
                    if datetime.datetime.now() - wind_started > datetime.timedelta(
                        seconds=10
                    ):
                        # Set the Relay for Wind Motors GPIO Pins to HIGH
                        GPIO.output(WIND_GPIO, GPIO.HIGH)
                        WIND = 0
                        # Stop playing the Audio and rewind
                        pygame_sounds["wind"].stop()

            # Display Houses Lights based on SOLAR, Hydro, and Wind power.
            # Full Power
            if SOLAR == 0 and WATER == 0 and WIND == 0:
                # print("No power - Turn all houses lights OFF")
                GPIO.output(HOUSE1_GPIO, GPIO.LOW)
                GPIO.output(HOUSE2_GPIO, GPIO.LOW)
                GPIO.output(HOUSE3_GPIO, GPIO.LOW)
                GPIO.output(HOUSE4_GPIO, GPIO.LOW)
            elif WATER > 0 or WIND > 0:
                # print("We have Wind or Water power - Turn all houses lights ON")
                GPIO.output(HOUSE1_GPIO, GPIO.HIGH)
                GPIO.output(HOUSE2_GPIO, GPIO.HIGH)
                GPIO.output(HOUSE3_GPIO, GPIO.HIGH)
                GPIO.output(HOUSE4_GPIO, GPIO.HIGH)
            elif SOLAR == 1:
                # print("Half Power - Turn 3 houses lights OFF")
                GPIO.output(HOUSE1_GPIO, GPIO.HIGH)
                GPIO.output(HOUSE2_GPIO, GPIO.LOW)
                GPIO.output(HOUSE3_GPIO, GPIO.LOW)
                GPIO.output(HOUSE4_GPIO, GPIO.LOW)
            elif SOLAR == 2:
                # print("Full Power - Turn all houses lights ON")
                GPIO.output(HOUSE1_GPIO, GPIO.HIGH)
                GPIO.output(HOUSE2_GPIO, GPIO.HIGH)
                GPIO.output(HOUSE3_GPIO, GPIO.HIGH)
                GPIO.output(HOUSE4_GPIO, GPIO.HIGH)
            else:
                print("Ummmm")
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
        # print("Waiting... 1 second.")
        # time.sleep(0.1)
        pygame.time.wait(15)  # around 60 fps
    # Quit Pygame
    pygame_movie.stop()
    pygame.quit()
    sys.exit()


# call the main function
if __name__ == "__main__":
    main()
