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

DEV_MODE = False

class PoseGame:
    def __init__(self, window, clock):
        self.window = window
        self.clock = clock
        self.width, self.height = window.get_size()
        self.game_active = False
        self.current_pose_index = 0
        self.game_over = False
        self.total_score = 0

        self.pixel_font = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 58)
        self.pixel_font_small = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 40)
        self.pixel_font_large = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 90)

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
        self.font = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 48)
        self.feedback_font = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 40)

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

    def draw_text_with_outline(self, surface, text, font, x, y, text_color, outline_color=(0, 0, 0), outline_width=2):
        # Draw outline
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                if dx != 0 or dy != 0:
                    outline_surface = font.render(text, True, outline_color)
                    surface.blit(outline_surface, (x + dx, y + dy))
        # Draw center text
        text_surface = font.render(text, True, text_color)
        surface.blit(text_surface, (x, y))

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
            font = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 100)
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
        if DEV_MODE:
            self.phase = "full"
            self.start_new_pose()
        else:
            self.phase = "preview"
        self.ready_confirmed = False  

    def draw_ready_circle(self, center, radius, duration, start_time):
        if start_time is None:
            return
        elapsed = time.time() - start_time
        progress = min(elapsed / duration, 1)

        # Draw background circle (grey)
        pygame.draw.circle(self.window, (100, 100, 100), center, radius, 5)

        # Draw progress arc (yellow/gold)
        end_angle = -math.pi / 2 + 2 * math.pi * progress
        points = [center]
        for i in range(0, int(360 * progress) + 1, 2):
            angle = -math.pi / 2 + math.radians(i)
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            points.append((x, y))
        if len(points) > 2:
            pygame.draw.polygon(self.window, (246, 203, 102), points)


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
            border_rect = cam_rect.inflate(10, 10)
            pygame.draw.rect(self.window, (46, 15, 0), border_rect, width=4, border_radius=6)
            self.window.blit(self.camera_surface, cam_rect)

        else:
            cam_rect = pygame.Rect(0, 0, 0, 0)

        font_large = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 45)
        instruction_color = (246, 203, 102)

        instructions = [
            "Place your laptop on a leveled chair-height surface",
            "Stand ~2 meters away from it",
            "Ensure your room is well-lit and your full body is visible",
            "Raise both arms above your shoulders to begin!"
        ]

        instruction_start_y = cam_rect.bottom + 30

        for i, line in enumerate(instructions):
            color = (255, 0, 0) if i == len(instructions) - 1 else instruction_color
            x = self.width // 2
            y = instruction_start_y + i * 50
            self.draw_text_with_outline(self.window, line, font_large, x - font_large.size(line)[0] // 2, y, color)


        # Draw circle if arms are raised
        if self.preview_raise_start_time:
            center = (45, self.height - 45)
            self.draw_ready_circle(center, 40, 3, self.preview_raise_start_time)



    def draw_start_screen(self):
        # Show background and title
        self.window.blit(self.background_image, (0, 0))
        title_text = title_text = self.pixel_font_large.render("BALANCIMALS", True, (246, 203, 102))
        self.window.blit(title_text, (self.width//2 - title_text.get_width()//2, self.height//2 - 150))

        # Button
        self.window.blit(self.start_button_images[self.start_button_state], self.start_button_rect)

        # Instruction text
        instruction = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 48).render("Balance training made fun!", True, (46, 15, 0))
        self.window.blit(instruction, (self.width//2 - instruction.get_width()//2, self.height//2 + 200))


    def draw_game_over_screen(self):
        """Draw game over screen"""
        # Game over text
        game_over_text = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 100).render("GAME OVER", True, (246, 203, 102))
        score_text = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 80).render(f"Final Score: {int(self.total_score)}", True, (246, 203, 102))
        
        self.window.blit(game_over_text, (self.width//2 - game_over_text.get_width()//2, self.height//3))
        self.window.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2))
        
        # Restart button
        restart_button = pygame.Rect(self.width//2 - 100, self.height*2//3, 200, 50)
        pygame.draw.rect(self.window, (100, 100, 255), restart_button)
        restart_text = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 60).render("RESTART", True, (246, 203, 102))
        self.window.blit(restart_text, (self.width//2 - restart_text.get_width()//2,
                                      self.height*2//3 + 25 - restart_text.get_height()//2))

    def draw_game_screen(self):
        """Draw main game screen"""
        # Camera preview (if using pose detection)
        if self.use_pose_detection and self.camera_surface:
            preview_width = 400
            preview_height = 300
            self.camera_surface = pygame.transform.scale(self.camera_surface, (preview_width, preview_height))

            cam_x = 20
            cam_y = 85
            cam_rect = pygame.Rect(cam_x, cam_y, preview_width, preview_height)

            # Draw border
            pygame.draw.rect(self.window, (46, 15, 0), cam_rect.inflate(10, 10), width=4, border_radius=6)

            # Draw camera
            self.window.blit(self.camera_surface, cam_rect)

        # Phase-specific rendering
        if self.phase == "full":
            self.draw_full_phase()

            # Show instruction if arms aren't raised for full 3 seconds yet
            if self.pose_raise_start_time is None or (time.time() - self.pose_raise_start_time < 3):
                instruction_text = "Raise both arms above your shoulders to begin!"
                font_large = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 45)
                text_surface = font_large.render(instruction_text, True, (255, 0, 0))
                x = self.width // 2 - text_surface.get_width() // 2
                y = self.height - 100
                self.draw_text_with_outline(self.window, instruction_text, font_large, x, y, (255, 0, 0))

        # Arms-up indicator before each pose
        if self.pose_raise_start_time:
            center = (45, self.height - 45)
            self.draw_ready_circle(center, 40, 3, self.pose_raise_start_time)

        if self.phase == "corner" or self.phase == "scoring":
            self.draw_corner_phase()

        # Always visible UI elements
        self.draw_ui_elements()

    def draw_full_phase(self):
        """Draw pose in full screen during learning phase"""
        if self.current_pose and len(self.current_pose) >= 3:
            scaled_pose = pygame.transform.scale(self.current_pose[0], (400, 400))
            pose_x = self.width // 2 - 200
            pose_y = self.height // 2 - 200
            self.window.blit(scaled_pose, (pose_x, pose_y))

            # Text positions
            name_text = self.pixel_font.render(self.current_pose[1], True, (246, 203, 102))
            name_x = self.width // 2 - name_text.get_width() // 2
            name_y = pose_y - name_text.get_height() - 10  # Just above pose image
            self.draw_text_with_outline(self.window, self.current_pose[1], self.pixel_font, name_x, name_y, (246, 203, 102))

            # Description still below the image
            desc_text = self.pixel_font.render(self.current_pose[2], True, (246, 203, 102))
            desc_x = self.width // 2 - desc_text.get_width() // 2
            desc_y = pose_y + 400 + 15
            self.draw_text_with_outline(self.window, self.current_pose[2], self.pixel_font, desc_x, desc_y, (246, 203, 102))




    def draw_corner_phase(self):
        """Draw pose in corner during detection phase"""
        if self.current_pose and len(self.current_pose) >= 1:
            # Small pose reference in corner
            scaled_pose = pygame.transform.scale(self.current_pose[0], (150, 150))
            pose_rect = scaled_pose.get_rect(topleft=(self.width - 170, 20))

            # Draw background box (frame)
            pygame.draw.rect(self.window, (46, 15, 0), pose_rect.inflate(10, 10), border_radius=8)  # Optional border radius
            self.window.blit(scaled_pose, pose_rect)

            # Reference label
            ref_label = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 25).render("Reference", True, (246, 203, 102))
            self.window.blit(ref_label, (pose_rect.x, pose_rect.bottom + 5))

            # Feedback display
            self.window.blit(self.current_feedback, (self.width//2 - 100, self.height//2 - 100))

        if self.phase == "corner":
        
            # Countdown
            elapsed = time.time() - self.start_time
            countdown = max(0, self.pose_corner_duration - int(elapsed))
            countdown_text = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 60).render(f"{countdown}", True, (255, 0, 0))
            self.window.blit(countdown_text, (self.width//2 - countdown_text.get_width()//2, 50))
            
            # Pose feedback
            if self.pose_feedback_text:
                self.draw_pose_feedback()
                
        else:  # scoring phase
            # Result display
            result_text = pygame.font.Font("assets/fonts/VT323-Regular.ttf", 40).render(
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
        feedback_font = pygame.font.Font("assets/fonts/VT323-Regular.ttf", font_size)
            
        feedback_lines = self.pose_feedback_text.split("\n")
        y_offset = self.height - 250
        
        for i, line in enumerate(feedback_lines[:4]):  # Limit to 4 lines
            if line.strip():
                x_pos = self.width // 2 - feedback_font.size(line)[0] // 2
                y_pos = y_offset + i * 60
                self.draw_text_with_outline(self.window, line, feedback_font, x_pos, y_pos, (246, 203, 102))

    def draw_ui_elements(self):
        """Draw context-specific UI elements"""
        # FONT
        font = self.font
        padding = 20

        if self.phase in ["full", "corner"]:
            # Show current pose score (top-left)
            score_text = font.render(f"Pose Score: {int(self.current_score)}", True, (246, 203, 102))
            box_width = score_text.get_width() + padding * 2
            box_height = score_text.get_height() + padding
            box_rect = pygame.Rect(15, 15, box_width, box_height)

            pygame.draw.rect(self.window, (40, 40, 40), box_rect, border_radius=10)
            pygame.draw.rect(self.window, (46, 15, 0), box_rect, width=3, border_radius=10)
            self.window.blit(score_text, (box_rect.x + padding, box_rect.y + (box_height - score_text.get_height()) // 2))

        elif self.phase == "scoring":
            # Show total score after pose is completed
            total_text = font.render(f"Total Score: {int(self.total_score)}", True, (246, 203, 102))
            box_width = total_text.get_width() + padding * 2
            box_height = total_text.get_height() + padding
            box_rect = pygame.Rect(15, 15, box_width, box_height)

            pygame.draw.rect(self.window, (40, 40, 40), box_rect, border_radius=10)
            pygame.draw.rect(self.window, (46, 15, 0), box_rect, width=3, border_radius=10)
            self.window.blit(total_text, (box_rect.x + padding, box_rect.y + (box_height - total_text.get_height()) // 2))

        # Pose progress (always shown)
        progress_text = font.render(f"Pose {self.current_pose_index + 1}/{len(self.poses)}", True, (246, 203, 102))
        self.window.blit(progress_text, (self.width - 200, self.height - 70))


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