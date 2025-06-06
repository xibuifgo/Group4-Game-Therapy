import cv2
import mediapipe as mp
import numpy as np
import math
import pygame

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.current_landmarks = None
        self.pose_detected = False

    def get_camera_frame(self):
        """Capture and process camera frame"""
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame for pose detection
        results = self.pose.process(rgb_frame)

        # Draw pose landmarks if detected
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS,
                self.mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                self.mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2)
            )
            self.current_landmarks = results.pose_landmarks
            self.pose_detected = True
        else:
            self.pose_detected = False
            self.current_landmarks = None

        return frame, results.pose_landmarks

    def get_pose_angles(self, landmarks):
        """Calculate key angles from pose landmarks"""
        if not landmarks:
            return None

        # Convert landmarks to numpy array for easier processing
        landmarks_array = np.array([[lm.x, lm.y, lm.z] for lm in landmarks.landmark])
        angles = {}

        # Get key landmark points
        try:
            left_hip = landmarks_array[self.mp_pose.PoseLandmark.LEFT_HIP.value]
            right_hip = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
            left_shoulder = landmarks_array[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
            right_shoulder = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
            left_elbow = landmarks_array[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
            right_elbow = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value]
            left_wrist = landmarks_array[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
            right_wrist = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
            left_ankle = landmarks_array[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
            right_ankle = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]
            left_heel = landmarks_array[self.mp_pose.PoseLandmark.LEFT_HEEL.value]
            right_heel = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_HEEL.value]            
            left_toe = landmarks_array[self.mp_pose.PoseLandmark.LEFT_FOOT_INDEX.value]
            right_toe = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_FOOT_INDEX.value]           

            # Calculate shoulder angles (arm positioning)
            angles['left_shoulder'] = self.calculate_angle(left_hip, left_shoulder, left_elbow)
            angles['right_shoulder'] = self.calculate_angle(right_hip, right_shoulder, right_elbow)

            # Calculate elbow angles (arm bend)
            angles['left_elbow'] = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            angles['right_elbow'] = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

            # Calculate torso lean (balance)
            mid_hip = (left_hip + right_hip) / 2
            mid_shoulder = (left_shoulder + right_shoulder) / 2
            angles['torso_lean'] = self.calculate_torso_lean(mid_hip, mid_shoulder)

            # Additional useful angles
            angles['hip_angle'] = self.calculate_angle(left_hip, right_hip, 
                                                    np.array([right_hip[0], right_hip[1] - 0.1, right_hip[2]]))
            
            # Ankles positions in x-direction
            angles["left_ankle_x"] = left_ankle[0]
            angles["right_ankle_x"] = right_ankle[0]
            
            # Ankles positions in y-direction            
            angles["left_ankle_y"] = left_ankle[1]
            angles["right_ankle_y"] = right_ankle[1]

            # Heels positions in y-direction            
            angles["left_heel_y"] = left_heel[1]
            angles["right_heel_y"] = right_heel[1]

            # Toes positions in y-direction
            angles["left_toe_y"] = left_toe[1]
            angles["right_toe_y"] = right_toe[1]


        except (IndexError, ValueError) as e:
            print(f"Error calculating angles: {e}")
            return None

        return angles

    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points (point2 is the vertex)"""
        try:
            # Create vectors from point2 to point1 and point2 to point3
            v1 = point1 - point2
            v2 = point3 - point2

            # Calculate dot product and magnitudes
            dot_product = np.dot(v1, v2)
            magnitude1 = np.linalg.norm(v1)
            magnitude2 = np.linalg.norm(v2)

            # Avoid division by zero
            if magnitude1 == 0 or magnitude2 == 0:
                return 0

            # Calculate cosine of angle
            cos_angle = dot_product / (magnitude1 * magnitude2)
            cos_angle = np.clip(cos_angle, -1, 1)  # Ensure valid range for arccos

            # Convert to degrees
            angle = np.arccos(cos_angle)
            return np.degrees(angle)

        except (ValueError, RuntimeWarning):
            return 0

    def calculate_torso_lean(self, hip_point, shoulder_point):
        """Calculate how much the torso is leaning from vertical"""
        try:
            # Vector from hip to shoulder
            torso_vector = shoulder_point - hip_point
            
            # Vertical reference vector (pointing up)
            vertical_vector = np.array([0, -1, 0])  # Negative Y is up in image coordinates
            
            # Calculate angle from vertical
            dot_product = np.dot(torso_vector[:2], vertical_vector[:2])  # Use only x,y components
            magnitude_torso = np.linalg.norm(torso_vector[:2])
            magnitude_vertical = np.linalg.norm(vertical_vector[:2])
            
            if magnitude_torso == 0:
                return 0
                
            cos_angle = dot_product / (magnitude_torso * magnitude_vertical)
            cos_angle = np.clip(cos_angle, -1, 1)
            
            angle = np.arccos(cos_angle)
            return np.degrees(angle)
            
        except (ValueError, RuntimeWarning):
            return 0

    def calculate_vertical_angle(self, point1, point2):
        """Calculate angle from vertical (legacy method for compatibility)"""
        try:
            dx = point2[0] - point1[0]
            dy = point2[1] - point1[1]
            angle = math.atan2(abs(dx), abs(dy))
            return math.degrees(angle)
        except:
            return 0

    def frame_to_pygame_surface(self, frame):
        """Convert OpenCV frame to Pygame surface"""
        try:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Rotate frame for proper display in pygame
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            return frame_surface
        except Exception as e:
            print(f"Error converting frame to pygame surface: {e}")
            # Return a blank surface if conversion fails
            blank_surface = pygame.Surface((640, 480))
            blank_surface.fill((128, 128, 128))
            return blank_surface

    def get_landmark_visibility(self, landmarks):
        """Check visibility of key landmarks"""
        if not landmarks:
            return {}
            
        visibility = {}
        key_landmarks = [
            'LEFT_SHOULDER', 'RIGHT_SHOULDER', 'LEFT_ELBOW', 'RIGHT_ELBOW',
            'LEFT_HIP', 'RIGHT_HIP', 'LEFT_KNEE', 'RIGHT_KNEE',
            'LEFT_ANKLE', 'RIGHT_ANKLE', 'NOSE'
        ]
        
        for landmark_name in key_landmarks:
            landmark_idx = getattr(self.mp_pose.PoseLandmark, landmark_name).value
            landmark = landmarks.landmark[landmark_idx]
            visibility[landmark_name.lower()] = landmark.visibility > 0.5
            
        return visibility

    def is_pose_stable(self, landmarks, previous_landmarks=None):
        """Check if pose is stable (not moving too much)"""
        if not landmarks or not previous_landmarks:
            return True
            
        # Compare key points between current and previous frame
        current_array = np.array([[lm.x, lm.y] for lm in landmarks.landmark])
        previous_array = np.array([[lm.x, lm.y] for lm in previous_landmarks.landmark])
        
        # Calculate average movement
        movement = np.mean(np.linalg.norm(current_array - previous_array, axis=1))
        
        # Threshold for stability (adjust as needed)
        stability_threshold = 0.02
        return movement < stability_threshold

    def release(self):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()