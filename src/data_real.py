import serial
import threading
import matplotlib.pyplot as plt
import numpy as np
import json
import time

# Dictionary to store sensor data
vals = {
    "AcX": [0],
    "AcY": [0],
    "AcZ": [0],
    "GyX": [0],
    "GyY": [0],
    "GyZ": [0]
}

def connect():
<<<<<<< HEAD
    ser = serial.Serial('COM4', 115200, timeout=0.1)

    return ser
=======
    """Connect to the ESP32 over COM port."""
    try:
        ser = serial.Serial('COM4', 115200, timeout=0.1)
        return ser
    except serial.SerialException as e:
        print(f"[ERROR] Failed to connect to COM4: {e}")
        return None
>>>>>>> 777c875d87b28e886d667157a23df799dc4fb9e3

def read_data(ser):
    """Continuously read and parse data from the serial port."""
    global vals

    while True:
        line_bytes = ser.readline()
        if not line_bytes:
            print("Warning: Received an empty line, skipping...")
            continue

        try:
            line = line_bytes.decode("utf-8").strip()
            data = json.loads(line)
            print(f"Parsed data: {data}")

            for key in vals.keys():
                vals[key].append(data[key])

        except json.JSONDecodeError as e:
            print("JSON Error:", e)
            print(f"Invalid data: {line}, skipping...")
            continue

        except UnicodeDecodeError as e:
            print("Decode Error:", e)
            print(f"Invalid byte stream: {line_bytes}, skipping...")
            continue

def start_data_thread():
    """Starts the data reading thread."""
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
    """Runs the ESP32 data collection process."""
    print("[INFO] Starting ESP32 Data Collection...")

    start_data_thread()

    # Keep printing latest sensor values every second
    while True:
        latest = {k: v[-1] for k, v in vals.items()}
        print(f"[LIVE] Latest sensor values: {latest}")
        time.sleep(1)

if __name__ == "__main__":
    main()
