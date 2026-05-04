import pygame
from settings import *

class ResultsScreen:
    def __init__(self):
        self.capital = 0
        self.pl = 0
        self.intel = "None"
        self.nodes = 0
        self.enemies = 0
        self.reason = None

        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)

    def collect(self, capital, pl, intel, nodes, enemies, reason=None):
        self.capital = capital
        self.pl = pl
        self.intel = intel
        self.nodes = nodes
        self.enemies = enemies
        self.reason = reason

    def draw(self, surface):
        surface.fill("black")

        lines = [
            "RUN COMPLETE",
            f"Capital: ${self.capital}",
            f"P/L: {self.pl}",
            f"Intel: {self.intel}",
            f"Nodes Accessed: {self.nodes}",
            f"Enemies Defeated: {self.enemies}",
        ]

        if self.reason == "REACHED_NASDAQ":
            lines.append("Outcome: SUCCESS — Reached NASDAQ")
        elif self.reason == "CAUGHT_BY_POLICE":
            lines.append("Outcome: CAUGHT — Police Intercepted You")
        elif self.reason == "TIME_UP":
            lines.append("Outcome: TIME UP — Market Closed")

        y = 150
        for text in lines:
            surf = self.font.render(text, True, "white")
            rect = surf.get_rect(center=(WINDOW_WIDTH // 2, y))
            surface.blit(surf, rect)
            y += 60
