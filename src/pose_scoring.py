import math
import numpy as np
from pose_templates import PoseTemplates
USE_ELECTRONICS = True  # Toggle this to False when you don't have the kit

if USE_ELECTRONICS:
    import data_real as sensor_data
else:
    import data_temp as sensor_data

class PoseScorer:
    def __init__(self):
        self.history_length = 30
        self.good_lim = 17.05
        self.moderate_lim = 17.50
    
    def get_max_acceleration(self):

        try:
            ax_vals = sensor_data.vals["AcX"][-self.history_length:]
            ay_vals = sensor_data.vals["AcY"][-self.history_length:]
            az_vals = sensor_data.vals["AcZ"][-self.history_length:]
            magnitudes = [math.sqrt(ax**2 + ay**2 + az**2) for ax, ay, az in zip(ax_vals, ay_vals, az_vals)]
            return max(magnitudes)
        except Exception as e:
            print(f"[ERROR] max accel calculation failed: {e}")
            return float('inf')  # Treat error as very unstable



    def sensor_score(self):     
        max_accel = self.get_max_acceleration()

        if (max_accel <= self.good_lim):
            return 1
        elif (max_accel <= self.moderate_lim):
            return 0.5
        else:
            return 0
        


