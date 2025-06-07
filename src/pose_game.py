import pygame
import sys
import random
import data_temp
import time
import math
from pose_loader import load_poses

# Try to import pose detection - fallback to mock data if not available
try:
    from pose_detector import PoseDetector
    from pose_templates import PoseTemplates
    POSE_DETECTION_AVAILABLE = True
    print("Pose detection available")
except ImportError as e:
    print(f"Pose detection not available: {e}")
    print("Falling back to accelerometer data")
    POSE_DETECTION_AVAILABLE = False

class PoseGame:
    def __init__(self, window, clock):
        self.window = window
        self.clock = clock
        self.width, self.height = window.get_size()
        self.game_active = False
        self.current_pose_index = 0
        self.game_over = False
        self.total_score = 0

        self.pose_full_duration = 3
        self.pose_corner_duration = 10
        self.current_time = 0
        self.start_time = 0
        self.phase = "waiting"
        self.phase = "preview"
        self.ready_confirmed = False
        self.preview_raise_start_time = None

        self.poses = load_poses()
        self.current_pose = None
        self.pose_raise_start_time = None

        # Initialize pose detection and templates
        if POSE_DETECTION_AVAILABLE:
            self.use_pose_detection = True
            self.pose_detector = PoseDetector()
            self.pose_templates = PoseTemplates()
        else:
            self.use_pose_detection = False
            self.pose_detector = None
            self.pose_templates = None

        # Create feedback images
        self.success_image = self.create_feedback_image("success")
        self.fail_image = self.create_feedback_image("fail")
        self.neutral_image = self.create_feedback_image("neutral")
        self.current_feedback = self.neutral_image

        # Scoring
        self.score_threshold = 70
        self.current_score = 0

        # Fonts
        self.font = pygame.font.SysFont('Comic Sans MS', 48)
        self.feedback_font = pygame.font.SysFont('Comic Sans MS', 40)

        # UI elements
        button_raw = {
            "default": pygame.image.load("assets/images/start_default.png").convert_alpha(),
            "hover": pygame.image.load("assets/images/start_hover.png").convert_alpha(),
            "clicked": pygame.image.load("assets/images/start_clicked.png").convert_alpha()
        }

        # Resize to smaller dimensions, e.g., 150x60
        scaled = {state: pygame.transform.scale(img, (350, 275)) for state, img in button_raw.items()}

        self.start_button_images = scaled
        self.start_button_state = "default"
        self.start_button_rect = self.start_button_images["default"].get_rect(center=(self.width // 2, self.height // 2 + 100))

        self.background_image = pygame.image.load("assets/images/bear_background.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

        # State variables
        self.mock_activity_level = 0
        self.camera_surface = None
        self.pose_feedback_text = ""
        self.previous_landmarks = None

    def create_feedback_image(self, feedback_type):
        """Create visual feedback images"""
        image = pygame.Surface((200, 200))
        if feedback_type == "success":
            image.fill((0, 200, 0))
            # Draw checkmark
            pygame.draw.lines(image, (255, 255, 255), False,
                             [(50, 100), (90, 150), (150, 70)], 10)
        elif feedback_type == "fail":
            image.fill((200, 0, 0))
            # Draw X
            pygame.draw.line(image, (255, 255, 255), (50, 50), (150, 150), 10)
            pygame.draw.line(image, (255, 255, 255), (150, 50), (50, 150), 10)
        else:  # neutral
            image.fill((150, 150, 150))
            font = pygame.font.SysFont('Comic Sans MS', 100)
            text = font.render("?", True, (255, 255, 255))
            image.blit(text, (80, 50))
        return image

    def start_game(self):
        """Initialize game state"""
        self.game_active = True
        self.current_pose_index = 0
        self.total_score = 0
        self.game_over = False
        self.mock_activity_level = 0
        self.previous_landmarks = None
        self.phase = "preview"  # Show camera preview first
        self.ready_confirmed = False  

    def start_new_pose(self):
        """Start a new pose challenge"""
        if self.current_pose_index >= len(self.poses):
            self.game_over = True
            return
            
        self.current_pose = self.poses[self.current_pose_index]
        self.phase = "full"
        self.start_time = time.time()
        self.current_score = 0
        self.current_feedback = self.neutral_image
        self.pose_feedback_text = ""
        self.mock_activity_level += 1

    def calculate_pose_score(self):
        """Calculate current pose score based on detection method"""
        if self.use_pose_detection and self.pose_detector:
            return self.calculate_pose_score_from_camera()
        else:
            return self.calculate_pose_score_from_accelerometer()

    def calculate_pose_score_from_camera(self):
        """Calculate pose score using camera-based pose detection"""
        try:
            # Get camera frame and landmarks
            frame, landmarks = self.pose_detector.get_camera_frame()
            
            # Update camera surface for display
            if frame is not None:
                self.camera_surface = self.pose_detector.frame_to_pygame_surface(frame)
                self.camera_surface = pygame.transform.scale(self.camera_surface, (320, 240))
            
            # Check if pose is detected
            if landmarks is None:
                self.pose_feedback_text = "No pose detected"
                return 0
            
            # Get pose angles
            angles = self.pose_detector.get_pose_angles(landmarks)
            if angles is None:
                self.pose_feedback_text = "Could not calculate pose angles"
                return 0
            
            # Calculate similarity score
            score = self.pose_templates.calculate_pose_similarity(angles, self.current_pose_index)
            
            # Get detailed feedback
            self.pose_feedback_text = self.pose_templates.get_pose_feedback(angles, self.current_pose_index)
            
            # Store landmarks for stability checking
            self.previous_landmarks = landmarks
            
            return score
            
        except Exception as e:
            print(f"Error in camera pose detection: {e}")
            self.pose_feedback_text = f"Detection error: {str(e)[:50]}"
            return 0

    def calculate_pose_score_from_accelerometer(self):
        """Fallback scoring using accelerometer data simulation"""
        try:
            # Get sensor data (simulated)
            ax = data_temp.vals["AcX"][-1] if data_temp.vals["AcX"] else 0
            ay = data_temp.vals["AcY"][-1] if data_temp.vals["AcY"] else 0
            az = data_temp.vals["AcZ"][-1] if data_temp.vals["AcZ"] else 0
            gx = data_temp.vals["GyX"][-1] if data_temp.vals["GyX"] else 0
            gy = data_temp.vals["GyY"][-1] if data_temp.vals["GyY"] else 0
            gz = data_temp.vals["GyZ"][-1] if data_temp.vals["GyZ"] else 0

            # Calculate activity level
            sensor_activity = math.sqrt(ax**2 + ay**2 + az**2 + gx**2 + gy**2 + gz**2)
            elapsed = time.time() - self.start_time
            
            # Basic scoring algorithm
            base_score = 60 + (self.current_pose_index * 5)
            activity_factor = min(30, sensor_activity * 30)
            time_factor = min(15, elapsed * 1.5)
            
            score = base_score + activity_factor + time_factor + random.uniform(-15, 15)
            score = min(100, max(0, score))
            
            # Update feedback
            if score >= self.score_threshold:
                self.pose_feedback_text = "Good pose detected!"
            else:
                self.pose_feedback_text = "Keep adjusting your pose"
            
            # Debug output
            if int(elapsed) % 2 == 0:
                print(f"Pose {self.current_pose_index+1} Score: {score:.1f} (base:{base_score} + activity:{activity_factor:.1f} + time:{time_factor:.1f})")
            
            return score
            
        except Exception as e:
            print(f"Error in accelerometer scoring: {e}")
            return 0

    def update(self):
        """Update game state"""
        if not self.game_active or self.game_over:
            return
            
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if self.phase == "full":
            frame, landmarks = self.pose_detector.get_camera_frame()
            if frame is not None:
                self.camera_surface = self.pose_detector.frame_to_pygame_surface(frame)
                self.camera_surface = pygame.transform.scale(self.camera_surface, (320, 240))

            if landmarks:
                left_hand_raised = landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.LEFT_WRIST.value].y < \
                                landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                right_hand_raised = landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.RIGHT_WRIST.value].y < \
                                    landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y

                if left_hand_raised and right_hand_raised:
                    if self.pose_raise_start_time is None:
                        self.pose_raise_start_time = time.time()
                    elif time.time() - self.pose_raise_start_time >= 3:
                        self.phase = "corner"
                        self.start_time = time.time()
                        self.pose_raise_start_time = None
                else:
                    self.pose_raise_start_time = None

                    
        elif self.phase == "corner":
            # Continuously calculate score during pose detection phase
            self.current_score = self.calculate_pose_score()
            
            if elapsed >= self.pose_corner_duration:
                # Evaluate final score and provide feedback
                if self.current_score >= self.score_threshold:
                    self.current_feedback = self.success_image
                    self.total_score += self.current_score
                else:
                    self.current_feedback = self.fail_image
                    self.total_score += self.current_score // 2
                
                self.phase = "scoring"
                self.start_time = current_time
                
        elif self.phase == "scoring" and elapsed >= 3:
            # Move to next pose or end game
            self.current_pose_index += 1
            if self.current_pose_index < len(self.poses):
                self.start_new_pose()
            else:
                self.game_over = True

        elif self.phase == "preview":
            frame, landmarks = self.pose_detector.get_camera_frame()
            if frame is not None:
                self.camera_surface = self.pose_detector.frame_to_pygame_surface(frame)
                self.camera_surface = pygame.transform.scale(self.camera_surface, (800, 600))

            if landmarks:
                visibility = self.pose_detector.get_landmark_visibility(landmarks)
                left_visible = visibility.get("left_shoulder", False) and visibility.get("left_elbow", False) and visibility.get("left_ankle", False)
                right_visible = visibility.get("right_shoulder", False) and visibility.get("right_elbow", False) and visibility.get("right_ankle", False)

                left_hand_raised = landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.LEFT_WRIST.value].y < \
                                landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y
                right_hand_raised = landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.RIGHT_WRIST.value].y < \
                                    landmarks.landmark[self.pose_detector.mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y

                arms_up = left_visible and right_visible and left_hand_raised and right_hand_raised

                if arms_up:
                    if self.preview_raise_start_time is None:
                        self.preview_raise_start_time = time.time()
                    elif time.time() - self.preview_raise_start_time >= 3:
                        self.ready_confirmed = True
                        self.phase = "full"
                        self.start_new_pose()
                else:
                    self.preview_raise_start_time = None
                

    def draw(self):
        """Render the game"""
        self.window.blit(self.background_image, (0, 0))
        
        if not self.game_active:
            self.draw_start_screen()
        elif self.phase == "preview":
            self.draw_preview_screen()
        elif self.game_over:
            self.draw_game_over_screen()
        else:
            self.draw_game_screen()

    def draw_preview_screen(self):
        self.window.blit(self.background_image, (0, 0))

        if self.camera_surface:
            cam_rect = self.camera_surface.get_rect(center=(self.width // 2, self.height // 2 - 100))
            self.window.blit(self.camera_surface, cam_rect)
        else:
            cam_rect = pygame.Rect(0, 0, 0, 0)

        font_large = pygame.font.SysFont('Comic Sans MS', 45)
        instruction_color = (246, 203, 102)

        instructions = [
            "Place your laptop on a leveled chair-height surface",
            "Stand ~2 meters away from it",
            "Ensure your room is well-lit and your full body is visible",
            "Raise both arms above your shoulders to begin!"
        ]

        instruction_start_y = cam_rect.bottom + 30

        for i, line in enumerate(instructions):
            # Set color: red for the last line, otherwise the regular color
            color = (255, 0, 0) if i == len(instructions) - 1 else instruction_color
            text_surface = font_large.render(line, True, color)
            x = self.width // 2 - text_surface.get_width() // 2
            y = instruction_start_y + i * 50
            self.window.blit(text_surface, (x, y))


    def draw_start_screen(self):
        # Show background and title
        self.window.blit(self.background_image, (0, 0))
        title_text = pygame.font.SysFont('Comic Sans MS', 100).render("BALANCIMALS", True, (224, 139, 33))
        self.window.blit(title_text, (self.width//2 - title_text.get_width()//2, self.height//2 - 150))

        # Button
        self.window.blit(self.start_button_images[self.start_button_state], self.start_button_rect)

        # Instruction text
        instruction = pygame.font.SysFont('Comic Sans MS', 48).render("Balance training made fun!", True, (46, 15, 0))
        self.window.blit(instruction, (self.width//2 - instruction.get_width()//2, self.height//2 + 200))


    def draw_game_over_screen(self):
        """Draw game over screen"""
        # Game over text
        game_over_text = pygame.font.SysFont('Comic Sans MS', 100).render("GAME OVER", True, (246, 203, 102))
        score_text = pygame.font.SysFont('Comic Sans MS', 80).render(f"Final Score: {int(self.total_score)}", True, (246, 203, 102))
        
        self.window.blit(game_over_text, (self.width//2 - game_over_text.get_width()//2, self.height//3))
        self.window.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2))
        
        # Restart button
        restart_button = pygame.Rect(self.width//2 - 100, self.height*2//3, 200, 50)
        pygame.draw.rect(self.window, (100, 100, 255), restart_button)
        restart_text = pygame.font.SysFont('Comic Sans MS', 60).render("RESTART", True, (246, 203, 102))
        self.window.blit(restart_text, (self.width//2 - restart_text.get_width()//2,
                                      self.height*2//3 + 25 - restart_text.get_height()//2))

    def draw_game_screen(self):
        """Draw main game screen"""
        # Camera preview (if using pose detection)
        if self.use_pose_detection and self.camera_surface:
            preview_width = 400
            preview_height = 300
            self.camera_surface = pygame.transform.scale(self.camera_surface, (preview_width, preview_height))
            self.window.blit(self.camera_surface, (50, self.height // 2 - preview_height // 2))

            preview_label = self.font.render("Camera Preview", True, (246, 203, 102))
            self.window.blit(preview_label, (50, self.height // 2 - preview_height // 2 - 70))

        # Phase-specific rendering
        if self.phase == "full":
            self.draw_full_phase()
        elif self.phase == "corner" or self.phase == "scoring":
            self.draw_corner_phase()

        # Always visible UI elements
        self.draw_ui_elements()

    def draw_full_phase(self):
        """Draw pose in full screen during learning phase"""
        if self.current_pose and len(self.current_pose) >= 3:
            # Scale and display pose image
            scaled_pose = pygame.transform.scale(self.current_pose[0], (400, 400))
            self.window.blit(scaled_pose, (self.width//2 - 200, self.height//2 - 200))
            
            # Pose name and description
            name_text = pygame.font.SysFont('Comic Sans MS', 56).render(self.current_pose[1], True, (246, 203, 102))
            desc_text = pygame.font.SysFont('Comic Sans MS', 44).render(self.current_pose[2], True, (246, 203, 102))
            
            self.window.blit(name_text, (self.width//2 - name_text.get_width()//2, self.height//2 + 200))
            self.window.blit(desc_text, (self.width//2 - desc_text.get_width()//2, self.height//2 + 265))
            
            # Instruction
            instruction = pygame.font.SysFont('Comic Sans MS', 56).render("Arms above your shoulder when you're ready!", True, (255, 0, 0))
            self.window.blit(instruction, (30, self.height - 80))
            
            # # Countdown
            # elapsed = time.time() - self.start_time
            # countdown = max(0, self.pose_full_duration - int(elapsed))
            # countdown_text = pygame.font.SysFont('Comic Sans MS', 80).render(f"{countdown}", True, (255, 0, 0))
            # self.window.blit(countdown_text, (self.width//2 - countdown_text.get_width()//2, 50))

    def draw_corner_phase(self):
        """Draw pose in corner during detection phase"""
        if self.current_pose and len(self.current_pose) >= 1:
            # Small pose reference in corner
            scaled_pose = pygame.transform.scale(self.current_pose[0], (150, 150))
            self.window.blit(scaled_pose, (self.width - 170, 20))
            
            # Reference label
            ref_label = pygame.font.SysFont('Comic Sans MS', 25).render("Reference", True, (246, 203, 102))
            self.window.blit(ref_label, (self.width - 170, 175))

        # Feedback display
        self.window.blit(self.current_feedback, (self.width//2 - 100, self.height//2 - 100))

        if self.phase == "corner":
            # # Active pose detection
            # instruction = pygame.font.SysFont('Comic Sans MS', 30).render("Copy the pose now!", True, (0, 0, 255))
            # self.window.blit(instruction, (self.width//2 - instruction.get_width()//2, self.height//2 + 120))
            
            # Countdown
            elapsed = time.time() - self.start_time
            countdown = max(0, self.pose_corner_duration - int(elapsed))
            countdown_text = pygame.font.SysFont('Comic Sans MS', 60).render(f"{countdown}", True, (255, 0, 0))
            self.window.blit(countdown_text, (self.width//2 - countdown_text.get_width()//2, 50))
            
            # Current score
            score_text = self.font.render(f"Current Score: {int(self.current_score)}", True, (246, 203, 102))
            self.window.blit(score_text, (20, 60))
            
            # Pose feedback
            if self.pose_feedback_text:
                self.draw_pose_feedback()
                
        else:  # scoring phase
            # Result display
            result_text = pygame.font.SysFont('Comic Sans MS', 40).render(
                "GREAT JOB!" if self.current_feedback == self.success_image else "TRY HARDER!",
                True, (0, 150, 0) if self.current_feedback == self.success_image else (150, 0, 0))
            self.window.blit(result_text, (self.width//2 - result_text.get_width()//2, self.height//2 + 120))
            
            # Final score for this pose
            final_score_text = self.font.render(f"Pose Score: {int(self.current_score)}", True, (246, 203, 102))
            self.window.blit(final_score_text, (self.width//2 - final_score_text.get_width()//2, self.height//2 + 160))

    def draw_pose_feedback(self):
        """Draw detailed pose feedback"""
        if not self.pose_feedback_text:
            return
        
        # Use larger font if it's a special pose
        feedback_lines = self.pose_feedback_text.split("\n")
        font_size = 55
        feedback_font = pygame.font.SysFont('Comic Sans MS', font_size)
            
        feedback_lines = self.pose_feedback_text.split("\n")
        y_offset = self.height - 250
        
        for i, line in enumerate(feedback_lines[:4]):  # Limit to 4 lines
            if line.strip():
                feedback_render = feedback_font.render(line, True, (246, 203, 102))
                x_pos = self.width // 2 - feedback_render.get_width() // 2
                self.window.blit(feedback_render, (x_pos, y_offset + i * 60))

    def draw_ui_elements(self):
        """Draw always-visible UI elements"""
        # Total score
        score_text = self.font.render(f"Total Score: {int(self.total_score)}", True, (246, 203, 102))
        self.window.blit(score_text, (20, 20))
        
        # Progress
        progress_text = self.font.render(f"Pose {self.current_pose_index + 1}/{len(self.poses)}", True, (246, 203, 102))
        self.window.blit(progress_text, (self.width - 200, self.height - 70))
        
        # # Detection method
        # method_text = "Camera Detection" if self.use_pose_detection else "Simulated Data"
        # method_color = (0, 150, 0) if self.use_pose_detection else (150, 0, 0)
        # method_render = self.font.render(method_text, True, method_color)
        # self.window.blit(method_render, (self.width//2 - method_render.get_width()//2, self.height - 30))

    def handle_events(self, events):
        mouse_pos = pygame.mouse.get_pos()
        hovering = self.start_button_rect.collidepoint(mouse_pos)

        if not self.game_active:
            self.start_button_state = "hover" if hovering else "default"

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if hovering and not self.game_active:
                    self.start_button_state = "clicked"

            elif event.type == pygame.MOUSEBUTTONUP:
                if hovering and not self.game_active:
                    self.start_game()
                    self.start_button_state = "default"

            elif self.game_over:
                restart_button = pygame.Rect(self.width//2 - 100, self.height*2//3, 200, 50)
                if event.type == pygame.MOUSEBUTTONDOWN and restart_button.collidepoint(mouse_pos):
                    self.start_game()


    def display(self):
        """Main display method"""
        self.update()
        self.draw()

    def cleanup(self):
        """Clean up resources"""
        if self.use_pose_detection and self.pose_detector:
            self.pose_detector.release()