# sustainability
Hive Display of Wind, Hydro, Hydro Battery, and Solar

# Next Steps
https://github.com/anrayliu/pyvidplayer2/blob/main/examples/video_demo.py

For Andrew:
Add solar panels to houses. As there is no solar panels in display.

# Software Language
Python 3
PyGame
PyAudio
sudo apt install python3-opencv
libportaudio2
https://github.com/anrayliu/pyvidplayer2/tree/main for Video Playing within PyGame

TODO When Nothing Happening, Make one screen tell the person to Turn the Wheel to move the sun across the day.
TODO Make an incentive to turn the SUN from one side to the other.
TODO Time how long it takes to get the sun from one side to the other, display on screen as a way to incentise keeping turning.

# Pi Setup
J8:
   3V3  (1) (2)  5V
 GPIO2  (3) (4)  5V
 GPIO3  (5) (6)  GND
 GPIO4  (7) (8)  GPIO14
   GND  (9) (10) GPIO15
GPIO17 (11) (12) GPIO18
GPIO27 (13) (14) GND
GPIO22 (15) (16) GPIO23
   3V3 (17) (18) GPIO24
GPIO10 (19) (20) GND
 GPIO9 (21) (22) GPIO25
GPIO11 (23) (24) GPIO8
   GND (25) (26) GPIO7
 GPIO0 (27) (28) GPIO1
 GPIO5 (29) (30) GND
 GPIO6 (31) (32) GPIO12
GPIO13 (33) (34) GND  <- Button GND
GPIO19 (35) (36) GPIO16 
GPIO26 (37) (38) GPIO20 <- Line Sensor
   GND (39) (40) GPIO21 <- Line Sensor

PINs Used for Line Sensor
1 Power to Line Sensor (can also be 5V if needed) - Blue Wire
6 Gnd to Line Sensor - Brown Wire
GPIO2 - Water Turbine - RELAY LOW for ON
GPIO3 - Wind Turbine - RELAY LOW for ON
GPIO19 - Button 1
GPIO26 - Button 2
GPIO20 - Sunset
GPIO21 - Sun behind clouds.

GPIO25 - Forth set of House Lights
GPIO8 - 3rd set of House Lights
GPIO7 - 2nd set of House Lights
GPIO1 - First set of House Lights

- Hydro Light - Currently set to be always ON


# Commands to remember for Raspberry Pi 5
## List GPIO Pin information
pinctrl


# Equipment used in build
* https://core-electronics.com.au/line-sensor-adjustable-threshold.html Sensor for Sun to know when Up and Behind Clouds.
* * 3.3-5V Operating range
* https://core-electronics.com.au/super-bright-yellow-5mm-led-25-pack.html LEDs for Houses. Nice bright and warm Yellow.
* * Forward Voltage (at 20mA current): 3.0-3.4V. 


# Wiring


# Changes to Raspberry Pi OS
## Set Autostart of Chrome
Edited ~/.config/lxsession/LXDE-pi/autostart
Added to test:
@chromium-browser --kiosk https://www.hivetasmania.com.au

## FIX error: externally-managed-environment
https://www.makeuseof.com/fix-pip-error-externally-managed-environment-linux/
hive@raspberrypi: cd /usr/lib/python3.11
hive@raspberrypi:/usr/lib/python3.11 $ sudo rm EXTERNALLY-MANAGED

## Fix RuntimeError: Cannot determine SOC peripheral base address
This is a Raspberry Pi Device and the standard RPi isn't support for Python
sudo apt remove python3-rpi.gpio
pip3 install rpi-lgpio

## Pygame Fix FULLSCREEN refuses to work across two monitors now. (used to work)
Changed it to pygame.NOFRAME, display=0


# History
2024-05-23 Trying to get the PyGame FULL SCREEN to be across both monitors, like it is on another Raspberry Pi
   sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
   Trying Wayland - reboot
   Failed
   SDL_VIDEODRIVER=x11 ./main.py worked.
   Tried lots of options without success. Switching to X11 backend.
   Better... Aleast it was across both.
   pygame.FULLSCREEN refuses to work over two monitors on X11.
   sudo apt-get update
   sudo apt-get install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev
   sudo apt-get install libdirectfb-1.7-7 libdirectfb-dev
   sudo apt-get install libsvga1 libsvga-dev
   sudo apt-get install libgbm-dev libdrm-dev

2024-05-14 Changed background wallpaper to Hive.
2024-05-06 Connect up 5v or 3.3v?
