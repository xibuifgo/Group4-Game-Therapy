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

    start_time = time.time()
    
    while running:
        elapsed = time.time() - start_time

        # Simulate semi-random balance noise bursts with some base values
        base_acc = [0, 0, 1]  # standing still: mostly Z gravity
        base_gyro = [0, 0, 0] # not rotating

        # Add small noise, and occasional bursts
        def noisy(val, burst_chance=0.1):
            if random.random() < burst_chance:
                return val + random.uniform(-3, 3)  # simulate balance loss
            else:
                return val + random.uniform(-0.2, 0.2)

        vals["AcX"].append(noisy(base_acc[0]))
        vals["AcY"].append(noisy(base_acc[1]))
        vals["AcZ"].append(noisy(base_acc[2]))
        vals["GyX"].append(noisy(base_gyro[0]))
        vals["GyY"].append(noisy(base_gyro[1]))
        vals["GyZ"].append(noisy(base_gyro[2]))

        # Truncate to keep length manageable
        for key in vals:
            if len(vals[key]) > 100:
                vals[key] = vals[key][-100:]

        time.sleep(0.05)  # 20Hz


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