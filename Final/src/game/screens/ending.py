import pygame
from settings import GAME_WIDTH, GAME_HEIGHT


class EndingScreen:
    def __init__(self):
        self.ui = None
        self.entered = False
        self.fade_alpha = 0

    def reset(self):
        self.fade_alpha = 0

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt, game_state):
        if not self.entered:
            self.reset()
            self.entered = True
        # Fade in over ~2.5 seconds
        if self.fade_alpha < 255:
            self.fade_alpha += 100 * dt
            if self.fade_alpha > 255:
                self.fade_alpha = 255

    def draw(self, surface):
        surface.fill((5, 5, 8))

        font_title = pygame.font.SysFont("Arial", 22, bold=True)
        font_body = pygame.font.SysFont("Arial", 14)

        title = font_title.render(
            "You survived 7 days through stock trading.",
            True, (220, 200, 100)
        )
        title.set_alpha(int(self.fade_alpha))
        title_rect = title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50))
        surface.blit(title, title_rect)

        # Multi-line body text
        lines = [
            "But for people struggling with depression,",
            "trading stocks isn't a good idea — ",
            "it can heavily affect your mood.",
        ]

        y = GAME_HEIGHT // 2 + 10
        for line in lines:
            text = font_body.render(line, True, (170, 170, 180))
            text.set_alpha(int(self.fade_alpha))
            rect = text.get_rect(center=(GAME_WIDTH // 2, y))
            surface.blit(text, rect)
            y += 22