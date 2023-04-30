from machine import Pin, I2C
import utime as time
from HDC1080 import HDC1080
import sh1106
import network
import secrets
import time
import socket
import json
import math
import ubinascii

TEMP_CORRECTION = 0

try:
    TEMP_CORRECTION = secrets.TEMP_CORRECTION
except:
    print("No temperature correction found")

led = machine.Pin('LED', machine.Pin.OUT)
led.on()

i2c = I2C(1, sda=Pin(26), scl=Pin(27))

sensor = HDC1080(i2c)
display = sh1106.SH1106_I2C(128, 64, i2c, machine.Pin(2), 0x3c)

def readSensor():
    data = sensor.readSensor()
    raw_temp = data[0]
    raw_humid = data[1]
    absolute_humid = absolute_from_relative_humidity(raw_temp, raw_humid)
    corrected_temp = data[0] + TEMP_CORRECTION
    corrected_humid = relative_from_absolute_humidity(corrected_temp, absolute_humid)
    return (corrected_temp, corrected_humid, absolute_humid)

# This formula is not 100% correct because it is not using the air pressure
# https://carnotcycle.wordpress.com/2012/08/04/how-to-convert-relative-humidity-to-absolute-humidity/
def absolute_from_relative_humidity(temp, rel_humid):
    return (6.112 * math.pow(math.e, (17.67 * temp)/(temp+243.5)) * rel_humid * 2.1674) / (273.15 + temp)

def relative_from_absolute_humidity(temp, abs_humid):
    return (abs_humid * (273.15 + temp)) / ( 13.2471 * math.pow(math.e, (17.67 * temp)/(temp+243.5)))

def connect_to_wifi():
    wlan.connect(secrets.SSID, secrets.PASSWORD)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("Waiting for connection...")
        time.sleep(1)

    if wlan.status() != 3:
        print("Network connection failed")

def check_wifi():
    if not wlan.isconnected():
        led.on()
        print("Disconnected from wifi")
        print('Reconnecting to wifi...')
        while not wlan.isconnected():
            connect_to_wifi()
        print("Reconnected to the wifi")
        print('Ip: ' + wlan.ifconfig()[0])
        print('Mac: ' + mac = ubinascii.hexlify(network.WLAN().config('mac'), ':').decode())
        led.off()
    else:
        print( 'Ip = ' + wlan.ifconfig()[0] )

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
check_wifi()

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

while True:
    check_wifi()
    
    try:
        data = readSensor()

        display.sleep(False)
        display.fill(0)

        display.text(str(round(data[0], 2)), 0, 0, 1)
        display.text('C', 50, 0, 1)
        display.text(str(round(data[1], 2)), 0, 10, 1)
        display.text('%', 50, 10, 1)
        display.text(str(round(data[2], 2)), 0, 20, 1)
        display.text('g/m3', 50, 20, 1)
        display.text(wlan.ifconfig()[0], 0, 55, 1)
        display.show()
        
    except:
        print("Failed to read data or to display it on the screen")
    
    s.settimeout(60)
    try:
        cl, addr = s.accept()
        print("Request from: ", addr)
        request = cl.recv(1024)
        
        try:
            data = readSensor()
            cl.send("HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n")
            cl.send("{\"temperature\":%s, \"relative_humidity\":%s, \"absolute_humidity\":%s}" % (data[0], data[1], data[2]))
    
        except:
            cl.send("HTTP/1.0 500 Internal Server Error\r\nContent-type: application/json\r\n\r\n")
            cl.send("{\"error\":\"Error while reading sensor data\"}")
        
        cl.close()
        
    except OSError as e:
        try:
            cl.close()
            print('connection closed')
        except:
            pass
        

