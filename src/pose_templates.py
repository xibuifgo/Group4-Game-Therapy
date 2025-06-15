import numpy as np
import math
from pygame import font

class PoseTemplates:
    def __init__(self):
        self.templates = [
            {"name": "Normal standing stance", "description": "Stand with your feet together and body upright", "angles": {"torso_lean": 0}, "tolerances": {"default": 20, "torso_lean": 15}, "special_check": "normal_standing_stance"},
            {"name": "Star Pose", "description": "Stand with arms and legs spread wide like a star", "angles": {"left_shoulder": 90, "right_shoulder": 90, "torso_lean": 0}, "tolerances": {"default": 45, "torso_lean": 15}, "special_check": "star_pose"},
            {"name": "Tandem Stance", "description": "Facing forwards, stand with one foot directly in front of the other", "angles": {"torso_lean": 0, "left_leg": 180, "right_leg": 180}, "tolerances": {"default": 25, "torso_lean": 10}, "special_check": "tandem_stance"},
            {"name": "Heel Raise", "description": "Stand on your toes, lifting your heels", "angles": {"torso_lean": 0, "left_leg": 180, "right_leg": 180}, "tolerances": {"default": 25, "torso_lean": 15}, "special_check": "heel_raise"},
            {"name": "Flamingo Left", "description": "Stand on your right leg, lift your left leg up", "angles": {"torso_lean": 0}, "tolerances": {"default": 30, "torso_lean": 15}, "special_check": "flamingo_left"},
            {"name": "Flamingo Right", "description": "Stand on your left leg, lift your right leg up", "angles": {"torso_lean": 0}, "tolerances": {"default": 30, "torso_lean": 15}, "special_check": "flamingo_right"}
        ]

    def calculate_pose_similarity(self, angles, pose_index):
        if pose_index < 0 or pose_index >= len(self.templates): return 0
        template = self.templates[pose_index]
        if "special_check" in template:
            return self._handle_special_pose(angles, template)

        total_score, count = 0, 0
        for joint, target_angle in template["angles"].items():
            if joint in angles:
                actual_angle = angles[joint]
                tolerance = template["tolerances"].get(joint, template["tolerances"]["default"])
                total_score += self._score_angle(actual_angle, target_angle, tolerance)
                count += 1
        return total_score // count if count > 0 else 0

    def _handle_special_pose(self, angles, template):
        check = template["special_check"]
        angles_dict = template["angles"]
        tolerances = template["tolerances"]

        if check == "flamingo_left":
            return 100 if angles.get("left_ankle_y", 0) > 0.5 * angles.get("right_knee_y", 0) else 0
        elif check == "flamingo_right":
            return 100 if angles.get("right_ankle_y", 0) > 0.5 * angles.get("left_knee_y", 0) else 0
        elif check == "star_pose":
            spread_ok = abs(angles.get("left_ankle_x", 0) - angles.get("right_ankle_x", 0)) >= 0.1
            if not spread_ok: return 0
            left_score = self._score_angle(angles.get("left_shoulder", 0), angles_dict["left_shoulder"], tolerances.get("left_shoulder", tolerances["default"]))
            right_score = self._score_angle(angles.get("right_shoulder", 0), angles_dict["right_shoulder"], tolerances.get("right_shoulder", tolerances["default"]))
            return (left_score + right_score) // 2
        elif check == "tandem_stance":
            x_aligned = abs(angles.get("left_ankle_x", 0) - angles.get("right_ankle_x", 0)) < 0.05
            z_aligned = abs(angles.get("left_ankle_z", 0) - angles.get("right_ankle_z", 0)) < 0.03
            foot_aligned = x_aligned or z_aligned
            leg_score = (self._score_angle(angles.get("left_leg", 0), angles_dict["left_leg"], tolerances.get("left_leg", tolerances["default"])) + self._score_angle(angles.get("right_leg", 0), angles_dict["right_leg"], tolerances.get("right_leg", tolerances["default"]))) / 2
            torso_score = self._score_angle(angles.get("torso_lean", 0), angles_dict["torso_lean"], tolerances.get("torso_lean", tolerances["default"]))
            align_score = 100 if foot_aligned else 0
            return (leg_score + torso_score + align_score) // 3
        elif check == "heel_raise":
            lifted = (angles.get("left_heel_y", 1) > angles.get("left_toe_y", 1) - 0.02 and angles.get("right_heel_y", 1) > angles.get("right_toe_y", 1) + 0.02)
            leg_score = (self._score_angle(angles.get("left_leg", 0), angles_dict["left_leg"], tolerances.get("left_leg", tolerances["default"])) + self._score_angle(angles.get("right_leg", 0), angles_dict["right_leg"], tolerances.get("right_leg", tolerances["default"]))) / 2
            torso_score = self._score_angle(angles.get("torso_lean", 0), angles_dict["torso_lean"], tolerances.get("torso_lean", tolerances["default"]))
            lift_score = 100 if lifted else 0
            return (leg_score + torso_score + lift_score) // 3
        return 0

    def _score_angle(self, actual, target, tolerance):
        error = abs(actual - target)
        error = min(error, 360 - error)
        return 100 * (1 - error / tolerance) if error <= tolerance else max(0, 100 - (error - tolerance) * 2)

    def get_pose_feedback(self, angles, pose_index):
        if pose_index < 0 or pose_index >= len(self.templates): return "Invalid pose"
        template = self.templates[pose_index]
        return self._get_special_feedback(angles, template) if "special_check" in template else self._get_standard_feedback(angles, template)

    def _get_standard_feedback(self, angles, template):
        feedback = []
        for joint, target_angle in template["angles"].items():
            if joint in angles:
                actual_angle = angles[joint]
                tolerance = template["tolerances"].get(joint, template["tolerances"]["default"])
                error = abs(actual_angle - target_angle)
                error = min(error, 360 - error)
                if error > tolerance:
                    direction = "more" if actual_angle < target_angle else "less"
                    feedback.append(f"Adjust {joint.replace('_', ' ')} {direction}")
        return "\n".join(feedback)

    def _get_special_feedback(self, angles, template):
        check = template["special_check"]
        feedback = []

        if check in ["flamingo_left", "flamingo_right"]:
            lifted = "left" if "left" in check else "right"
            lifted_y = angles.get(f"{lifted}_ankle_y", 0)
            standing_y = angles.get(f"{'right' if lifted == 'left' else 'left'}_ankle_y", 0)
            if lifted_y <= standing_y:
                feedback.append(f"Lift your {lifted} leg higher")
            else: 
                feedback.append(":) Your leg is well lifted!")
            if abs(angles.get("torso_lean", 0)) > 20:
                feedback.append("Stand more upright")
            else:
                feedback.append(":) Good posture!")

        elif check == "normal_standing_stance":
            if abs(angles.get("torso_lean", 0)) > 10:
                feedback.append("Stand more upright")
            else:
                feedback.append(":) Good posture!")                
            if abs(angles.get("left_ankle_x", 0) - angles.get("right_ankle_x", 0)) >= 0.1:
                feedback.append("Bring your feet closer")
            else:
                feedback.append(":) Good feet position!")                

        elif check == "star_pose":
            if abs(angles.get("left_shoulder", 0) - 90) > 45 or abs(angles.get("right_shoulder", 0) - 90) > 45:
                feedback.append("Keep your arms at shoulder height")
            else:
                feedback.append(":) Good arms position")
            if abs(angles.get("left_ankle_x", 0) - angles.get("right_ankle_x", 0)) < 0.1:
                feedback.append("Spread your feet wider")
            else:
                feedback.append(":) Good legs position")

        elif check == "tandem_stance":
            if abs(angles.get("torso_lean", 0)) > 10:
                feedback.append("Stand more upright")
            else:
                feedback.append(":) Good posture!")                
            if abs(angles.get("left_ankle_x", 0) - angles.get("right_ankle_x", 0)) >= 0.05:
                feedback.append("Align your feet")
            else:
                feedback.append(":) Nice feet alignment")

        elif check == "heel_raise":
            if abs(angles.get("torso_lean", 0)) > 15:
                feedback.append("Keep torso upright")
            else:
                feedback.append(":) Good posture!")                   
            if not (
                angles.get("left_heel_y", 1) < angles.get("left_toe_y", 1) - 0.02 and
                angles.get("right_heel_y", 1) < angles.get("right_toe_y", 1) - 0.02
            ):
                feedback.append("Lift your heels higher")

            else:
                feedback.append(":) Your heels are lifted high")

        return "\n".join(feedback)


    def get_pose_score(self, angles, pose_index):
        template = self.templates[pose_index]

        check = template["special_check"]

        def binary(cond):
            return 1 if cond else 0

        if check in ("flamingo_left", "flamingo_right"):
            lifted = "left" if "left" in check else "right"
            other = "right" if lifted == "left" else "left"

            # criteria: lifted leg higher than standing leg, and torso lean ≤ 20°
            leg_ok = angles.get(f"{lifted}_ankle_y", 0) > angles.get(f"{other}_ankle_y", 0)
            posture_ok = abs(angles.get("torso_lean", 0)) <= 20

            return binary(leg_ok and posture_ok)

        elif check == "normal_standing_stance":
            # criteria: torso lean ≤ 10°, feet separation < 0.1
            posture_ok = abs(angles.get("torso_lean", 0)) <= 10
            feet_sep = abs(angles.get("left_ankle_x", 0) - angles.get("right_ankle_x", 0))
            feet_ok = feet_sep < 0.1

            return binary(posture_ok and feet_ok)

        elif check == "star_pose":
            # criteria: arms near shoulder height (±45° from 90°) and feet spread ≥ 0.1
            left_arm_ok = abs(angles.get("left_shoulder", 0) - 90) <= 45
            right_arm_ok = abs(angles.get("right_shoulder", 0) - 90) <= 45
            feet_sep = abs(angles.get("left_ankle_x", 0) - angles.get("right_ankle_x", 0))
            feet_ok = feet_sep >= 0.1

            return binary(left_arm_ok and right_arm_ok and feet_ok)

        elif check == "tandem_stance":
            # criteria: torso lean ≤ 10°, feet alignment < 0.05
            posture_ok = abs(angles.get("torso_lean", 0)) <= 10
            feet_sep = abs(angles.get("left_ankle_x", 0) - angles.get("right_ankle_x", 0))
            feet_ok = feet_sep < 0.05

            return binary(posture_ok and feet_ok)

        elif check == "heel_raise":
            # criteria: torso lean ≤ 15°, both heels lifted > 0.02 above toes
            posture_ok = abs(angles.get("torso_lean", 0)) <= 15
            left_lift = angles.get("left_toe_y", 1) - angles.get("left_heel_y", 1) > 0.02
            right_lift = angles.get("right_toe_y", 1) - angles.get("right_heel_y", 1) > 0.02

            return binary(posture_ok and left_lift and right_lift)

        # If we don’t recognize the check, consider it incorrect
        return 0

    def get_pose_description(self, index):
        if 0 <= index < len(self.templates):
            return {"name": self.templates[index]["name"], "description": self.templates[index]["description"]}
        return None

    def get_pose_count(self):
        return len(self.templates)

    def get_all_pose_names(self):
        return [template["name"] for template in self.templates]
