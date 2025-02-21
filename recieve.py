import network
import espnow
import machine

# A WLAN interface must be active to send()/recv()
sta = network.WLAN(network.STA_IF)  # Or network.AP_IF
sta.active(True)

# Initialize ESP-NOW
esp = espnow.ESPNow()
esp.active(True)

while True:
    _, msg = esp.recv()
    if msg: 
        print(msg)
    else:
        print("Message not recieved")