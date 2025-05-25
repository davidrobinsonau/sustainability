#!/usr/bin/env python3

import time
import datetime
import sys
import os
import threading
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
SUNSET_BUTTON = Button(20, pull_up=True, bounce_time=0.5)
SUNBEHIND_BUTTON = Button(21, pull_up=True, bounce_time=0.5)
BUTTON1 = Button(19)
BUTTON2 = Button(26)
LEFT_STOP_SENSOR = Button(12, pull_up=True, bounce_time=0.5)
RIGHT_STOP_SENSOR = Button(16, pull_up=True, bounce_time=0.5)

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

# Shared variables for thread control
stop_event = threading.Event()
video_playing = False


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
        "turnright": "images/turnleft.png",
        "turnleft": "images/turnright.png",
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
        "night": "sounds/swamp.wav",
    }
    loaded_sounds = {}
    pygame.mixer.init(buffer=4096)  # Increase buffer size if needed
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


# Function to draw text on the screen in large font
def draw_text(screen, text, x, y):
    font = pygame.font.Font(None, 96)
    text = font.render(text, 1, (255, 255, 255))
    screen.blit(text, (x, y))
    # pygame.display.flip()


# Draw Turn Left and Turn Right images in the center of the screen
def draw_turn_left_image():
    global pygame_screen, pygame_images
    turn_left_image = pygame_images["turnleft"]
    turn_left_rect = turn_left_image.get_rect(center=(1921 + 960, 540))
    pygame_screen.blit(turn_left_image, turn_left_rect)
    # pygame.display.flip()


def draw_turn_right_image():
    global pygame_screen, pygame_images
    turn_right_image = pygame_images["turnright"]
    turn_right_rect = turn_right_image.get_rect(center=(1921 + 960, 540))
    pygame_screen.blit(turn_right_image, turn_right_rect)
    # pygame.display.flip()


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
    elif SOLAR == 1 and WATER == 0 and WIND == 0:
        HOUSE1.on()
        HOUSE2.off()
        HOUSE3.off()
        HOUSE4.off()
        pygame_screen.blit(pygame_images["sunshadebg"], (1921, 0))
        pygame_screen.blit(pygame_images["sunshade"], (1921, 0))
    elif SOLAR == 2 and WATER == 0 and WIND == 0:
        HOUSE1.on()
        HOUSE2.on()
        HOUSE3.on()
        HOUSE4.on()
        pygame_screen.blit(pygame_images["sunoutbg"], (1921, 0))
        pygame_screen.blit(pygame_images["sunout"], (1921, 0))
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
            WIND_MOTOR.off()
            pygame_sounds["wind"].play()


def sunout_action():
    global SOLAR, stop_event
    SOLAR = 2
    stop_event.set()  # Signal the stop_event to stop any ongoing threads
    pygame_sounds["night"].stop()


def sunset_action():
    global SOLAR, pygame_screen, pygame_images, pygame_sounds, stop_event

    SOLAR = 0

    def play_night_sound():
        while not stop_event.is_set():
            print("Playing night sound...")
            pygame_sounds["night"].play()
            time.sleep(pygame_sounds["night"].get_length())

    if (
        not hasattr(sunset_action, "night_sound_thread")
        or not sunset_action.night_sound_thread.is_alive()
    ):
        print("Starting night sound thread...")
        stop_event.clear()
        sunset_action.night_sound_thread = threading.Thread(
            target=play_night_sound, daemon=True
        )
        sunset_action.night_sound_thread.start()
    else:
        print("Night sound thread is already running.")

    sys.stdout.flush()


def sunshade_action():
    global SOLAR
    SOLAR = 1


def hydro_action():
    global WATER, water_started, pygame_movie
    if pygame_movie.active == True:
        # Only restart the threat if the movie is more than 8 seconds in
        if pygame_movie.frame > 1000:
            pygame_movie.restart()  # Restart the movie from the beginning
    WATER = 1
    water_started = datetime.datetime.now()


def wind_action():
    global WIND, wind_started
    WIND = 1
    wind_started = datetime.datetime.now()


def main():
    global pygame_screen, pygame_images, pygame_sounds, pygame_movie

    pygame_screen = setup_pygame()
    pygame_images = load_images()
    pygame_sounds = load_sounds()
    pygame_movies = load_movies()
    pygame_movie = pygame_movies["hydro"]
    # if pygame_movie.active == False:
    # play_movie_thread(pygame_movie, pygame_screen, (0, 0))

    SUNSET_BUTTON.when_pressed = sunset_action
    SUNSET_BUTTON.when_released = sunout_action
    SUNBEHIND_BUTTON.when_pressed = sunshade_action
    SUNBEHIND_BUTTON.when_released = sunout_action
    BUTTON1.when_pressed = hydro_action
    BUTTON2.when_pressed = wind_action
    LEFT_STOP_SENSOR.when_pressed = draw_turn_left_image
    LEFT_STOP_SENSOR.when_released = lambda: print("Left Stop Sensor Released")
    RIGHT_STOP_SENSOR.when_pressed = draw_turn_right_image
    RIGHT_STOP_SENSOR.when_released = lambda: print("Right Stop Sensor Released")

    running = True
    debugOn = False
    last_time = datetime.datetime.now()

    while running:
        if datetime.datetime.now() - last_time > datetime.timedelta(seconds=0.1):
            last_time = datetime.datetime.now()
            workflow_engine()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    # Code to handle "h" key press event
                    # Hide the screen so that I can see the console
                    pygame.display.iconify()
                if event.key == pygame.K_f:
                    # Code to handle "f" key press event
                    # Hide the screen so that I can see the console
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_d:
                    # Code to handle "d" key press event
                    # Hide the screen so that I can see the console
                    debugOn = not debugOn
                if event.key == pygame.K_q:
                    # Code to handle "q" key press event
                    # Hide the screen so that I can see the console
                    running = False
                if event.key == pygame.K_s:
                    # Code to handle "s" key press event
                    # Stop playing the crickets sound.
                    pygame_sounds["night"].stop()

        if pygame_movie.active == True:
            pygame_movie.draw(pygame_screen, (0, 0), force_draw=False)

        if debugOn:
            draw_text(pygame_screen, "SOLAR: " + str(SOLAR), 2000, 10)
            draw_text(pygame_screen, "WATER: " + str(WATER), 2000, 100)
            draw_text(pygame_screen, "WIND: " + str(WIND), 2000, 200)

        pygame.display.update()
        time.sleep(0.01)  # Small delay to prevent CPU overuse
        # pygame.time.wait(15)
    pygame_movie.stop()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
