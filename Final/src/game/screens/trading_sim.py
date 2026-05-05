#Lexie's game will have to integrate with this code placeholder right here and assign values to money gained
import pygame
import random

class TradingSimScreen:
    def __init__(self):
        self.ui = None
        self.investment_amount = 0
        self.result_text = ""
        self.timer = 0.0
        self.state = "IDLE"  # IDLE → RUNNING → RESULT → EXIT

    def start(self, amount):
        """Called by UIManager when the player enters the mini-game."""
        self.investment_amount = amount
        self.result_text = ""
        self.timer = 0.0
        self.state = "RUNNING"

    def handle_event(self, event):
        pass  # No input needed

    def update(self, dt, game_state):
        # dt is in SECONDS (0.016, 0.033, etc.)

        # If already finished, do nothing
        if self.state == "EXIT":
            return

        # -------------------------
        # PHASE 1 — TRADING
        # -------------------------
        if self.state == "RUNNING":
            self.timer += dt

            if self.timer >= 2.0:  # 2 seconds
                win = random.choice([True, False])

                if win:
                    winnings = self.investment_amount * 2
                    game_state.add_money(winnings)
                    self.result_text = f"You WON! +${self.investment_amount}"
                else:
                    self.result_text = f"You LOST! -${self.investment_amount}"

                self.state = "RESULT"
                self.timer = 0.0

        # -------------------------
        # PHASE 2 — SHOW RESULT
        # -------------------------
        elif self.state == "RESULT":
            self.timer += dt

            if self.timer >= 2.0:  # show result for 2 seconds
                self.state = "EXIT"

                # Return to Trading Floor
                self.ui.change_screen("TRADING_FLOOR")
                self.ui.state = None

    def draw(self, surface):
        font = pygame.font.SysFont(None, 32)

        if self.state == "RUNNING":
            msg = "Trading..."
        else:
            msg = self.result_text

        surf = font.render(msg, True, (255, 255, 255))
        rect = surf.get_rect(center=(surface.get_width() // 2,
                                     surface.get_height() // 2))
        surface.blit(surf, rect)
