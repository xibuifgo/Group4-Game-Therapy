import pygame
import sys
import random
import data_temp
import time
import math
from pose_loader import load_poses
from bear_animator import BearAnimator
import threading
import pyttsx3


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

DEV_MODE = True

class PoseGame:
    def __init__(self, window, clock):
        self.window = window
        self.clock = clock
        self.width, self.height = window.get_size()
        self.game_active = False
        self.current_pose_index = 0
        self.game_over = False
        self.total_score = 0

        font_small_size = int(self.height * 0.03)   # ~3% of height
        font_normal_size = int(self.height * 0.045) # ~4.5%
        font_large_size = int(self.height * 0.07)   # ~7%
        font_xlarge_size = int(self.height * 0.1)   # ~10%

        self.font_small = pygame.font.Font("assets/fonts/VT323-Regular.ttf", font_small_size)
        self.font = pygame.font.Font("assets/fonts/VT323-Regular.ttf", font_normal_size)
        self.font_large = pygame.font.Font("assets/fonts/VT323-Regular.ttf", font_large_size)
        self.font_xlarge = pygame.font.Font("assets/fonts/VT323-Regular.ttf", font_xlarge_size)

        self.bear_animator = BearAnimator(self.width, self.height)

        self.pose_full_duration = 3
        self.pose_corner_duration = 10
        self.current_time = 0
        self.start_time = 0
        self.phase = "waiting"
        self.phase = "preview"
        self.ready_confirmed = False
        self.preview_raise_start_time = None
        self.current_bear_state = "sleeping"  # or "neutral" if you have one

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
        self.success_image = self.create_feedback_image("success")
        self.fail_image = self.create_feedback_image("fail")

        # Scoring
        self.score_threshold = 70
        self.current_score = 0

        # UI elements
        button_raw = {
            "default": pygame.image.load("assets/images/start_default.png").convert_alpha(),
            "hover": pygame.image.load("assets/images/start_hover.png").convert_alpha(),
            "clicked": pygame.image.load("assets/images/start_clicked.png").convert_alpha()
        }

        original_width, original_height = button_raw["default"].get_size()
        aspect_ratio = original_width / original_height

        button_width = int(self.width * 0.15)
        button_height = int(button_width / aspect_ratio)

        # Resize all button states to match
        self.start_button_images = {
            state: pygame.transform.scale(img, (button_width, button_height))
            for state, img in button_raw.items()
        }

        self.start_button_rect = self.start_button_images["default"].get_rect(center=(self.width // 2, int(self.height * 0.6)))


        self.background_image = pygame.image.load("assets/images/background_2.png").convert()
        self.background_image = pygame.transform.scale(self.background_image, (self.width, self.height))

        self.logo_image = pygame.image.load("assets/images/balancimals_logo.png").convert_alpha()
        logo_width = int(self.width * 0.5)
        logo_height = int(logo_width * self.logo_image.get_height() / self.logo_image.get_width())
        self.logo_image = pygame.transform.scale(self.logo_image, (logo_width, logo_height))


        # State variables
        self.mock_activity_level = 0
        self.camera_surface = None
        self.pose_feedback_text = ""
        self.previous_landmarks = None

        self.bear_states = {
            "sleeping": pygame.image.load("assets/images/sleeping_bear.png").convert_alpha(),
            "waking": pygame.image.load("assets/images/waking_bear.PNG").convert_alpha(),
            "angry": pygame.image.load("assets/images/angry_bear.PNG").convert_alpha(),
        }

        # TTS setup
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_enabled = True
        except Exception as e:
            print("TTS init failed:", e)
            self.tts_enabled = False

        # Audio setup
        pygame.mixer.init()  # call before loading any music
        self.music_files = {
            "start": "assets/music/start.mp3",
            "setup": "assets/music/setup.mp3",
            "prep": "assets/music/prep.mp3",
            "pose": "assets/music/pose.mp3"
        }
        self.current_music = None


        # Flags to avoid repeating speech
        self.preview_spoken = False
        self.pose_intro_spoken = False
        self.arms_instruction_spoken = False


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

    def wrap_text(self, text, font, max_width):
        """Wrap text into a list of lines that fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        return lines
    
    def play_music(self, key, loop=-1, fade_ms=500):
        """Switch background track to `self.music_files[key]`."""
        if self.current_music == key:
            return
        # fade out old music
        pygame.mixer.music.fadeout(fade_ms)
        # load & play the new track
        pygame.mixer.music.load(self.music_files[key])
        pygame.mixer.music.play(loop, fade_ms=fade_ms)
        self.current_music = key

    
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
        return image

    def start_game(self):
        """Initialize game state"""
        self.game_active = True
        self.current_pose_index = 0
        self.total_score = 0
        self.game_over = False
        self.mock_activity_level = 0
        self.previous_landmarks = None
        self.preview_spoken = False
        self.pose_intro_spoken = False
        self.arms_instruction_spoken = False

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
        self.pose_feedback_text = ""
        self.mock_activity_level += 1
        
        # Reset speech flags for this pose
        self.pose_intro_spoken = False
        self.arms_instruction_spoken = False

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
        
    def speak_text(self, text, delay: float = 0.0):
        if not self.tts_enabled: return

        def _worker(msg, wait):
            if wait > 0: time.sleep(wait)
            self.tts_engine.say(msg)
            self.tts_engine.runAndWait()

        threading.Thread(target=_worker, args=(text, delay), daemon=True).start()

    def calculate_pose_score_from_accelerometer(self):
        """Override scoring with phase-based cycling for animation testing"""
        elapsed = time.time() - self.start_time
        phase = int(elapsed // 3) % 3

        if phase == 0:
            score = 85  # sleeping
            self.pose_feedback_text = "🛌 Sleeping (score 85)"
        elif phase == 1:
            score = 65  # waking
            self.pose_feedback_text = "👀 Waking (score 65)"
        else:
            score = 30  # angry
            self.pose_feedback_text = "😠 Angry (score 30)"

        print(f"[DEBUG] Phase: {phase}, Forced Score: {score}")
        return score



    # def calculate_pose_score_from_accelerometer(self):
    #     """Fallback scoring using accelerometer data simulation"""
    #     try:
    #         # Get sensor data (simulated)
    #         ax = data_temp.vals["AcX"][-1] if data_temp.vals["AcX"] else 0
    #         ay = data_temp.vals["AcY"][-1] if data_temp.vals["AcY"] else 0
    #         az = data_temp.vals["AcZ"][-1] if data_temp.vals["AcZ"] else 0
    #         gx = data_temp.vals["GyX"][-1] if data_temp.vals["GyX"] else 0
    #         gy = data_temp.vals["GyY"][-1] if data_temp.vals["GyY"] else 0
    #         gz = data_temp.vals["GyZ"][-1] if data_temp.vals["GyZ"] else 0

    #         # Calculate activity level
    #         sensor_activity = math.sqrt(ax**2 + ay**2 + az**2 + gx**2 + gy**2 + gz**2)
    #         elapsed = time.time() - self.start_time
            
    #         # Basic scoring algorithm
    #         base_score = 60 + (self.current_pose_index * 5)
    #         activity_factor = min(30, sensor_activity * 30)
    #         time_factor = min(15, elapsed * 1.5)
            
    #         score = base_score + activity_factor + time_factor + random.uniform(-15, 15)
    #         score = min(100, max(0, score))
            
    #         # Update feedback
    #         if score >= self.score_threshold:
    #             self.pose_feedback_text = "Good pose detected!"
    #         else:
    #             self.pose_feedback_text = "Keep adjusting your pose"
            
    #         # Debug output
    #         if int(elapsed) % 2 == 0:
    #             print(f"Pose {self.current_pose_index+1} Score: {score:.1f} (base:{base_score} + activity:{activity_factor:.1f} + time:{time_factor:.1f})")
            
    #         return score
            
    #     except Exception as e:
    #         print(f"Error in accelerometer scoring: {e}")
    #         return 0

    def update(self):
        """Update game state"""
        if not self.game_active or self.game_over:
            return
            
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if self.phase == "full":
            # Speak the arms instruction after 2.5 seconds if not already spoken
            if not self.arms_instruction_spoken and elapsed >= 0.5:
                # Speak once, half a second after entering full phase
                self.speak_text("Raise both arms above your shoulders to begin!")
                self.arms_instruction_spoken = True

            
            frame, landmarks = self.pose_detector.get_camera_frame()
            if frame is not None:
                self.camera_surface = self.pose_detector.frame_to_pygame_surface(frame)
                preview_width = int(self.width * 0.25)
                preview_height = int(self.height * 0.3)
                self.camera_surface = pygame.transform.scale(self.camera_surface, (preview_width, preview_height))

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
            self.bear_animator.update(self.current_score)
            
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
            self.bear_animator.update(self.current_score)
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
        self.play_music("setup")
        self.window.blit(self.background_image, (0, 0))

        if self.camera_surface:
            cam_rect = self.camera_surface.get_rect(center=(self.width // 2, self.height // 2 - 100))
            border_rect = cam_rect.inflate(10, 10)
            pygame.draw.rect(self.window, (46, 15, 0), border_rect, width=4, border_radius=6)
            self.window.blit(self.camera_surface, cam_rect)

        else:
            cam_rect = pygame.Rect(0, 0, 0, 0)

        font_large = self.font
        instruction_color = (246, 203, 102)

        instructions = [
            "Place your laptop on a leveled chair-height surface",
            "Stand ~2 meters away from it",
            "Ensure your room is well-lit and your full body is visible",
            "Raise both arms above your shoulders to begin!"
        ]

        instruction_start_y = cam_rect.bottom + int(self.height * 0.02)

        for i, line in enumerate(instructions):
            color = (158, 209, 242) if i == len(instructions) - 1 else instruction_color
            x = self.width // 2
            y = instruction_start_y + i * int(self.height * 0.05)
            self.draw_text_with_outline(self.window, line, font_large, x - font_large.size(line)[0] // 2, y, color)

        if not self.preview_spoken:
            prompt = "Place your laptop on a leveled chair-height surface. " \
                    "Stand two meters away from it. " \
                    "Ensure your room is well lit and your full body is visible. " \
                    "Raise both arms above your shoulders to begin!"
            self.speak_text(prompt)
            self.preview_spoken = True

        # Draw circle if arms are raised
        if self.preview_raise_start_time:
            center = (45, self.height - 45)
            self.draw_ready_circle(center, 40, 3, self.preview_raise_start_time)

    def draw_start_screen(self):
        self.play_music("start")
        # Show background and title
        self.window.blit(self.background_image, (0, 0))
        logo_rect = self.logo_image.get_rect(center=(self.width // 2, self.height // 2 - 150))
        self.window.blit(self.logo_image, logo_rect)

        # Button
        self.window.blit(self.start_button_images[self.start_button_state], self.start_button_rect)

        # Instruction text
        instruction = self.font.render("Balance training made fun!", True, (246, 203, 102))
        self.window.blit(instruction, (self.width//2 - instruction.get_width()//2, self.height//2 + 200))

    def draw_game_over_screen(self):
        """Draw game over screen"""
        # Game over text
        game_over_text = self.font_xlarge.render("GAME OVER", True, (246, 203, 102))
        score_text = self.font_large.render(f"Final Score: {int(self.total_score)}", True, (246, 203, 102))
        
        self.window.blit(game_over_text, (self.width//2 - game_over_text.get_width()//2, self.height//3))
        self.window.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2))
        
        # Restart button
        button_width = int(self.width * 0.25)
        button_height = int(self.height * 0.08)
        button_x = self.width // 2 - button_width // 2
        button_y = int(self.height * 0.7)

        restart_button = pygame.Rect(button_x, button_y, button_width, button_height)
        pygame.draw.rect(self.window, (100, 100, 255), restart_button)
        restart_text = self.font.render("RESTART", True, (246, 203, 102))
        text_x = self.width // 2 - restart_text.get_width() // 2
        text_y = restart_button.centery - restart_text.get_height() // 2
        self.window.blit(restart_text, (text_x, text_y))

    def draw_game_screen(self):
        """Draw main game screen"""
        # Camera preview (if using pose detection)
        if self.use_pose_detection and self.camera_surface:
            preview_width = int(self.width * 0.25)
            preview_height = int(self.height * 0.3)
            self.camera_surface = pygame.transform.scale(self.camera_surface, (preview_width, preview_height))

            cam_x = int(self.width * 0.02)
            cam_y = int(self.height * 0.1)
            cam_rect = pygame.Rect(cam_x, cam_y, preview_width, preview_height)

            # Draw border
            pygame.draw.rect(self.window, (46, 15, 0), cam_rect.inflate(10, 10), width=4, border_radius=6)

            # Draw camera
            self.window.blit(self.camera_surface, cam_rect)

        # Phase-specific rendering
        if self.phase == "full":
            self.play_music("prep")
            # Always draw the full-pose screen
            self.draw_full_phase()

            # Show instruction overlay until arms are raised for 3s
            if self.pose_raise_start_time is None or (time.time() - self.pose_raise_start_time < 3):
                instruction_text = "Raise both arms above your shoulders to begin!"
                font_large = self.font_large
                text_surface = font_large.render(instruction_text, True, (158, 209, 242))
                x = self.width // 2 - text_surface.get_width() // 2
                y = self.height - 100
                self.draw_text_with_outline(self.window, instruction_text,
                                           font_large, x, y, (158, 209, 242))

        # Arms-up indicator before each pose
        if self.pose_raise_start_time:
            center = (45, self.height - 45)
            self.draw_ready_circle(center, 40, 3, self.pose_raise_start_time)

        if self.phase == "corner" or self.phase == "scoring":
            self.play_music("pose")
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

            # Pose name
            name_font = self.font_large
            name_text = self.current_pose[1]
            name_x = self.width // 2 - name_font.size(name_text)[0] // 2
            name_y = int(pose_y - name_font.size(name_text)[1] - self.height * 0.02)
            self.draw_text_with_outline(self.window, name_text, name_font, name_x, name_y, (246, 203, 102))

            # Pose description
            desc_text = self.current_pose[2]
            desc_font = self.font_large
            wrapped_lines = self.wrap_text(desc_text, desc_font, max_width=int(self.width * 0.9))  # up to 90% screen width

            start_y = pose_y + scaled_pose.get_height() + int(self.height * 0.02)
            line_spacing = int(self.height * 0.06)

            for i, line in enumerate(wrapped_lines):
                line_x = self.width // 2 - desc_font.size(line)[0] // 2
                line_y = start_y + i * line_spacing
                self.draw_text_with_outline(self.window, line, desc_font, line_x, line_y, (246, 203, 102))

    def draw_corner_phase(self):
        """Draw pose in corner during detection phase"""

        if self.current_pose and len(self.current_pose) >= 1:
            # Small pose reference in corner
            scaled_pose = pygame.transform.scale(self.current_pose[0], (150, 150))
            pose_rect = scaled_pose.get_rect(topleft=(self.width - 170, 20))

            # Draw background box (frame)
            pygame.draw.rect(self.window, (46, 15, 0), pose_rect.inflate(10, 10), border_radius=8)
            self.window.blit(scaled_pose, pose_rect)

            # Reference label
            ref_label = self.font_small.render("Reference", True, (246, 203, 102))
            self.window.blit(ref_label, (pose_rect.x, pose_rect.bottom + 5))

        if self.phase == "corner":
            bear_center = (self.width // 2, self.height - int(self.height * 0.25))
            self.bear_animator.draw(self.window, center_pos=bear_center)

            # Countdown
            elapsed = time.time() - self.start_time
            countdown = max(0, self.pose_corner_duration - int(elapsed))
            countdown_text = self.font_xlarge.render(f"{countdown}", True, (255, 0, 0))
            self.window.blit(countdown_text, (self.width//2 - countdown_text.get_width()//2, 50))

            # Pose feedback
            if self.pose_feedback_text:
                self.draw_pose_feedback()

        else:  # scoring phase
            # Result display
            result_text = self.font_small.render(
                "GREAT JOB!" if self.current_feedback == self.success_image else "TRY HARDER!",
                True, (0, 150, 0) if self.current_feedback == self.success_image else (150, 0, 0)
            )
            self.window.blit(result_text, (self.width//2 - result_text.get_width()//2, self.height//2 + 120))

            # Final score for this pose
            final_score_text = self.font.render(f"Pose Score: {int(self.current_score)}", True, (246, 203, 102))
            self.window.blit(final_score_text, (self.width//2 - final_score_text.get_width()//2, self.height//2 + 160))


    def draw_pose_feedback(self):
        """Draw detailed pose feedback"""
        if not self.pose_feedback_text:
            return

        feedback_lines = self.pose_feedback_text.split("\n")
        feedback_font = self.font_large

        y_offset = int(self.height * 0.35)


        for i, line in enumerate(feedback_lines[:4]):
            if line.strip():
                x_pos = self.width // 2 - feedback_font.size(line)[0] // 2
                y_pos = y_offset + i * int(self.height * 0.06)
                self.draw_text_with_outline(self.window, line, feedback_font, x_pos, y_pos, (246, 203, 102))

    def draw_ui_elements(self):
        """Draw context-specific UI elements"""
        padding_x = int(self.width * 0.015)
        padding_y = int(self.height * 0.01)
        font = self.font  # standardized font

        if self.phase in ["full", "corner"]:
            score_text = font.render(f"Pose Score: {int(self.current_score)}", True, (246, 203, 102))
            box_width = score_text.get_width() + padding_x * 2
            box_height = score_text.get_height() + padding_y * 2

            # Align camera preview with bottom of this box
            cam_top_y = int(self.height * 0.1)
            box_y = cam_top_y - box_height
            box_rect = pygame.Rect(padding_x, box_y, box_width, box_height)

            pygame.draw.rect(self.window, (46, 15, 0), box_rect, border_radius=10)
            pygame.draw.rect(self.window, (46, 15, 0), box_rect, width=3, border_radius=10)
            self.window.blit(score_text, (box_rect.x + padding_x, box_rect.y + padding_y))

        elif self.phase == "scoring":
            total_text = self.font.render(f"Total Score: {int(self.total_score)}", True, (246, 203, 102))
            box_width = total_text.get_width() + padding_x * 2
            box_height = total_text.get_height() + padding_y * 2

            cam_top_y = int(self.height * 0.1)  # Same as camera preview Y
            box_y = cam_top_y - box_height     # So box's bottom aligns with camera top

            box_rect = pygame.Rect(padding_x, box_y, box_width, box_height)

            pygame.draw.rect(self.window, (46, 15, 0), box_rect, border_radius=10)
            pygame.draw.rect(self.window, (46, 15, 0), box_rect, width=3, border_radius=10)
            self.window.blit(total_text, (box_rect.x + padding_x, box_rect.y + padding_y))


        # Pose progress (always shown)
        progress_text = font.render(f"Pose {self.current_pose_index + 1}/{len(self.poses)}", True, (246, 203, 102))
        self.window.blit(progress_text, (self.width - int(self.width * 0.18), self.height - int(self.height * 0.05)))

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
                button_width = int(self.width * 0.25)
                button_height = int(self.height * 0.08)
                button_x = self.width // 2 - button_width // 2
                button_y = int(self.height * 0.7)
                restart_button = pygame.Rect(button_x, button_y, button_width, button_height)

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