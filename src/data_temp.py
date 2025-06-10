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
    """Cycle through data patterns that simulate pose scores: high → medium → low → repeat"""
    global vals, running

    phase_duration = 3  # seconds per phase
    phases = [
        {"label": "sleeping", "acc": [0.0, 0.0, 1.0], "gyro": [0.0, 0.0, 0.0]},         # score ~85+
        {"label": "waking",   "acc": [0.6, 0.2, 0.8], "gyro": [0.3, 0.3, 0.1]},         # score ~60
        {"label": "angry",    "acc": [1.5, -1.2, 0.3], "gyro": [2.0, 2.0, 2.0]},        # score ~30
    ]

    print("[INFO] Cycling through mock balance patterns (sleeping → waking → angry)")
    start_time = time.time()

    while running:
        elapsed = time.time() - start_time
        phase_index = int(elapsed // phase_duration) % len(phases)
        current_phase = phases[phase_index]

        # Print the current phase every cycle
        if int(elapsed * 10) % (phase_duration * 10) == 0:
            print(f"[DEBUG] Phase: {current_phase['label']}")

        # Add small noise around base values
        def noisy(val, scale=0.1):
            return val + random.uniform(-scale, scale)

        acc = [noisy(v) for v in current_phase["acc"]]
        gyro = [noisy(v) for v in current_phase["gyro"]]

        vals["AcX"].append(acc[0])
        vals["AcY"].append(acc[1])
        vals["AcZ"].append(acc[2])
        vals["GyX"].append(gyro[0])
        vals["GyY"].append(gyro[1])
        vals["GyZ"].append(gyro[2])

        # Truncate to last 100
        for key in vals:
            if len(vals[key]) > 100:
                vals[key] = vals[key][-100:]

        time.sleep(0.05)  # 20 Hz

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

    for _ in range(30):
        for key in vals:
            print(f"{key}: {vals[key][-1] if vals[key] else 0}")
        print("---")
        time.sleep(0.5)

    stop_data_thread()

if __name__ == "__main__":
    main()