import pygame

FPS = 30
WHITE = (255, 255, 255)

pygame.init()

infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)  # Or use pygame.FULLSCREEN

pygame.display.set_caption("Balancimals")

clock = pygame.time.Clock()
