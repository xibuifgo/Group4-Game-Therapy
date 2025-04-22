import pygame

WIDTH, HEIGHT = 800, 600
FPS = 30
WHITE = (255, 255, 255)

pygame.init()

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Balancimals")

clock = pygame.time.Clock()