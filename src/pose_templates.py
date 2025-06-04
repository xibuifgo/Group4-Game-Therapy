import numpy as np
import math
from pygame import font

class PoseTemplates:
    def __init__(self):
        # Define target angles for each pose
        self.templates = [
            {  # Normal standing stance
                "name": "Normal standing stance",
                "description": "Stand with your body upright",
                "angles": {                  
                    "torso_lean": 0
                },
                "tolerances": {                
                    "default": 20,
                    "torso_lean": 15
                },
                "special_check": "normal_standing_stance"
            },

            {  # Star Pose
                "name": "Star Pose",
                "description": "Stand with arms and legs spread wide like a star",
                "angles": {
                    "left_shoulder": 90,
                    "right_shoulder": 90,
                    "torso_lean": 0
                },
                "tolerances": {
                    "default": 25,
                    "torso_lean": 15
                }, 
                "special_check": "star_pose"
            },

            {  # Tandem Stance
                "name": "Tandem Stance",
                "description": "Stand with one foot directly in front of the other",
                "angles": {
                    "torso_lean": 0
                },
                "tolerances": {
                    "default": 25,
                    "torso_lean": 10
                },
                "special_check": "tandem_stance"
            },

            {  # Heel Raise
                "name": "Heel Rise",
                "description": "Stand on your toes, lifting your heels",
                "angles": {
                    "torso_lean": 0
                },
                "tolerances": {
                    "default": 25,
                    "torso_lean": 15
                },
                "special_check": "heel_rise"
            },

            {  # Flamingo Left
                "name": "Flamingo Left",
                "description": "Stand on your right leg, lift your left leg up",
                "angles": {
                    "torso_lean": 0
                },
                "tolerances": {
                    "default": 30,                 
                    "torso_lean": 20
                },
                "special_check": "flamingo_left"
            },

            {  # Flamingo Right
                "name": "Flamingo Right", 
                "description": "Stand on your left leg, lift your right leg up",
                "angles": {
                    "torso_lean": 0
                },
                "tolerances": {
                    "default": 30,               
                    "torso_lean": 20
                },
                "special_check": "flamingo_right"
            }
        ]

    def calculate_pose_similarity(self, angles, pose_index):
        """Calculate similarity between current pose and target pose"""
        if pose_index < 0 or pose_index >= len(self.templates):
            return 0
            
        template = self.templates[pose_index]
        
        # Handle special pose checks
        if "special_check" in template:
            return self._handle_special_pose(angles, template, pose_index)
        
        # Standard angle-based comparison
        total_score = 0
        count = 0
        
        for joint, target_angle in template["angles"].items():
            if joint in angles:
                actual_angle = angles[joint]
                tolerance = template["tolerances"].get(joint, template["tolerances"]["default"])
                
                # Calculate angular difference (accounting for circular nature)
                error = abs(actual_angle - target_angle)
                error = min(error, 360 - error)
                
                # Score based on how close we are to target within tolerance
                if error <= tolerance:
                    joint_score = 100 * (1 - error / tolerance)
                else:
                    joint_score = max(0, 100 - (error - tolerance) * 2)
                
                total_score += joint_score
                count += 1
        
        return total_score / count if count > 0 else 0

    def _handle_special_pose(self, angles, template, pose_index):
        """Handle poses that need special detection logic"""
        special_check = template["special_check"]

        if special_check == "flamingo_left":
            # Check if left ankle is above right ankle (left leg lifted)
            try:
                left_ankle_y = angles.get("left_ankle_y")
                right_ankle_y = angles.get("right_ankle_y")
                if left_ankle_y is not None and right_ankle_y is not None:
                    return 100 if left_ankle_y < right_ankle_y else 0
            except:
                pass
            return 0

        elif special_check == "flamingo_right":
            # Check if right ankle is above left ankle (right leg lifted)
            try:
                right_ankle_y = angles.get("right_ankle_y")
                left_ankle_y = angles.get("left_ankle_y")
                if right_ankle_y is not None and left_ankle_y is not None:
                    return 100 if right_ankle_y < left_ankle_y else 0
            except:
                pass
            return 0
        
        
        elif special_check == "star_pose":
            # Detect if feet and arms are wide apart
            try:
                left_ankle_x = angles.get("left_ankle_x")
                right_ankle_x = angles.get("right_ankle_x")
                ankle_spread = abs(left_ankle_x - right_ankle_x)

                shoulder_score = (
                    self._score_angle(angles.get("left_shoulder", 0), 135, 25) +
                    self._score_angle(angles.get("right_shoulder", 0), 135, 25)
                ) / 2

                # Require significant spread between ankles (tweak threshold as needed)
                if ankle_spread >= 0.1:
                    leg_score = 100
                else:
                    leg_score = 0

                return (shoulder_score + leg_score) / 2
            except:
                return 0

        elif special_check == "tandem_stance":
            try:
                left_ankle_x = angles.get("left_ankle_x")
                right_ankle_x = angles.get("right_ankle_x")
                ankle_dist = abs(left_ankle_x - right_ankle_x)

                legs_score = (
                    self._score_angle(angles.get("left_leg", 0), 180, 25) +
                    self._score_angle(angles.get("right_leg", 0), 180, 25)
                ) / 2
                balance_score = self._score_angle(angles.get("torso_lean", 0), 0, 10)
                foot_alignment_score = 100 if ankle_dist < 0.05 else 0

                return (legs_score + balance_score + foot_alignment_score) / 3
            except:
                return 0

        elif special_check == "heel_rise":
            try:
                left_heel_y = angles.get("left_ankle_y")
                right_heel_y = angles.get("right_ankle_y")
                left_toe_y = angles.get("left_toe_y")
                right_toe_y = angles.get("right_toe_y")

                # Heels must be higher (lower y value) than toes
                lifted = (left_heel_y < left_toe_y - 0.02) and (right_heel_y < right_toe_y - 0.02)

                leg_score = (
                    self._score_angle(angles.get("left_leg", 0), 180, 25) +
                    self._score_angle(angles.get("right_leg", 0), 180, 25)
                ) / 2
                balance_score = self._score_angle(angles.get("torso_lean", 0), 0, 15)
                lift_score = 100 if lifted else 0

                return (leg_score + balance_score + lift_score) / 3
            except:
                return 0

        return 0
    
        


    def _score_angle(self, actual, target, tolerance):
        """Score a single angle comparison"""
        error = abs(actual - target)
        error = min(error, 360 - error)
        
        if error <= tolerance:
            return 100 * (1 - error / tolerance)
        else:
            return max(0, 100 - (error - tolerance) * 2)

    def get_pose_feedback(self, angles, pose_index):
        """Get detailed feedback for pose correction"""
        if pose_index < 0 or pose_index >= len(self.templates):
            return "Invalid pose"
            
        template = self.templates[pose_index]
        feedback = []
        
        # Handle special poses
        if "special_check" in template:
            return self._get_special_feedback(angles, template)
        
        # Standard feedback
        for joint, target_angle in template["angles"].items():
            if joint in angles:
                actual_angle = angles[joint]
                tolerance = template["tolerances"].get(joint, template["tolerances"]["default"])
                error = abs(actual_angle - target_angle)
                error = min(error, 360 - error)
                
                if error <= tolerance:
                    feedback.append(f":) {joint.replace('_', ' ').title()}")
                else:
                    direction = "more" if actual_angle < target_angle else "less"
                    feedback.append(f":( {joint.replace('_', ' ').title()} - adjust {direction}")
        
        return "\n".join(feedback) if feedback else "Keep trying!"

    def _get_special_feedback(self, angles, template):
        """Get feedback for special poses"""
        special_check = template["special_check"]
        feedback = []

        if special_check == "normal_standing_stance":
            # Normal standing stance specific feedback            
            feedback = []
            torso = angles.get("torso_lean", 0)
            left_ankle_x = angles.get("left_ankle_x", 0)
            right_ankle_x = angles.get("right_ankle_x", 0)
            ankle_spread = abs(left_ankle_x - right_ankle_x)

            if abs(torso) <= 10:
                feedback.append(":) Your posture is good")
            else:
                feedback.append(":( Stand more upright")

            if ankle_spread < 0.1:
                feedback.append(":) Good legs position")
            else:
                feedback.append(":( Keep your feet together")

        elif "flamingo" in special_check:
            # Flaming pose specific feedback
            lifted_leg = "left" if "left" in special_check else "right"

            lifted_angle = angles.get(f"{lifted_leg}_leg", 0)
            lean = angles.get("torso_lean", 0)
                
            if abs(lifted_angle - 90) <= 40:
                feedback.append(f":) Your {lifted_leg.title()} leg is lifted")
            else:
                feedback.append(f":( Lift your {lifted_leg} leg higher")
                
            if abs(lean) <= 20:
                feedback.append(":) Your balance is good")
            else:
                feedback.append(":( Keep your balanced")


        elif special_check == "star_pose":
            # Star pose specific feedback
            feedback = []
            left_shoulder = angles.get("left_shoulder", 0)
            right_shoulder = angles.get("right_shoulder", 0)
            left_ankle_x = angles.get("left_ankle_x", 0)
            right_ankle_x = angles.get("right_ankle_x", 0)
            ankle_spread = abs(left_ankle_x - right_ankle_x)

            if abs(left_shoulder - 90) <= 25:
                feedback.append(":) Good left arm position")
            else:
                feedback.append(":( Spread you left arm more")

            if abs(right_shoulder - 90) <= 25:
                feedback.append(":) Good right arm position")
            else:
                feedback.append(":( Spread your right arm more")

            if ankle_spread >= 0.1:
                feedback.append(":) Good legs position")
            else:
                feedback.append(":( Keep your feet apart")

            return "\n".join(feedback)

        elif special_check == "tandem_stance":
            # Tandem stance specific feedback            
            feedback = []
            torso = angles.get("torso_lean", 0)
            left_ankle_x = angles.get("left_ankle_x", 0)
            right_ankle_x = angles.get("right_ankle_x", 0)
            ankle_dist = abs(left_ankle_x - right_ankle_x)


            if abs(torso) <= 10:
                feedback.append(":) Your posture is good")
            else:
                feedback.append(":( Stand more upright")

            if ankle_dist < 0.05:
                feedback.append(":) Your feet are aligned")
            else:
                feedback.append(":( Bring feet into line")

            return "\n".join(feedback)
        
        elif special_check == "heel_rise":
            # Heel rise specific feedback
            feedback = []
            torso = angles.get("torso_lean", 0)
            left_heel = angles.get("left_ankle_y", 1)
            right_heel = angles.get("right_ankle_y", 1)
            left_toe = angles.get("left_toe_y", 1)
            right_toe = angles.get("right_toe_y", 1)

            if abs(torso) <= 15:
                feedback.append(":) Your balance is good")
            else:
                feedback.append(":( Keep your torso upright")

            if left_heel < left_toe - 0.02 and right_heel < right_toe - 0.02:
                feedback.append(":) Your heels are lifted")
            else:
                feedback.append(":( Lift your heels higher")

            return "\n".join(feedback)


        
        return "\n".join(feedback) if feedback else "Keep trying!"


    def get_pose_description(self, index):
        """Get pose name and description"""
        if 0 <= index < len(self.templates):
            template = self.templates[index]
            return {
                "name": template["name"],
                "description": template["description"]
            }
        return None

    def get_pose_count(self):
        """Get total number of poses"""
        return len(self.templates)

    def get_all_pose_names(self):
        """Get list of all pose names"""
        return [template["name"] for template in self.templates]