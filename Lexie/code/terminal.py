import pygame
from settings import WINDOW_WIDTH, WINDOW_HEIGHT

NEON = (0, 255, 140)
WHITE = (230, 230, 230)


class Terminal:
    def __init__(self):
        self.visible = False
        self.node = None
        self.near_node = False
        self.data = {}

    # ---------------------------------------------------------
    # OPEN / CLOSE
    # ---------------------------------------------------------
    def open(self, node):
        self.visible = True
        self.node = node

    def close(self):
        self.visible = False
        self.node = None

    # ---------------------------------------------------------
    # TEXT DRAWING
    # ---------------------------------------------------------
    def draw_text(self, surf, text, pos, size=26, color=NEON, left=False):
        font = pygame.font.Font(None, size)
        img = font.render(text, True, color)
        rect = img.get_rect(topleft=pos) if left else img.get_rect(center=pos)
        surf.blit(img, rect)

    # ---------------------------------------------------------
    # INTEL HINT
    # ---------------------------------------------------------
    def get_hint(self):
        if not self.node:
            return "No intel."
        t = self.node.__class__.__name__
        if t == "MomentumNode": return "Momentum Spike"
        if t == "LiquidityNode": return "Liquidity Pocket"
        if t == "RiskNode": return "Risky Zone"
        if t == "DarkPoolNode": return "Dark Pool Activity"
        return "Unknown Intel"

    # ---------------------------------------------------------
    # ALWAYS-VISIBLE HEADER
    # ---------------------------------------------------------
    def draw_header(self, surf):
        if not self.data:
            return

        d = self.data

        # Title
        self.draw_text(surf, "H100 TERMINAL", (WINDOW_WIDTH//2, 10), size=32)

        # Capital
        self.draw_text(surf,
                       f"${d['capital']:.2f}",
                       (20, 45), size=24, left=True)

        # P/L
        self.draw_text(surf,
                       f"P/L {d['pl_display']}",
                       (200, 45), size=24, left=True)

        # Timer
        self.draw_text(surf,
                       f"{int(d['run_time'])}s LEFT",
                       (450, 45), size=24, left=True)

        # Intel indicator
        if d.get("carrying_intel", False):
            self.draw_text(surf,
                           "INTEL READY",
                           (650, 45), size=24, left=True)

    # ---------------------------------------------------------
    # MAIN DRAW
    # ---------------------------------------------------------
    def draw(self, surf):

        # Header always visible
        if self.data:
            self.draw_header(surf)

        # Prompt when near node (SPACE opens terminal)
        if self.near_node and not self.visible:
            self.draw_text(
                surf,
                "[SPACE] CONNECT",
                (WINDOW_WIDTH//2, WINDOW_HEIGHT - 50),
                size=28
            )
            return

        # If terminal is closed, stop here
        if not self.visible or not self.node:
            return

        d = self.data

        # Panel
        w, h = 380, 160
        x = WINDOW_WIDTH//2 - w//2
        y = WINDOW_HEIGHT//2 - h//2 + 40

        panel = pygame.Surface((w, h))
        panel.fill((10, 10, 14))
        pygame.draw.rect(panel, NEON, (0, 0, w, h), 2)
        surf.blit(panel, (x, y))

        # Symbol
        self.draw_text(surf, self.node.symbol,
                       (x + w//2, y + 30), size=32)

        # Hint
        self.draw_text(surf, d["insider_hint"],
                       (x + w//2, y + 65), size=20, color=WHITE)

        # Live intel
        if d["current_signal"]:
            label = d["current_signal"]["label"]
            self.draw_text(surf,
                           f"Intel: {label}",
                           (x + w//2, y + 100),
                           size=22)

        # Action (ENTER commits liquidation)
        self.draw_text(
            surf,
            "[ENTER] COMMIT",
            (x + w//2, y + h - 30),
            size=22
        )
