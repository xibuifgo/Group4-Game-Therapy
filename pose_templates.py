import numpy as np

class PoseTemplates:
    def __init__(self):
        self.poses = [
            {
                "name": "T-Pose",
                "description": "Stand tall with both arms stretched out to the sides",
                "angles": {
                    "left_arm": {"target": 180, "tolerance": 20},
                    "right_arm": {"target": 180, "tolerance": 20},
                    "torso_lean": {"target": 0, "tolerance": 10}
                }
            },
            {
                "name": "Flamingo Right",
                "description": "Stand on left leg and raise right leg slightly forward, arms out to balance",
                "angles": {
                    "left_arm": {"target": 180, "tolerance": 20},
                    "right_arm": {"target": 180, "tolerance": 20},
                    "right_leg": {"target": 90, "tolerance": 20},
                    "torso_lean": {"target": 0, "tolerance": 10}
                }
            },
            {
                "name": "Flamingo Left",
                "description": "Stand on right leg and raise left leg slightly forward, arms out to balance",
                "angles": {
                    "left_arm": {"target": 180, "tolerance": 20},
                    "right_arm": {"target": 180, "tolerance": 20},
                    "left_leg": {"target": 90, "tolerance": 20},
                    "torso_lean": {"target": 0, "tolerance": 10}
                }
            },
            {
                "name": "Airplane",
                "description": "Lean slightly forward with arms out like airplane wings",
                "angles": {
                    "left_arm": {"target": 180, "tolerance": 20},
                    "right_arm": {"target": 180, "tolerance": 20},
                    "torso_lean": {"target": 20, "tolerance": 10}
                }
            },
            {
                "name": "Star Pose",
                "description": "Stand with arms and legs spread wide like a star",
                "angles": {
                    "left_arm": {"target": 180, "tolerance": 20},
                    "right_arm": {"target": 180, "tolerance": 20},
                    "left_leg": {"target": 180, "tolerance": 20},
                    "right_leg": {"target": 180, "tolerance": 20},
                    "torso_lean": {"target": 0, "tolerance": 10}
                }
            }
        ]

    def get_pose(self, index):
        if 0 <= index < len(self.poses):
            return self.poses[index]
        return None

    def get_pose_count(self):
        return len(self.poses)

    def calculate_pose_similarity(self, detected_angles, pose_index):
        if pose_index < 0 or pose_index >= len(self.poses):
            return 0

        if not detected_angles:
            return 0

        target_pose = self.poses[pose_index]
        angle_scores = []

        for angle_name, target_data in target_pose["angles"].items():
            if angle_name in detected_angles:
                detected_angle = detected_angles[angle_name]
                target_angle = target_data["target"]
                tolerance = target_data["tolerance"]

                angle_diff = abs(detected_angle - target_angle)

                if angle_diff <= tolerance:
                    score = 100 * (1 - angle_diff / tolerance)
                else:
                    score = max(0, 100 * (1 - angle_diff / (tolerance * 2)))

                angle_scores.append(score)

        if not angle_scores:
            return 0

        return np.mean(angle_scores)

    def get_pose_feedback(self, detected_angles, pose_index):
        if pose_index < 0 or pose_index >= len(self.poses):
            return "Invalid pose index"

        if not detected_angles:
            return "No pose detected"

        target_pose = self.poses[pose_index]
        feedback = []

        for angle_name, target_data in target_pose["angles"].items():
            if angle_name in detected_angles:
                detected_angle = detected_angles[angle_name]
                target_angle = target_data["target"]
                tolerance = target_data["tolerance"]

                angle_diff = abs(detected_angle - target_angle)

                if angle_diff <= tolerance:
                    feedback.append(f"✓ {angle_name}: Good!")
                else:
                    if detected_angle > target_angle:
                        feedback.append(f"✗ {angle_name}: Too high ({detected_angle:.1f}° vs {target_angle}°)")
                    else:
                        feedback.append(f"✗ {angle_name}: Too low ({detected_angle:.1f}° vs {target_angle}°)")

        return "\n".join(feedback)
