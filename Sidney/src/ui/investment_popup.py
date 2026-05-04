import pygame

class InvestmentPopup:
    def __init__(self, surface, font, max_amount):
        self.surface = surface
        self.font = font
        self.max_amount = max_amount

        self.width = 320
        self.height = 180

        sw, sh = surface.get_size()
        self.rect = pygame.Rect(
            (sw - self.width) // 2,
            (sh - self.height) // 2,
            self.width,
            self.height
        )

        # Input box
        self.input_rect = pygame.Rect(self.rect.x + 40, self.rect.y + 60, 240, 32)
        self.input_text = ""

        # Buttons
        self.btn_ok = pygame.Rect(self.rect.x + 40, self.rect.y + 120, 100, 32)
        self.btn_cancel = pygame.Rect(self.rect.x + 180, self.rect.y + 120, 100, 32)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_RETURN:
                return self._validate()
            elif event.unicode.isdigit():
                self.input_text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn_ok.collidepoint(event.pos):
                return self._validate()
            if self.btn_cancel.collidepoint(event.pos):
                return "cancel"

        return None

    def _validate(self):
        if self.input_text == "":
            return None

        amount = int(self.input_text)

        if 0 < amount <= self.max_amount:
            return amount
        return None

    def draw(self):
        pygame.draw.rect(self.surface, (30, 30, 30), self.rect)
        pygame.draw.rect(self.surface, (200, 200, 200), self.rect, 2)

        title = self.font.render("Investment Amount", True, (255, 255, 255))
        self.surface.blit(title, (self.rect.x + 60, self.rect.y + 20))

        pygame.draw.rect(self.surface, (255, 255, 255), self.input_rect, 2)
        text_surface = self.font.render(self.input_text, True, (255, 255, 255))
        self.surface.blit(text_surface, (self.input_rect.x + 5, self.input_rect.y + 5))

        pygame.draw.rect(self.surface, (80, 200, 80), self.btn_ok)
        ok = self.font.render("OK", True, (0, 0, 0))
        self.surface.blit(ok, (self.btn_ok.x + 30, self.btn_ok.y + 5))

        pygame.draw.rect(self.surface, (200, 80, 80), self.btn_cancel)
        cancel = self.font.render("Cancel", True, (0, 0, 0))
        self.surface.blit(cancel, (self.btn_cancel.x + 15, self.btn_cancel.y + 5))