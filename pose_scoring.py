import math
import numpy as np
import data_temp

class PoseScorer:
    def __init__(self):
        self.poses = [
            # T-Pose
            {
                "AcX": {"expected": 0.0, "tolerance": 0.3},
                "AcY": {"expected": 0.0, "tolerance": 0.3},
                "AcZ": {"expected": 1.0, "tolerance": 0.3},
                "GyX": {"expected": 0.0, "tolerance": 0.2},
                "GyY": {"expected": 0.0, "tolerance": 0.2},
                "GyZ": {"expected": 0.0, "tolerance": 0.2}
            },
            # Flamingo Right (Right leg lifted)
            {
                "AcX": {"expected": 0.3, "tolerance": 0.3},
                "AcY": {"expected": 0.0, "tolerance": 0.3},
                "AcZ": {"expected": 0.9, "tolerance": 0.3},
                "GyX": {"expected": 0.0, "tolerance": 0.2},
                "GyY": {"expected": 0.0, "tolerance": 0.2},
                "GyZ": {"expected": 0.0, "tolerance": 0.2}
            },
            # Flamingo Left (Left leg lifted)
            {
                "AcX": {"expected": -0.3, "tolerance": 0.3},
                "AcY": {"expected": 0.0, "tolerance": 0.3},
                "AcZ": {"expected": 0.9, "tolerance": 0.3},
                "GyX": {"expected": 0.0, "tolerance": 0.2},
                "GyY": {"expected": 0.0, "tolerance": 0.2},
                "GyZ": {"expected": 0.0, "tolerance": 0.2}
            },
            # Airplane Pose (Forward Lean)
            {
                "AcX": {"expected": 0.6, "tolerance": 0.3},
                "AcY": {"expected": 0.1, "tolerance": 0.3},
                "AcZ": {"expected": 0.8, "tolerance": 0.3},
                "GyX": {"expected": 0.0, "tolerance": 0.2},
                "GyY": {"expected": 0.0, "tolerance": 0.2},
                "GyZ": {"expected": 0.0, "tolerance": 0.2}
            },
            # Star Pose (Wide stance)
            {
                "AcX": {"expected": 0.0, "tolerance": 0.3},
                "AcY": {"expected": 0.0, "tolerance": 0.3},
                "AcZ": {"expected": 1.0, "tolerance": 0.3},
                "GyX": {"expected": 0.0, "tolerance": 0.2},
                "GyY": {"expected": 0.0, "tolerance": 0.2},
                "GyZ": {"expected": 0.0, "tolerance": 0.2}
            }
        ]

        self.history_length = 5
        self.readings_history = []

    def get_normalized_sensor_data(self):
        ax = data_temp.vals["AcX"][-1] if data_temp.vals["AcX"] else 0
        ay = data_temp.vals["AcY"][-1] if data_temp.vals["AcY"] else 0
        az = data_temp.vals["AcZ"][-1] if data_temp.vals["AcZ"] else 0
        gx = data_temp.vals["GyX"][-1] if data_temp.vals["GyX"] else 0
        gy = data_temp.vals["GyY"][-1] if data_temp.vals["GyY"] else 0
        gz = data_temp.vals["GyZ"][-1] if data_temp.vals["GyZ"] else 0

        ax = max(-1, min(1, ax / 16384))
        ay = max(-1, min(1, ay / 16384))
        az = max(-1, min(1, az / 16384))

        gx = max(-1, min(1, gx / 131))
        gy = max(-1, min(1, gy / 131))
        gz = max(-1, min(1, gz / 131))

        return {
            "AcX": ax,
            "AcY": ay,
            "AcZ": az,
            "GyX": gx,
            "GyY": gy,
            "GyZ": gz
        }

    def smooth_readings(self, new_reading):
        self.readings_history.append(new_reading)
        if len(self.readings_history) > self.history_length:
            self.readings_history.pop(0)

        smoothed = {}
        for key in new_reading:
            values = [reading[key] for reading in self.readings_history]
            smoothed[key] = sum(values) / len(values)

        return smoothed

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

            difference = abs(smoothed[key] - expected)
            if difference > tolerance:
                sensor_scores[key] = 0
            else:
                sensor_scores[key] = 100 * (1 - difference / tolerance)

        total_score = sum(sensor_scores.values()) / len(sensor_scores)
        return total_score
