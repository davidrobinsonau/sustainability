# sustainability
Hive Display of Wind, Hydro, Hydro Battery, and Solar

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
GPIO13 (33) (34) GND
GPIO19 (35) (36) GPIO16
GPIO26 (37) (38) GPIO20
   GND (39) (40) GPIO21

PINs Used for Line Sensor
1 Power to Line Sensor (can also be 5V if needed) - Blue Wire
6 Gnd to Line Sensor - Brown Wire
GPIO20 - Sunset
GPIO21 - Sun behind clouds.

# Commands to remember for Raspberry Pi 5
## List GPIO Pin information
pinctrl


# Equipment used in build
* https://core-electronics.com.au/line-sensor-adjustable-threshold.html Sensor for Sun to know when Up and Behind Clouds.
** 3.3-5V Operating range


# Changes to Raspberry Pi OS
## FIX error: externally-managed-environment
https://www.makeuseof.com/fix-pip-error-externally-managed-environment-linux/
hive@raspberrypi: cd /usr/lib/python3.11
hive@raspberrypi:/usr/lib/python3.11 $ sudo rm EXTERNALLY-MANAGED

## Fix RuntimeError: Cannot determine SOC peripheral base address
This is a Raspberry Pi Device and the standard RPi isn't support for Python
sudo apt remove python3-rpi.gpio
pip3 install rpi-lgpio

# History
2024-05-06 Connect up 5v or 3.3v?