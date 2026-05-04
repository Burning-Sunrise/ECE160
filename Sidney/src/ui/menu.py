import pygame

class SettingsMenu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

        # Panel size + position
        panel_width = 260
        panel_height = 200
        screen_w = self.screen.get_width()
        screen_h = self.screen.get_height()

        self.panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        self.panel_rect.center = (screen_w // 2, screen_h // 2)

        # Buttons dictionary
        self.buttons = {}
        self._create_buttons()

    def _create_buttons(self):
        """Create Toggle Fullscreen + Back buttons."""
        button_width = 180
        button_height = 32
        spacing = 12

        start_y = self.panel_rect.y + 60
        center_x = self.panel_rect.centerx

        items = [
            ("Toggle Fullscreen", "toggle_fullscreen"),
            ("Back", "back"),
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
        """Draw the settings menu panel + buttons."""
        # Panel
        pygame.draw.rect(self.screen, (25, 25, 25), self.panel_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.panel_rect, 2)

        # Title
        title_surface = self.font.render("SETTINGS", False, (255, 255, 255))
        title_rect = title_surface.get_rect(
            center=(self.panel_rect.centerx, self.panel_rect.y + 24)
        )
        self.screen.blit(title_surface, title_rect)

        # Buttons
        for data in self.buttons.values():
            rect = data["rect"]

            pygame.draw.rect(self.screen, (70, 70, 70), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

            label_surface = self.font.render(data["label"], False, (255, 255, 255))
            label_rect = label_surface.get_rect(center=rect.center)
            self.screen.blit(label_surface, label_rect)