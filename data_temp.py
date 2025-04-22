import threading
import time
import random
import math

# Mock sensor data
vals = {
    "AcX": [0],
    "AcY": [0],
    "AcZ": [0],
    "GyX": [0],
    "GyY": [0],
    "GyZ": [0]
}

# Flag to control the mock data generation
running = True

def generate_mock_data():
    """Generate simulated sensor data instead of reading from actual hardware"""
    global vals, running
    
    # Frequency and amplitude for simulated motion
    freq = 0.5  # Lower frequency for slower changes
    amplitude = 0.5  # Smaller amplitude for less extreme values
    
    # Starting time for our simulated motion
    start_time = time.time()
    
    while running:
        # Calculate time elapsed for wave generation
        elapsed = time.time() - start_time
        
        # Generate sinusoidal patterns for different axes with phase shifts
        # This creates somewhat realistic motion patterns
        vals["AcX"].append(amplitude * math.sin(freq * elapsed) + random.uniform(-0.1, 0.1))
        vals["AcY"].append(amplitude * math.sin(freq * elapsed + 1) + random.uniform(-0.1, 0.1))
        vals["AcZ"].append(amplitude * math.sin(freq * elapsed + 2) + random.uniform(-0.1, 0.1))
        vals["GyX"].append(amplitude * 0.5 * math.cos(freq * elapsed) + random.uniform(-0.05, 0.05))
        vals["GyY"].append(amplitude * 0.5 * math.cos(freq * elapsed + 1) + random.uniform(-0.05, 0.05))
        vals["GyZ"].append(amplitude * 0.5 * math.cos(freq * elapsed + 2) + random.uniform(-0.05, 0.05))
        
        # Keep the lists from growing too large
        for key in vals:
            if len(vals[key]) > 100:  # Keep only the most recent 100 readings
                vals[key] = vals[key][-100:]
        
        # Simulate sensor reading frequency
        time.sleep(0.05)  # 20Hz update rate

def connect():
    """Mock connection function that always succeeds"""
    print("Mock sensor connected successfully")
    return True

def read_data(ser):
    """This function is not used in the mock version"""
    pass  # Not used in mock version

def start_data_thread():
    """Start the mock data generation thread"""
    print("[DEBUG] Starting mock data generation thread")
    
    global running
    running = True
    
    # Create and start the thread for generating mock data
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
    
    # Monitor data for a while
    for _ in range(10):
        for key in vals:
            print(f"{key}: {vals[key][-1] if vals[key] else 0}")
        print("---")
        time.sleep(0.5)
    
    stop_data_thread()

if __name__ == "__main__":
    main()