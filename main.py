from machine import Pin, I2C
import utime as time
from dht import DHT11, InvalidChecksum
import network
import secrets
import time
import socket
import json

led = machine.Pin('LED', machine.Pin.OUT)
led.on()

def meassure():
    try:
        return ((sensor.temperature), (sensor.humidity))
    except:
        return
    
def connect_to_wifi():
    wlan.connect(secrets.SSID, secrets.PASSWORD)

    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        print('network connection failed')

def check_wifi():
    if not wlan.isconnected():
        led.on()
        print("Disconnected from wifi")
        print('Reconnecting to wifi...')
        while not wlan.isconnected():
            connect_to_wifi()
        print("Reconnected to the wifi")
        print( 'Ip = ' + wlan.ifconfig()[0] )
        led.off()

pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(pin)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
connect_to_wifi()

if wlan.isconnected():
    while not wlan.isconnected():
        connect_to_wifi()
    print('Connected to wifi')
    led.off()

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

while True:
    check_wifi()
    
    s.settimeout(60)
    try:
        cl, addr = s.accept()
        print('Request from: ', addr)
        request = cl.recv(1024)
        
        m = meassure()
    
        if m:
            cl.send('HTTP/1.0 200 OK\r\nContent-type: application/json\r\n\r\n')
            cl.send("{\"temperature\":%s, \"humidity\":%s}" % (m[0], m[1]))
        else:
            cl.send('HTTP/1.0 500 Internal Server Error\r\nContent-type: application/json\r\n\r\n')
            cl.send("{\"error\":\"Error while reading sensor data\"}")
        
        cl.close()
        
    except OSError as e:
        try:
            cl.close()
            print('connection closed')
        except:
            pass
        