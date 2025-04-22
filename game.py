import pygame
import sys
import data_temp
from constants import WIDTH, HEIGHT, FPS, WHITE, window, clock

data_temp.start_data_thread()

from login_screen import LoginScreen
from menu_screen import MenuScreen
from calibration_screen import CalibrationScreen
from game_over_screen import GameOverScreen
from game_screen import GameScreen
from pose_game import PoseGame
from pose_scoring import PoseScorer

def main():
    running = True
    screen_status = 5

    pose_scorer = PoseScorer()

    login_screen_object = LoginScreen(window, clock)
    menu_screen_object = MenuScreen(window, clock)
    calibration_screen_object = CalibrationScreen(window, clock)
    game_screen_object = GameScreen(window, clock)
    game_over_screen_object = GameOverScreen(window, clock)

    pose_game_object = PoseGame(window, clock)

    while running:
        window.fill(WHITE)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

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
            pose_game_object.handle_events(events)
            pose_game_object.display()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()