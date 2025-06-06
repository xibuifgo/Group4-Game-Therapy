import pygame
import data_temp
from base_screen import Screen
from constants import WHITE, window, clock, FPS

class GameScreen(Screen):
    def __init__(self, window, clock):
        self.window = window
        self.clock = clock
        
        try:
            sleeping_bear = pygame.image.load("assets/images/sleeping_bear.png")
            back_sleeping = pygame.image.load("assets/images/back_sleeping.png")
            waking_bear = pygame.image.load("assets/images/waking_bear.png")
            left_ear = pygame.image.load("assets/images/left_ear.png")
            right_ear = pygame.image.load("assets/images/right_ear.png")
            angry_bear = pygame.image.load("assets/images/angry_bear.png")
        except pygame.error:
            sleeping_bear = self.create_placeholder_image((200, 200), (150, 150, 200))
            back_sleeping = self.create_placeholder_image((100, 50), (100, 100, 150))
            waking_bear = self.create_placeholder_image((200, 200), (200, 150, 150))
            left_ear = self.create_placeholder_image((70, 70), (100, 100, 100))
            right_ear = self.create_placeholder_image((80, 80), (100, 100, 100))
            angry_bear = self.create_placeholder_image((200, 200), (250, 100, 100))

        self.counter = 1
        
        window_width, window_height = window.get_size()
        
        self.sleeping_bear = pygame.transform.scale(sleeping_bear, (window_width // 2, window_height // 2))
        self.back_sleeping = pygame.transform.scale(back_sleeping, (210, 100))
        self.waking_bear = pygame.transform.scale(waking_bear, (window_width // 2, window_height // 2))
        self.left_ear = pygame.transform.scale(left_ear, (70, 70))
        self.right_ear = pygame.transform.scale(right_ear, (80, 80))
        self.angry_bear = pygame.transform.scale(angry_bear, (window_width // 2, window_height // 2))

    def create_placeholder_image(self, size, color):
        """Create a placeholder image when actual assets/images aren't available"""
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface

    def display(self): 
        self.sleeping_animation()
        self.counter += 1 
        vals = data_temp.vals

        slight = []
        big = []
        for key, value_list in vals.items():
            if value_list:
                last_value = value_list[-1]
                if abs(last_value) >= 1 and abs(last_value) < 2:
                    slight.append(last_value)
                elif abs(last_value) >= 2:
                    big.append(last_value)
        
        print("Big movements:", big)
        if big:
            self.angry_transition()
        elif slight: 
            self.waking_animation()

    def sleeping_animation(self):
        for _ in range(5):
            self.window.fill(WHITE)
            y_offset = 5 * (pygame.time.get_ticks() % 1000) / 1000 
            self.window.blit(self.sleeping_bear, (200, 250))
            self.window.blit(self.back_sleeping, (300, 215 + int(y_offset)))

            self.draw_zzzz(self.window, 200, 250 - _ // 4, max(0, 255 - _ * 2))
            pygame.display.flip()

            self.clock.tick(FPS)

    def draw_zzzz(self, surface, x, y, alpha=255):
        font = pygame.font.Font(None, 36)
        text = font.render("ZZZZ", True, (200, 200, 200))
        text.set_alpha(alpha)
        surface.blit(text, (x, y))

    def waking_animation(self):
        pupil_x = 320 
        ear_twitch_offset = 0
        PUPIL_COLOR = (20, 20, 20)

        for i in range(5):
            self.window.fill(WHITE)
            self.window.blit(self.waking_bear, (200, 250))

            if pupil_x < 326: 
                pupil_x += 0.4

            pygame.draw.circle(self.window, PUPIL_COLOR, (int(pupil_x), 395), 5) 
            ear_twitch_offset = 2 if i % 10 < 5 else -2
            self.window.blit(self.left_ear, (195 + ear_twitch_offset, 300))
            self.window.blit(self.right_ear, (332 - ear_twitch_offset, 290))

            pygame.display.flip()
            self.clock.tick(FPS)
    
    def angry_transition(self):
        for i in range(5): 
            self.window.fill(WHITE)
            alpha = int((i / 20) * 255) 

            waking_surface = self.waking_bear.copy()
            waking_surface.set_alpha(255 - alpha)
            self.window.blit(waking_surface, (200, 250))

            angry_surface = self.angry_bear.copy()
            angry_surface.set_alpha(alpha) 
            self.window.blit(angry_surface, (200, 250))

            pygame.display.flip()
            self.clock.tick(FPS)

        for _ in range(5):
            self.window.fill(WHITE)
            offset_x = 5 if _ % 2 == 0 else -5 
            self.window.blit(self.angry_bear, (200 + offset_x, 250))

            pygame.display.flip()
            self.clock.tick(FPS)