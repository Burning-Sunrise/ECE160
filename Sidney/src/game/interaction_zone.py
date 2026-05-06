import pygame

class InteractionZone:
    def __init__(self, x, y, w, h, zone_type, data=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.type = zone_type
        self.data = data or {}
#dummy text, Ui Manager calls when necessary