import pygame
import sys
import random
import data_temp
import time
import math
from pose_loader import load_poses

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

        self.poses = load_poses()
        self.current_pose = None

        self.success_image = self.create_feedback_image("success")
        self.fail_image = self.create_feedback_image("fail")
        self.neutral_image = self.create_feedback_image("neutral")
        
        self.current_feedback = self.neutral_image

        self.score_threshold = 70
        self.current_score = 0

        self.font = pygame.font.SysFont('Arial', 24)

        self.start_button = pygame.Rect(self.width//2 - 100, self.height//2 - 25, 200, 50)
        self.button_text = pygame.font.SysFont('Arial', 30).render("START", True, (0, 0, 0))

        self.mock_activity_level = 0
    
    def create_feedback_image(self, feedback_type):
        """Create feedback images with visual indicators of success/failure"""
        image = pygame.Surface((200, 200))
        
        if feedback_type == "success":
            image.fill((0, 200, 0))
            pygame.draw.lines(image, (255, 255, 255), False, 
                             [(50, 100), (90, 150), (150, 70)], 10)
        elif feedback_type == "fail":
            image.fill((200, 0, 0))
            pygame.draw.line(image, (255, 255, 255), (50, 50), (150, 150), 10)
            pygame.draw.line(image, (255, 255, 255), (150, 50), (50, 150), 10)
        else: 

            image.fill((150, 150, 150))
            font = pygame.font.SysFont('Arial', 100)
            text = font.render("?", True, (255, 255, 255))
            image.blit(text, (80, 50))
            
        return image
    
    def start_game(self):
        self.game_active = True
        self.current_pose_index = 0
        self.total_score = 0
        self.game_over = False
        self.mock_activity_level = 0
        self.start_new_pose()
    
    def start_new_pose(self):
        if self.current_pose_index >= len(self.poses):
            self.game_over = True
            return
            
        self.current_pose = self.poses[self.current_pose_index]
        self.phase = "full"
        self.start_time = time.time()
        self.current_score = 0
        self.current_feedback = self.neutral_image
        
        self.mock_activity_level += 1
    
    def calculate_pose_score(self):
        """
        Enhanced mock scoring function that generates more interesting scores 
        based on the current time and mock activity level.
        """
        ax = data_temp.vals["AcX"][-1] if data_temp.vals["AcX"] else 0
        ay = data_temp.vals["AcY"][-1] if data_temp.vals["AcY"] else 0
        az = data_temp.vals["AcZ"][-1] if data_temp.vals["AcZ"] else 0
        gx = data_temp.vals["GyX"][-1] if data_temp.vals["GyX"] else 0
        gy = data_temp.vals["GyY"][-1] if data_temp.vals["GyY"] else 0
        gz = data_temp.vals["GyZ"][-1] if data_temp.vals["GyZ"] else 0
        
        sensor_activity = math.sqrt(ax**2 + ay**2 + az**2 + gx**2 + gy**2 + gz**2)
        
        elapsed = time.time() - self.start_time

        base_score = 60 + (self.current_pose_index * 5)
        
        activity_factor = min(30, sensor_activity * 30)
        
        time_factor = min(15, elapsed * 1.5)
        
        score = base_score + activity_factor + time_factor + random.uniform(-15, 15)

        score = min(100, max(0, score))

        if int(elapsed) % 2 == 0:
            print(f"Pose {self.current_pose_index+1} Score: {score:.1f} (base:{base_score} + activity:{activity_factor:.1f} + time:{time_factor:.1f})")
        
        return score
    
    def update(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        if not self.game_active:
            return
            
        if self.game_over:
            return
            
        if self.phase == "full":
            if elapsed >= self.pose_full_duration:
                self.phase = "corner"
                self.start_time = current_time
                
        elif self.phase == "corner":
            self.current_score = self.calculate_pose_score()
            
            if elapsed >= self.pose_corner_duration:
                if self.current_score >= self.score_threshold:
                    self.current_feedback = self.success_image
                    self.total_score += self.current_score
                else:
                    self.current_feedback = self.fail_image
                    self.total_score += self.current_score // 2
                
                self.phase = "scoring"
                self.start_time = current_time
                
        elif self.phase == "scoring":
            if elapsed >= 3:
                self.current_pose_index += 1
                if self.current_pose_index < len(self.poses):
                    self.start_new_pose()
                else:
                    self.game_over = True
    
    def draw(self):
        if not self.game_active:
            pygame.draw.rect(self.window, (100, 100, 255), self.start_button)
            self.window.blit(self.button_text, (self.width//2 - self.button_text.get_width()//2, 
                                              self.height//2 - self.button_text.get_height()//2))
            title_text = pygame.font.SysFont('Arial', 40).render("BALANCIMALS", True, (0, 0, 0))
            self.window.blit(title_text, (self.width//2 - title_text.get_width()//2, self.height//3))
            
            instruction = pygame.font.SysFont('Arial', 24).render("Wear your accelerometer belt and copy the poses!", True, (0, 0, 0))
            self.window.blit(instruction, (self.width//2 - instruction.get_width()//2, self.height//2 + 50))
            
            mock_notice = pygame.font.SysFont('Arial', 18).render("Using simulated motion data", True, (150, 0, 0))
            self.window.blit(mock_notice, (self.width//2 - mock_notice.get_width()//2, self.height//2 + 100))
            
            return
            
        if self.game_over:
            game_over_text = pygame.font.SysFont('Arial', 50).render("GAME OVER", True, (0, 0, 0))
            score_text = pygame.font.SysFont('Arial', 40).render(f"Final Score: {int(self.total_score)}", True, (0, 0, 0))
            
            self.window.blit(game_over_text, (self.width//2 - game_over_text.get_width()//2, self.height//3))
            self.window.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2))
            
            restart_button = pygame.Rect(self.width//2 - 100, self.height*2//3, 200, 50)
            pygame.draw.rect(self.window, (100, 100, 255), restart_button)
            restart_text = pygame.font.SysFont('Arial', 30).render("RESTART", True, (0, 0, 0))
            self.window.blit(restart_text, (self.width//2 - restart_text.get_width()//2, 
                                          self.height*2//3 + 25 - restart_text.get_height()//2))
            
            return
        
        if self.phase == "full":
            scaled_pose = pygame.transform.scale(self.current_pose, (400, 400))
            self.window.blit(scaled_pose, (self.width//2 - 200, self.height//2 - 200))
            
            instruction = pygame.font.SysFont('Arial', 30).render("Hit this pose!", True, (0, 0, 0))
            self.window.blit(instruction, (self.width//2 - instruction.get_width()//2, self.height//2 + 220))
            
            elapsed = time.time() - self.start_time
            countdown = max(0, self.pose_full_duration - int(elapsed))
            countdown_text = pygame.font.SysFont('Arial', 50).render(f"{countdown}", True, (0, 0, 0))
            self.window.blit(countdown_text, (self.width//2 - countdown_text.get_width()//2, 50))
            
        elif self.phase == "corner" or self.phase == "scoring":
            scaled_pose = pygame.transform.scale(self.current_pose, (150, 150))
            self.window.blit(scaled_pose, (self.width - 170, 20))
            
            self.window.blit(self.current_feedback, (self.width//2 - 100, self.height//2 - 100))
            
            if self.phase == "corner":
                instruction = pygame.font.SysFont('Arial', 30).render("Copy the pose now!", True, (0, 0, 0))
                self.window.blit(instruction, (self.width//2 - instruction.get_width()//2, self.height//2 + 120))
                
                elapsed = time.time() - self.start_time
                countdown = max(0, self.pose_corner_duration - int(elapsed))
                countdown_text = pygame.font.SysFont('Arial', 50).render(f"{countdown}", True, (0, 0, 0))
                self.window.blit(countdown_text, (self.width//2 - countdown_text.get_width()//2, 50))
                
                score_text = self.font.render(f"Current Score: {int(self.current_score)}", True, (0, 0, 0))
                self.window.blit(score_text, (20, 60))
            else:
                if self.current_feedback == self.success_image:
                    result_text = pygame.font.SysFont('Arial', 40).render("GREAT JOB!", True, (0, 150, 0))
                else:
                    result_text = pygame.font.SysFont('Arial', 40).render("TRY HARDER!", True, (150, 0, 0))
                self.window.blit(result_text, (self.width//2 - result_text.get_width()//2, self.height//2 + 120))

        score_text = self.font.render(f"Total Score: {int(self.total_score)}", True, (0, 0, 0))
        self.window.blit(score_text, (20, 20))
        
        progress_text = self.font.render(f"Pose {self.current_pose_index + 1}/{len(self.poses)}", True, (0, 0, 0))
        self.window.blit(progress_text, (self.width - 150, self.height - 30))
        
        mock_text = self.font.render("Using simulated motion data", True, (150, 0, 0))
        self.window.blit(mock_text, (self.width//2 - mock_text.get_width()//2, self.height - 30))
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if not self.game_active:
                    if self.start_button.collidepoint(mouse_pos):
                        self.start_game()
                elif self.game_over:
                    restart_button = pygame.Rect(self.width//2 - 100, self.height*2//3, 200, 50)
                    if restart_button.collidepoint(mouse_pos):
                        self.start_game()
    
    def display(self):
        self.update()
        self.draw()