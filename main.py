from machine import SoftI2C, I2C
from machine import Pin
from machine import sleep
import network
import espnow
import mpu6050
import ujson

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)

# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

# Define the MAC address of the receiving ESP32 (ESP32 B)
peer = b'<\x8a\x1f\x9dE\xa4'
esp.add_peer(peer)

# Initialzing the i2c comm protocol by declaring location of sda and scl pins
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

# creating instance of mpu class to read the acceleration data via the i2c serial bus
mpu = mpu6050.accel(i2c)

while True:
    vals = mpu.get_values()
    json_data = ujson.dumps(vals)
    esp.send(peer, json_data.encode())
    print(f"Sending: {json_data}")
