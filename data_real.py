import serial
import threading
import matplotlib.pyplot as plt
import numpy as np
import json
import time

vals = {"AcX": [0],
            "AcY": [0],
            "AcZ": [0],
            "GyX": [0],
            "GyY": [0],
            "GyZ": [0]}

def connect():
    # Adjust the port to match your ESP32 (check Device Manager or `ls /dev/ttyUSB*` on Linux/Mac)
    ser = serial.Serial('COM3', 115200, timeout=0.1)

    return ser

def read_data(ser):

    global vals

    while True: 
        # Read and decode the incoming line from serial
        line = ser.readline() # Read, decode, and clean the data

        # Clean the line by stripping out any unwanted characters (like the extra 'b' and surrounding quotes)
        cleaned_line = line.decode("utf-8").strip()  # Remove surrounding spaces/newlines
        if cleaned_line.startswith("b'") and cleaned_line.endswith("'"):
            line = cleaned_line[2:-1]  # Remove the unwanted b' and '
        
        if not line:  # Check if the line is empty
            print("Warning: Received an empty line, skipping...")
            continue

        try:
            data = json.loads(line)  # Convert JSON string to dictionary
            print(f"Parsed data: {data} (type: {type(data)})")
            
            # Append the parsed data to the respective lists in vals
            for key in vals.keys():
                vals[key].append(data[key])
            
        except json.JSONDecodeError as e:

            print("JSON Error:", e)
            # Handle the error if the line is not valid JSON
            print(f"Invalid data: {line}, skipping...")
            continue  # Skip invalid data and move to the next iteration

def start_data_thread():
    print("[DEBUG] start_data_thread() was called.")

    ser = connect()
    if ser is not None:
        print("[DEBUG] Creating and starting the thread.")  # ✅ Check if thread starts
        thread = threading.Thread(target=read_data, args=(ser,), daemon=True)
        thread.start()
        print("[INFO] Data thread started.")  # ✅ Confirm the thread started
    else:
        print("[ERROR] Could not start data thread due to connection failure.")

def main():
    """ Runs the ESP32 data collection process. """
    print("[INFO] Starting ESP32 Data Collection...")
    
    ser = connect()  # Open serial connection
    if ser is None:
        print("[ERROR] Failed to connect to ESP32. Exiting...")
        return

    while True:
        vals = read_data(ser)  # Read data
        # if vals:
        #     print(f"[DEBUG] Latest sensor values: {vals}")  # Print real-time values

        time.sleep(0.1)  # Adjust sampling rate if needed

if __name__ == "__main__":

    main()