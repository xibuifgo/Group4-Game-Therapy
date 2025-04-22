import threading
import time
import random
import math

vals = {
    "AcX": [0],
    "AcY": [0],
    "AcZ": [0],
    "GyX": [0],
    "GyY": [0],
    "GyZ": [0]
}

running = True

def generate_mock_data():
    """Generate simulated sensor data instead of reading from actual hardware"""
    global vals, running

    freq = 0.5
    amplitude = 0.5

    start_time = time.time()
    
    while running:
        elapsed = time.time() - start_time

        vals["AcX"].append(amplitude * math.sin(freq * elapsed) + random.uniform(-0.1, 0.1))
        vals["AcY"].append(amplitude * math.sin(freq * elapsed + 1) + random.uniform(-0.1, 0.1))
        vals["AcZ"].append(amplitude * math.sin(freq * elapsed + 2) + random.uniform(-0.1, 0.1))
        vals["GyX"].append(amplitude * 0.5 * math.cos(freq * elapsed) + random.uniform(-0.05, 0.05))
        vals["GyY"].append(amplitude * 0.5 * math.cos(freq * elapsed + 1) + random.uniform(-0.05, 0.05))
        vals["GyZ"].append(amplitude * 0.5 * math.cos(freq * elapsed + 2) + random.uniform(-0.05, 0.05))
        
        for key in vals:
            if len(vals[key]) > 100:
                vals[key] = vals[key][-100:]
        
        time.sleep(0.05)  # 20Hz update rate

def connect():
    """Mock connection function that always succeeds"""
    print("Mock sensor connected successfully")
    return True

def read_data(ser):
    """This function is not used in the mock version"""
    pass

def start_data_thread():
    """Start the mock data generation thread"""
    print("[DEBUG] Starting mock data generation thread")
    
    global running
    running = True
    
    thread = threading.Thread(target=generate_mock_data, daemon=True)
    thread.start()
    print("[INFO] Mock data thread started")

def stop_data_thread():
    """Stop the mock data generation thread"""
    global running
    running = False
    print("[INFO] Mock data thread stopped")

def main():
    """Test the mock data generation"""
    print("[INFO] Starting mock data test...")
    
    start_data_thread()
    
    for _ in range(10):
        for key in vals:
            print(f"{key}: {vals[key][-1] if vals[key] else 0}")
        print("---")
        time.sleep(0.5)
    
    stop_data_thread()

if __name__ == "__main__":
    main()