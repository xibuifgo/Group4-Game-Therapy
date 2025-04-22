import pygame
import sys
import data_temp
from constants import WIDTH, HEIGHT, FPS, WHITE, window, clock

# Start data collection thread
data_temp.start_data_thread()

# Import all screens
from login_screen import LoginScreen
from menu_screen import MenuScreen
from calibration_screen import CalibrationScreen
from game_over_screen import GameOverScreen
from game_screen import GameScreen
from pose_game import PoseGame
from pose_scoring import PoseScorer

def main():
    running = True
    screen_status = 5  # Start with our pose game (5 is PoseGame)
    
    # Create pose scorer for evaluating poses
    pose_scorer = PoseScorer()
    
    # Create all screen objects
    login_screen_object = LoginScreen(window, clock)
    menu_screen_object = MenuScreen(window, clock)
    calibration_screen_object = CalibrationScreen(window, clock)
    game_screen_object = GameScreen(window, clock)
    game_over_screen_object = GameOverScreen(window, clock)
    
    # Create our pose game object and pass the pose scorer
    pose_game_object = PoseGame(window, clock)
    
    # Main game loop
    while running:
        window.fill(WHITE)
        
        # Get all events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # Check for key presses to switch screens (for testing)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    screen_status = 0  # Login screen
                elif event.key == pygame.K_1:
                    screen_status = 1  # Menu screen
                elif event.key == pygame.K_2:
                    screen_status = 2  # Calibration screen
                elif event.key == pygame.K_3:
                    screen_status = 3  # Game screen
                elif event.key == pygame.K_4:
                    screen_status = 4  # Game over screen
                elif event.key == pygame.K_5:
                    screen_status = 5  # Pose game
        
        # Display the current screen
        if screen_status == 0: 
            login_screen_object.display()
        elif screen_status == 1:
            menu_screen_object.display()
        elif screen_status == 2:
            calibration_screen_object.display()          
        elif screen_status == 3:
            game_screen_object.display()
        elif screen_status == 4:
            game_over_screen_object.display()
        elif screen_status == 5:
            # Pass events to pose game for handling
            pose_game_object.handle_events(events)
            pose_game_object.display()  # This calls both update and draw
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()