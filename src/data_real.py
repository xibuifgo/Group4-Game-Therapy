import serial
import threading
import matplotlib.pyplot 
import numpy 
import json
import time
import serial.tools.list_ports

vals = {"AcX": [0],
            "AcY": [0],
            "AcZ": [0],
            "GyX": [0],
            "GyY": [0],
            "GyZ": [0]}

ports = serial.tools.list_ports.comports(include_links=True)
available = [port.device for port in ports]

def connect():
    ports = serial.tools.list_ports.comports()
    available = [port.device for port in ports]



    if not available:
        raise serial.SerialException("No serial ports found.")

    for port in ports:
        try:
            if port.vid != None:
                ser = serial.Serial(port.device, 115200, timeout=0.2)
                time.sleep(2)  # Give the ESP32 time to reset
                print(f"[INFO] Connected to {port}")
                return ser
            raise serial.SerialException("No available USB ports")
        except Exception as e:
            print(f"[WARNING] Could not open {port}: {e}")

    raise serial.SerialException("Could not connect to any available port.")

def read_data(ser):

    while True: 
        line = ser.readline()
        try:
            line = line.decode("utf-8").strip()
        except UnicodeDecodeError:
            print("[WARNING] Received non-UTF-8 data, skipping...")
            continue

        if not line:
            print("[DEBUG] Empty line received.")
            continue

        try:
            data = json.loads(line)
            print(f"Parsed data: {data}")

            for key in vals.keys():
                vals[key].append(data[key])
            
            if __name__ != "__main__":
                return vals
            
        except json.JSONDecodeError as e:

            print("JSON Error:", e)
            print(f"Invalid data: {line}, skipping...")
            continue

def start_data_thread():
    print("[DEBUG] start_data_thread() was called.")

    ser = connect()
    if ser is not None:
        print("[DEBUG] Creating and starting the thread.") 
        thread = threading.Thread(target=read_data, args=(ser,), daemon=True)
        thread.start()
        print("[INFO] Data thread started.") 
    else:
        print("[ERROR] Could not start data thread due to connection failure.")

def main():
    """ Runs the ESP32 data collection process. """
    print("[INFO] Starting ESP32 Data Collection...")
    
    ser = connect()
    if ser is None:
        print("[ERROR] Failed to connect to ESP32. Exiting...")
        return

    going = True

    while going:
        try:
            vals = read_data(ser) 
            # if vals:
            #     print(f"[DEBUG] Latest sensor values: {vals}")  # Print real-time values

            time.sleep(0.1)
        except KeyboardInterrupt:
            ser.close()
            going = False


if __name__ == "__main__":

    main()