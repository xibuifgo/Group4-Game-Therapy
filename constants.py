import pygame

# Global constants that will be used across screens
WIDTH, HEIGHT = 800, 600
FPS = 30
WHITE = (255, 255, 255)

# Initialize pygame
pygame.init()

# Create the window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pose Mimicking Game")

# Create the clock
clock = pygame.time.Clock()