# Mojo

Let's make a smart bike!

This project was made for Treehacks 2019.  The Devpost page can be found [here](https://devpost.com/software/mojo-9ctvuj).

## Hardware
* Raspberry Pi Zero W
* 3A Switching DC-DC Buck Converter
* CD4050B Non-Inverting Level Shifter
  * Allows communication between Pi (3.3V) and SK6812 LEDs (5V)
* SK6812 RGBW LEDs
  * Snubbing Diode (for LEDs)
  * 1000uF Bypass Capacitor (for LEDs)
* Adafruit LSM9DS1 9dof Sensor Breakout Board
* Cute lil switches
* Neo-M8N GPS

## Software Dependencies
The Raspberry Pi was running rasbpian stretch-lite, flashed using the [Etcher](https://www.balena.io/etcher/) utility. [SSH over USB](https://stevegrunwell.com/blog/raspberry-pi-zero-share-internet/) was set up immediately to make things less painful.

All of the following can be installed with pip3 from [pypi.org](https://pypi.org)).
* [CircuitPython](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux)
* [NeoPixel](https://learn.adafruit.com/neopixels-on-raspberry-pi/raspberry-pi-wiring)
* [LSM9DS1](https://learn.adafruit.com/adafruit-lsm9ds1-accelerometer-plus-gyro-plus-magnetometer-9-dof-breakout/python-circuitpython)

## Gotchas
* Scheduling crontab tasks (like launching the LED script on @reboot) requires the use of `sudo crontab config_file_name`, instead of regular `crontab config_file_name` in order to get the crontab to run as root.
* If installing a package with `pip3` works OK but the program says there is "no module such-and-such," try `sudo pip3` instead.
* The [Adafruit GPS Library](https://learn.adafruit.com/adafruit-ultimate-gps/circuitpython-parsing) doesn't actually work with GNSS receivers like the Neo-M8N, since all the messages have different headers (sad).  GNSS receivers are more robust since they can receive from non-gps constellations like GLONASS and Beidou, so someone should probably build a CircuitPython library for GNSS receivers at some point.
* The default baud rate for our Neo-M8N receiver was 38400 baud.  If stuff doesn't work at first (messages about Unicode characters not being in the charset), it's usually because the baud rate is wrong and the program is receiving gibberish.
