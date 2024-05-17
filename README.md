# sustainability
Hive Display of Wind, Hydro, Hydro Battery, and Solar

# Software Language
Python 3

TODO Consider switching to PyGame for display over the two monitors. Then I can draw over the image and change it. 
TODO Draw two Arrows that align up to the Buttons and Add large text "Wind Power" "Hydro Power"
TODO When Nothing Happening, Make one screen tell the person to Turn the Wheel to move the sun across the day.
TODO Make an incentive to turn the SUN from one side to the other.

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
GPIO20 - Sunset
GPIO21 - Sun behind clouds.

- Hydro Light
- Houses x 2 (batches of 2). Need Transister to drive them.
- Hydro Power Relay (LOW ON)
- Window Power Relay (LOW ON)

I need:
11 x NPN Transisters to test on LED.
Small Screwdrivers
6V Power supply to lower noise of motors.
Cut - on LEDS and connect Pins to Breadboard for NPN Transister.


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

# History
2024-05-14 Changed background wallpaper to Hive.
2024-05-06 Connect up 5v or 3.3v?
