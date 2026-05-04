#Lexie's game will have to integrate with this code placeholder right here and assign values to money gained

import pygame
import random

class TradingSimScreen:
    def __init__(self):
        self.ui = None
        self.active = False
        self.invest_amount = 0
        self.timer = 0
        self.result_ready = False
        self.win = False

    # Called by UIManager when entering this screen
    def start(self, amount):
        self.invest_amount = amount
        self.active = True
        self.timer = 0
        self.result_ready = False
        self.win = False

    def handle_event(self, event):
        # Later your teammate can add controls here
        pass

    def update(self, dt, game_state):
        if not self.active:
            return

        # -----------------------------------------
        # Placeholder minigame logic:
        # After 2 seconds, randomly win or lose
        # -----------------------------------------
        self.timer += dt
        if self.timer >= 2.0 and not self.result_ready:
            self.result_ready = True
            self.win = random.choice([True, False])

            # Apply win/loss to GameState
            if self.win:
                game_state.money += self.invest_amount
            else:
                game_state.money -= self.invest_amount

            # Register the trade
            outcome = game_state.register_trade()

            # Decide next screen
            if outcome == "DAY_OVER":
                self.ui.change_screen("RECOVERY_ROOM")
            else:
                self.ui.change_screen("TRADING_FLOOR")

            # Reset this screen
            self.active = False

    def draw(self, surface):
        surface.fill((40, 0, 0))

        font = self.ui.font

        if not self.result_ready:
            msg = f"Trading... Investing ${self.invest_amount}"
        else:
            msg = "WIN!" if self.win else "LOSS!"

        text = font.render(msg, True, (255, 255, 255))
        surface.blit(text, (40, 40))
