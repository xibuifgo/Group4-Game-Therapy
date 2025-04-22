import pygame
import sys
import data_real
from login_screen import LoginScreen
from menu_screen import MenuScreen
from calibration_screen import CalibrationScreen
from game_over_screen import GameOverScreen
from game_screen import GameScreen
from abc import ABC, abstractmethod

class Screen():
    @abstractmethod
    def display(self):
        pass

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 30
WHITE = (255, 255, 255)

data_real.start_data_thread()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bear Animation")

clock = pygame.time.Clock()

def main():

    running = True
    frame_count = 0
    screen_status = 0

    login_screen_object = LoginScreen(window, clock)
    menu_screen_object = MenuScreen(window, clock)
    calibration_screen_object = CalibrationScreen(window, clock)
    game_screen_object = GameScreen(window, clock)
    game_over_screen_object = GameOverScreen(window, clock)  

    while running:
        window.fill(WHITE)
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

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()


main()