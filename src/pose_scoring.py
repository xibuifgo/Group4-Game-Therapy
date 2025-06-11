import math
import numpy as np
from pose_templates import PoseTemplates
USE_ELECTRONICS = False  # Toggle this to False when you don't have the kit

if USE_ELECTRONICS:
    import data_real as sensor_data
else:
    import data_temp as sensor_data

class PoseScorer:
    def __init__(self):
        self.poses = [
            # T-Pose
            {"AcX": {"expected": 0.0, "tolerance": 0.3},
             "AcY": {"expected": 0.0, "tolerance": 0.3},
             "AcZ": {"expected": 1.0, "tolerance": 0.3},
             "GyX": {"expected": 0.0, "tolerance": 0.2},
             "GyY": {"expected": 0.0, "tolerance": 0.2},
             "GyZ": {"expected": 0.0, "tolerance": 0.2}},

            # Flamingo Right
            {"AcX": {"expected": 0.3, "tolerance": 0.3},
             "AcY": {"expected": 0.0, "tolerance": 0.3},
             "AcZ": {"expected": 0.9, "tolerance": 0.3},
             "GyX": {"expected": 0.0, "tolerance": 0.2},
             "GyY": {"expected": 0.0, "tolerance": 0.2},
             "GyZ": {"expected": 0.0, "tolerance": 0.2}},

            # Flamingo Left
            {"AcX": {"expected": -0.3, "tolerance": 0.3},
             "AcY": {"expected": 0.0, "tolerance": 0.3},
             "AcZ": {"expected": 0.9, "tolerance": 0.3},
             "GyX": {"expected": 0.0, "tolerance": 0.2},
             "GyY": {"expected": 0.0, "tolerance": 0.2},
             "GyZ": {"expected": 0.0, "tolerance": 0.2}},

            # Airplane Pose
            {"AcX": {"expected": 0.6, "tolerance": 0.3},
             "AcY": {"expected": 0.1, "tolerance": 0.3},
             "AcZ": {"expected": 0.8, "tolerance": 0.3},
             "GyX": {"expected": 0.0, "tolerance": 0.2},
             "GyY": {"expected": 0.0, "tolerance": 0.2},
             "GyZ": {"expected": 0.0, "tolerance": 0.2}},

            # Star Pose
            {"AcX": {"expected": 0.0, "tolerance": 0.3},
             "AcY": {"expected": 0.0, "tolerance": 0.3},
             "AcZ": {"expected": 1.0, "tolerance": 0.3},
             "GyX": {"expected": 0.0, "tolerance": 0.2},
             "GyY": {"expected": 0.0, "tolerance": 0.2},
             "GyZ": {"expected": 0.0, "tolerance": 0.2}}
        ]
        self.history_length = 5
        self.readings_history = []

    def get_normalized_sensor_data(self):
        ax = sensor_data.vals["AcX"][-1] if sensor_data.vals["AcX"] else 0
        ay = sensor_data.vals["AcY"][-1] if sensor_data.vals["AcY"] else 0
        az = sensor_data.vals["AcZ"][-1] if sensor_data.vals["AcZ"] else 0
        gx = sensor_data.vals["GyX"][-1] if sensor_data.vals["GyX"] else 0
        gy = sensor_data.vals["GyY"][-1] if sensor_data.vals["GyY"] else 0
        gz = sensor_data.vals["GyZ"][-1] if sensor_data.vals["GyZ"] else 0

        ax = max(-1, min(1, ax / 16384))
        ay = max(-1, min(1, ay / 16384))
        az = max(-1, min(1, az / 16384))
        gx = max(-1, min(1, gx / 131))
        gy = max(-1, min(1, gy / 131))
        gz = max(-1, min(1, gz / 131))

        return {"AcX": ax, "AcY": ay, "AcZ": az, "GyX": gx, "GyY": gy, "GyZ": gz}
    
    def get_max_acceleration(self):
        try:
            ax_vals = data_real.vals["AcX"][-30:]
            ay_vals = data_real.vals["AcY"][-30:]
            az_vals = data_real.vals["AcZ"][-30:]
            magnitudes = [math.sqrt(ax**2 + ay**2 + az**2) for ax, ay, az in zip(ax_vals, ay_vals, az_vals)]
            return max(magnitudes)
        except Exception as e:
            print(f"[ERROR] max accel calculation failed: {e}")
            return float('inf')  # Treat error as very unstable

    def smooth_readings(self, new_reading):
        self.readings_history.append(new_reading)
        if len(self.readings_history) > self.history_length:
            self.readings_history.pop(0)

        return {k: sum(d[k] for d in self.readings_history) / len(self.readings_history)
                for k in new_reading}

    def calculate_score(self, pose_index):
        if pose_index < 0 or pose_index >= len(self.poses):
            return 0

        current = self.get_normalized_sensor_data()
        smoothed = self.smooth_readings(current)
        expected_pose = self.poses[pose_index]

        sensor_scores = {}
        for key in expected_pose:
            expected = expected_pose[key]["expected"]
            tolerance = expected_pose[key]["tolerance"]
            diff = abs(smoothed[key] - expected)

            if diff > tolerance:
                sensor_scores[key] = 0
            else:
                sensor_scores[key] = 100 * (1 - diff / tolerance)

        return sum(sensor_scores.values()) / len(sensor_scores)
