import pygame
from os.path import join

# Base info node
class InfoNode(pygame.sprite.Sprite):
    def __init__(self, pos, symbol, groups, image_name):
        super().__init__(groups)

        path = join("data", "graphics", "nodes", image_name)
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect(center=pos)

        self.symbol = symbol
        self.activated = False

    def activate(self, game):
        print(f"[NODE] Activated {self.symbol}")
        self.activated = True


class MomentumNode(InfoNode):
    def __init__(self, pos, symbol, groups):
        super().__init__(pos, symbol, groups, "momentum.png")


class LiquidityNode(InfoNode):
    def __init__(self, pos, symbol, groups):
        super().__init__(pos, symbol, groups, "liquidity.png")


class RiskNode(InfoNode):
    def __init__(self, pos, symbol, groups):
        super().__init__(pos, symbol, groups, "risk.png")


class DarkPoolNode(InfoNode):
    def __init__(self, pos, symbol, groups):
        super().__init__(pos, symbol, groups, "darkpool.png")


# Generic Node used by main.py / Tiled "Node" objects
class Node(pygame.sprite.Sprite):
    def __init__(self, pos, symbol, *groups):
        super().__init__(*groups)

        path = join("data", "graphics", "nodes", "node.png")
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (64, 64))
        self.rect = self.image.get_rect(center=pos)

        self.symbol = symbol
