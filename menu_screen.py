import pygame
from base_screen import Screen
from constants import WHITE, window, clock, FPS

class MenuScreen(Screen):
    def __init__(self, window, clock):
        self.window = window
        self.clock = clock
        
    def display(self):
        # Basic display for now
        font = pygame.font.SysFont('Arial', 40)
        text = font.render("Menu Screen", True, (0, 0, 0))
        self.window.blit(text, (self.window.get_width()//2 - text.get_width()//2, 
                            self.window.get_height()//2 - text.get_height()//2))