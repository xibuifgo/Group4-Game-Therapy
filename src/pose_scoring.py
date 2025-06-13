# pose_scoring.py
import math
USE_ELECTRONICS = True          # set by PoseGame or at the top level

if USE_ELECTRONICS:
    import data_real as sensor_data
else:
    import data_temp as sensor_data


class PoseScorer:
    """
    Computes a stability score out of 100 based purely on recent
    accelerometer wobble.  Lower peak acceleration → higher score.
    """

    # --- Per-pose peak-acceleration bands (g) ------------------------
    # Taken from the old pose_score_thresholds in pose_game.py
    # Format:  (good_limit, moderate_limit)
    #
    ACCEL_THRESHOLDS = [
        (20.6, 23.0),     # 0  Normal standing
        (20.7, 26.0),     # 1  Star
        (21.0, 29.0),     # 2  Tandem
        (21.1, 30.0),    # 3  Heel-raise
        (21.6, 32.0),    # 4  Flamingo left
        (21.6, 32.0)     # 5  Flamingo right
    ]
    # -----------------------------------------------------------------

    WINDOW = 30        # how many readings (~1 s @ 30 Hz) to inspect

    # -----------------------------------------------------------------
    # Low-level helpers
    # -----------------------------------------------------------------
    @staticmethod
    def _max_accel_last_window():
        """Return the largest √(ax²+ay²+az²) in the most-recent window."""
        try:
            ax = sensor_data.vals["AcX"][-PoseScorer.WINDOW:]
            ay = sensor_data.vals["AcY"][-PoseScorer.WINDOW:]
            az = sensor_data.vals["AcZ"][-PoseScorer.WINDOW:]
            print(f"Acceleration Window: {ax}, {ay}, {ay}")
            mags = [math.sqrt(x**2 + y**2 + z**2)
                     for x, y, z in zip(ax, ay, az)]
            return max(mags) if mags else float("inf")
        except Exception as e:
            print(f"[PoseScorer] accel window error: {e}")
            return float("inf")               # treat error as very shaky

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------
    def sensor_score(self, pose_index: int) -> float:
        """
        100 when the peak acceleration is within `good`;
         65 when within `moderate`;
         30 otherwise.
        """
        if pose_index >= len(self.ACCEL_THRESHOLDS):
            return 50.0                       # unknown pose → neutral

        good_lim, mod_lim = self.ACCEL_THRESHOLDS[pose_index]
        max_accel         = self._max_accel_last_window()
        print(f"max accel:{max_accel}, good_lim: {good_lim}, mod_lim: {mod_lim}")
        if max_accel <= good_lim:
            return 100.0
        if max_accel <= mod_lim:
            return 65.0
        return 30.0
