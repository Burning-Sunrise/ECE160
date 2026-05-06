import pygame
# drawing and design of pause button (simple)
class PauseMenu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

        #Panel size + position
        panel_width = 240
        panel_height = 180
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()

        self.panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        self.panel_rect.center = (screen_w // 2, screen_h //2)

        #Buttons dictionary
        self.buttons = {}
        self._create_buttons()
    def _create_buttons(self):
        """Create Resume, Settings, Exit buttons."""
        button_width = 160
        button_height = 32
        spacing = 12

        start_y = self.panel_rect.y + 50
        center_x = self.panel_rect.centerx

        # (Label, Action)
        items = [
            ("Resume", "resume"),
            ("Settings", "settings"),
            ("Exit Game", "exit"),
        ]

        for i, (label, action) in enumerate(items):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.centerx = center_x
            rect.y = start_y + i * (button_height + spacing)

            self.buttons[action] = {
                "rect": rect,
                "label": label
            }

    def handle_click(self, mouse_pos):
        """Return the action string if a button is clicked."""
        for action, data in self.buttons.items():
            if data["rect"].collidepoint(mouse_pos):
                return action
        return None
    def draw(self):
        """Draw the pause menu panel + buttons."""
        # Draw panel
        pygame.draw.rect(self.screen, (30, 30, 30), self.panel_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.panel_rect, 2)

        # Title
        title_surface = self.font.render("PAUSED", False, (255, 255, 255))
        title_rect = title_surface.get_rect(
            center=(self.panel_rect.centerx, self.panel_rect.y + 24)
        )
        self.screen.blit(title_surface, title_rect)

        # Draw buttons
        for data in self.buttons.values():
            rect = data["rect"]

            # Button background
            pygame.draw.rect(self.screen, (60, 60, 60), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

            # Button label
            label_surface = self.font.render(data["label"], False, (255, 255, 255))
            label_rect = label_surface.get_rect(center=rect.center)
            self.screen.blit(label_surface, label_rect)