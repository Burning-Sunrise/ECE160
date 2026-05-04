import pygame

class ConfirmTradePopup:
    def __init__(self, surface, font):
        self.surface = surface
        self.font = font

        # Popup size
        self.width = 300
        self.height = 150

        sw, sh = surface.get_size()
        self.rect = pygame.Rect(
            (sw - self.width) // 2,
            (sh - self.height) // 2,
            self.width,
            self.height
        )

        # Buttons
        self.btn_yes = pygame.Rect(self.rect.x + 40, self.rect.y + 90, 80, 30)
        self.btn_no  = pygame.Rect(self.rect.x + 180, self.rect.y + 90, 80, 30)

    def draw(self):
        # Background box
        pygame.draw.rect(self.surface, (30, 30, 30), self.rect)
        pygame.draw.rect(self.surface, (200, 200, 200), self.rect, 2)

        # Text
        text = self.font.render("Gonna Trade?", True, (255, 255, 255))
        self.surface.blit(text, (self.rect.x + 40, self.rect.y + 30))

        # Yes button
        pygame.draw.rect(self.surface, (80, 200, 80), self.btn_yes)
        yes = self.font.render("Yes", True, (0, 0, 0))
        self.surface.blit(yes, (self.btn_yes.x + 20, self.btn_yes.y + 5))

        # No button
        pygame.draw.rect(self.surface, (200, 80, 80), self.btn_no)
        no = self.font.render("No", True, (0, 0, 0))
        self.surface.blit(no, (self.btn_no.x + 25, self.btn_no.y + 5))

    def handle_click(self, pos):
        if self.btn_yes.collidepoint(pos):
            return "yes"
        if self.btn_no.collidepoint(pos):
            return "no"
        return None
    