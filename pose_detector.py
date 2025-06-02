# pose_detector.py
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
        
        # Store current pose landmarks
        self.current_landmarks = None
        self.pose_detected = False
        
    def get_camera_frame(self):
        """Get current camera frame and detect pose"""
        ret, frame = self.cap.read()
        if not ret:
            return None, None
            
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose detection
        results = self.pose.process(rgb_frame)
        
        # Draw pose landmarks on frame
        if results.pose_landmarks:
            self.mp_drawing.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            self.current_landmarks = results.pose_landmarks
            self.pose_detected = True
        else:
            self.pose_detected = False
            
        return frame, results.pose_landmarks
    
    def get_pose_angles(self, landmarks):
        """Extract key angles from pose landmarks"""
        if not landmarks:
            return None
            
        # Get landmark positions
        landmarks_array = []
        for landmark in landmarks.landmark:
            landmarks_array.append([landmark.x, landmark.y, landmark.z])
        landmarks_array = np.array(landmarks_array)
        
        # Define key angles to calculate
        angles = {}
        
        # Left arm angle (shoulder-elbow-wrist)
        left_shoulder = landmarks_array[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks_array[self.mp_pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks_array[self.mp_pose.PoseLandmark.LEFT_WRIST.value]
        angles['left_arm'] = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        
        # Right arm angle
        right_shoulder = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_WRIST.value]
        angles['right_arm'] = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
        
        # Left shoulder elevation (torso-shoulder-elbow)
        left_hip = landmarks_array[self.mp_pose.PoseLandmark.LEFT_HIP.value]
        angles['left_shoulder_elevation'] = self.calculate_angle(left_hip, left_shoulder, left_elbow)
        
        # Right shoulder elevation
        right_hip = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_HIP.value]
        angles['right_shoulder_elevation'] = self.calculate_angle(right_hip, right_shoulder, right_elbow)
        
        # Torso lean (vertical vs hip-shoulder line)
        nose = landmarks_array[self.mp_pose.PoseLandmark.NOSE.value]
        mid_hip = (left_hip + right_hip) / 2
        angles['torso_lean'] = self.calculate_vertical_angle(mid_hip, nose)

        # Left leg angle (hip-knee-ankle)
        left_knee = landmarks_array[self.mp_pose.PoseLandmark.LEFT_KNEE.value]
        left_ankle = landmarks_array[self.mp_pose.PoseLandmark.LEFT_ANKLE.value]
        angles['left_leg'] = self.calculate_angle(left_hip, left_knee, left_ankle)

        # Right leg angle (hip-knee-ankle)
        right_knee = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_KNEE.value]
        right_ankle = landmarks_array[self.mp_pose.PoseLandmark.RIGHT_ANKLE.value]
        angles['right_leg'] = self.calculate_angle(right_hip, right_knee, right_ankle)

        
        return angles
    
    def calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        # Vectors
        v1 = point1 - point2
        v2 = point3 - point2
        
        # Calculate angle
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        cos_angle = np.clip(cos_angle, -1, 1)  # Prevent numerical errors
        angle = np.arccos(cos_angle)
        
        return np.degrees(angle)
    
    def calculate_vertical_angle(self, point1, point2):
        """Calculate angle from vertical"""
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        angle = math.atan2(abs(dx), abs(dy))
        return math.degrees(angle)
    
    def frame_to_pygame_surface(self, frame):
        """Convert OpenCV frame to pygame surface"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        return frame_surface
    
    def release(self):
        """Release camera resources"""
        self.cap.release()
        cv2.destroyAllWindows()