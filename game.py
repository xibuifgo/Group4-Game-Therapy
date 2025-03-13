import pygame
import sys
import data

pygame.init()

WIDTH, HEIGHT = 800, 600
FPS = 30
WHITE = (255, 255, 255)

data.start_data_thread()

sleeping_bear = pygame.image.load("images/sleeping_bear.png")
back_sleeping = pygame.image.load("images/back_sleeping.png")
waking_bear = pygame.image.load("images/waking_bear.png")
left_ear = pygame.image.load("images/left_ear.png")
right_ear = pygame.image.load("images/right_ear.png")
angry_bear = pygame.image.load("images/angry_bear.png")

sleeping_bear = pygame.transform.scale(sleeping_bear, (400, 300))
back_sleeping = pygame.transform.scale(back_sleeping, (210, 100))
waking_bear = pygame.transform.scale(waking_bear, (400, 300))
left_ear = pygame.transform.scale(left_ear, (70, 70))
right_ear = pygame.transform.scale(right_ear, (80, 80))
angry_bear = pygame.transform.scale(angry_bear, (400, 300))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bear Animation")

clock = pygame.time.Clock()

def draw_zzzz(surface, x, y, alpha=255):

    font = pygame.font.Font(None, 36)
    text = font.render("ZZZZ", True, (200, 200, 200))
    text.set_alpha(alpha)
    surface.blit(text, (x, y))


def sleeping_animation():

    for _ in range(20):

        screen.fill(WHITE)
        y_offset = 5 * (pygame.time.get_ticks() % 1000) / 1000 
        screen.blit(sleeping_bear, (200, 250))
        screen.blit(back_sleeping, (300, 215 + int(y_offset)))

        draw_zzzz(screen, 200, 250 - _ // 4, max(0, 255 - _ * 2))
        pygame.display.flip()

        clock.tick(FPS)


def waking_animation():

    pupil_x = 320 
    ear_twitch_offset = 0
    PUPIL_COLOR = (20, 20, 20)

    for i in range(20): 

        screen.fill(WHITE)
        screen.blit(waking_bear, (200, 250))

        if pupil_x < 326: 
            pupil_x += 0.4

        pygame.draw.circle(screen, PUPIL_COLOR, (int(pupil_x), 395), 5) 
        ear_twitch_offset = 2 if i % 10 < 5 else -2
        screen.blit(left_ear, (195 + ear_twitch_offset, 300))
        screen.blit(right_ear, (332 - ear_twitch_offset, 290))

        pygame.display.flip()
        clock.tick(FPS)

 
def angry_transition():

    for i in range(5): 
        screen.fill(WHITE)
        alpha = int((i / 20) * 255) 

        waking_surface = waking_bear.copy()
        waking_surface.set_alpha(255 - alpha)
        screen.blit(waking_surface, (200, 250))

        angry_surface = angry_bear.copy()
        angry_surface.set_alpha(alpha) 
        screen.blit(angry_surface, (200, 250))

        pygame.display.flip()
        clock.tick(FPS)

    for _ in range(20):

        screen.fill(WHITE)
        offset_x = 5 if _ % 2 == 0 else -5 
        screen.blit(angry_bear, (200 + offset_x, 250))

        pygame.display.flip()
        clock.tick(FPS)


def main():

    running = True

    while running:
        screen.fill(WHITE)

        sleeping_animation()

        vals = data.vals

        slight = [value[-1] for value in vals.values() if abs(value[-1]) >= 1 and abs(value[-1]) < 2]
        big = [value[-1] for value in vals.values() if abs(value[-1]) >= 2]
        print(big)
        if big:
            angry_transition()
            exit()
        elif slight: 
            waking_animation()

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()


main()