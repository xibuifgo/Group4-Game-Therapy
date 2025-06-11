import pygame
import sys
import data_real
from constants import WIDTH, HEIGHT, FPS, WHITE, window, clock
from pose_game import PoseGame

data_real.start_data_thread()

def main():
    running = True
    pose_game = PoseGame(window, clock)

    while running:
        window.fill(WHITE)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()

        pose_game.handle_events(events)
        pose_game.display()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    pygame.mixer.music.stop()
    pygame.mixer.quit()
    sys.exit()

if __name__ == "__main__":
    main()
