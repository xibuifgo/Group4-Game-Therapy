import pygame

class BearAnimator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clock = pygame.time.Clock()
        self.fps = 30
        self.state = "sleeping"
        self.prev_state = None

        # Fractions based on the original 800x600 layout
        self.base_x_frac = 290 / 800
        self.base_y_frac = 260 / 600
        self.back_dx_frac = 55 / 800   # back_offset_x
        self.back_dy_frac = -20 / 600   # back_offset_y

        # Waking relative offsets w.r.t. bear image size
        self.eye_offset_x_frac = 130 / 400
        self.eye_offset_y_frac = 55 / 300
        self.left_ear_dx_frac = -5 / 400
        self.left_ear_dy_frac = 50 / 300
        self.right_ear_dx_frac = 132 / 400
        self.right_ear_dy_frac = 40 / 300

        # Scale factor and bear size (approx half screen)
        self.bear_size = int(min(self.width, self.height) * 0.5)

        # Load images with fallbacks
        try:
            self.sleep_img = pygame.image.load("assets/images/sleeping_bear.png").convert_alpha()
            self.back_img  = pygame.image.load("assets/images/back_sleeping.PNG").convert_alpha()
            self.wake_img  = pygame.image.load("assets/images/waking_bear.PNG").convert_alpha()
            self.angry_img = pygame.image.load("assets/images/angry_bear.PNG").convert_alpha()
            self.l_ear_img = pygame.image.load("assets/images/left_ear.PNG").convert_alpha()
            self.r_ear_img = pygame.image.load("assets/images/right_ear.PNG").convert_alpha()
        except pygame.error:
            # placeholder
            self.sleep_img = self._placeholder((200,200),(150,150,200))
            self.back_img  = self._placeholder((210,100),(100,100,150))
            self.wake_img  = self._placeholder((200,200),(200,150,150))
            self.angry_img = self._placeholder((200,200),(250,100,100))
            self.l_ear_img = self._placeholder((70,70),(100,100,100))
            self.r_ear_img = self._placeholder((80,80),(100,100,100))

        # Scale all to original proportions: sleeping/back 400x300 & 210x100 back, waking/angry 400x300, ears 70x70/80x80
        self.sleep_img = pygame.transform.scale(self.sleep_img, (400, 300))
        self.back_img  = pygame.transform.scale(self.back_img,  (210, 100))
        self.wake_img  = pygame.transform.scale(self.wake_img,  (400, 300))
        self.angry_img = pygame.transform.scale(self.angry_img, (400, 300))
        self.l_ear_img = pygame.transform.scale(self.l_ear_img, (70, 70))
        self.r_ear_img = pygame.transform.scale(self.r_ear_img, (80, 80))

        # Pupil
        self.pupil_x = 0
        self.pupil_y = 0

    def _placeholder(self, size, color):
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill(color)
        return surf

    def update(self, score):
        new_state = "sleeping" if score >= 80 else "waking" if score >= 50 else "angry"
        if new_state == "waking" and self.prev_state != "waking":
            # init pupil from waking image
            base_x = int(self.base_x_frac * self.width)
            base_y = int(self.base_y_frac * self.height)
            self.pupil_x = base_x + int(self.eye_offset_x_frac * 400)
            self.pupil_y = base_y + int(self.eye_offset_y_frac * 300)
        self.state = new_state
        self.prev_state = new_state

    def draw(self, surface, center_pos=None):
        if center_pos is None:
            center_pos = (self.width // 2, self.height // 2)

        if self.state == "sleeping":
            self._draw_sleep(surface, center_pos)
        elif self.state == "waking":
            self._draw_wake(surface, center_pos)
        else:
            self._draw_angry(surface, center_pos)


    def _draw_sleep(self, surface, center_pos):
        bear_rect = self.sleep_img.get_rect(center=center_pos)
        x, y = bear_rect.topleft

        # Bobbing animation
        bob = int((pygame.time.get_ticks() % 1000) / 1000 * 5)

        # Draw base bear
        surface.blit(self.sleep_img, (x, y))
        surface.blit(self.back_img, (x + int(self.back_dx_frac * self.width),
                                    y + int(self.back_dy_frac * self.height) + bob))

        # Floating ZZZ (responsive + left-aligned above bear)
        t = pygame.time.get_ticks() % 2000
        f = t / 2000
        font = pygame.font.Font(None, int(self.height * 0.05))  # scale font to screen height
        txt = font.render("ZZZ", True, (200, 200, 200))
        txt.set_alpha(max(0, 255 - int(f * 255)))
        zzz_x = center_pos[0] - int(self.sleep_img.get_width() * 0.25) - txt.get_width() // 2  # 25% left of bear center
        zzz_y = y - int(self.height * 0.05) - int(f * self.height * 0.1)

        surface.blit(txt, (zzz_x, zzz_y))


    def _draw_wake(self, surface, center_pos):
        bear_rect = self.wake_img.get_rect(center=center_pos)
        x, y = bear_rect.topleft

        surface.blit(self.wake_img, (x, y))

        # Pupil
        eye_x = x + int(self.eye_offset_x_frac * self.wake_img.get_width())
        eye_y = y + int(self.eye_offset_y_frac * self.wake_img.get_height())
        pupil_range = int(self.wake_img.get_width() * 0.05)  # move ~5% of bear width
        pupil_x = eye_x - int(pupil_range * 0.5) + int((pygame.time.get_ticks() % 1000) / 1000 * pupil_range)
        pupil_x -= int(self.wake_img.get_width() * 0.015)  # shift left ~2% of bear width
        pupil_y = eye_y + int(self.wake_img.get_height() * 0.30)  # shift down ~2% of bear height

        pygame.draw.circle(surface, (20, 20, 20), (pupil_x, pupil_y), int(self.width * 0.006))

        # Ears twitch
        off = 2 if ((pygame.time.get_ticks() // 200) % 2) == 0 else -2
        lx = x + int(self.left_ear_dx_frac * 400) + off
        ly = y + int(self.left_ear_dy_frac * 300)
        rx = x + int(self.right_ear_dx_frac * 400) - off
        ry = y + int(self.right_ear_dy_frac * 300)
        surface.blit(self.l_ear_img, (lx, ly))
        surface.blit(self.r_ear_img, (rx, ry))


    def _draw_angry(self, surface, center_pos):
        bear_rect = self.angry_img.get_rect(center=center_pos)
        x, y = bear_rect.topleft

        shake = 5 if ((pygame.time.get_ticks() // 100) % 2) == 0 else -5
        surface.blit(self.angry_img, (x + shake, y))