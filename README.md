# temp-humid-sensor-pico-w

## About

This is a micropython script for the raspberry pi pico w in use with a HDC1080 sensor. If you send a http request to the raspberry pi pico will you receive the current temperature and humidity read by the sensor.

## How to use

1. Upload [my HDC1080 library](https://github.com/SturmEnte/hdc1080-raspberry-pi-pico) to the pico.
2. Upload a Python file called "secrets.py" with a variable called "SSID" containing the wifi's ssid and a variable called "PASSWORD" containing the wifi's password. You can also create a variable called "TEMP_CORRECTION". The integer you put in this variable will be added to the raw temperatur to get the corrected temperature.
3. Upload main.py from this repository to the pico.

## Wifi connection

If the pico is not connected to the wifi will the onboard led be activated. If it disconnects from the wifi will it try to reconnect to the wifi until it reconnects

## Units

- Temperature: °C
- Relative Humidity: %
- Absolute Humidity: g/m³

## My example circuit

![IMG_20230425_140846](https://user-images.githubusercontent.com/55847228/234283987-8146d318-3150-4072-add4-3c604de445e0.jpg)
![IMG_20230425_140852](https://user-images.githubusercontent.com/55847228/234284000-e7260b63-16d1-4535-ab2d-9bbd1362220c.jpg)
