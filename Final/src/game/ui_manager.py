import os, sys
print("CWD:", os.getcwd())
print("PATH:", sys.path)

import pygame
from ui.pause import PauseMenu
from ui.menu import SettingsMenu
from ui.confirm_trade import ConfirmTradePopup
from ui.investment_popup import InvestmentPopup

from game.screens.trading_floor import TradingFloorScreen
from game.screens.trading_sim import TradingSimScreen
from game.screens.recovery_room import RecoveryRoomScreen
from game.screens.nightmare import NightmareScreen
from game.screens.game_over import GameOverScreen


class UIManager:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

        # GameState reference (set in update)
        self.game_state = None

        self.state = None
        self.paused = False

        self.pause_menu = PauseMenu(self.screen, self.font)
        self.settings_menu = SettingsMenu(self.screen, self.font)

        self.pause_button_rect = pygame.Rect(0, 0, 32, 32)
        self._position_pause_button()

        # HUD values
        self.money = 0
        self.day = 1
        self.actions_left = 3
        self.stress = 0
        self.max_stress = 100

        # Investment popup
        self.invest_popup = None
        self.invest_amount = None

        # Prompt text
        self.prompt_text = None
        self.prompt_pos = None

        # Screens
        self.screens = {
            "TRADING_FLOOR": TradingFloorScreen(),
            "TRADING_SIM": TradingSimScreen(),
            "RECOVERY_ROOM": RecoveryRoomScreen(),
            "NIGHTMARE": NightmareScreen(),
            "GAME_OVER": GameOverScreen(),
        }
        self.current_screen = "TRADING_FLOOR"
        self.confirm_trade = ConfirmTradePopup(self.screen, self.font)

        # Give each screen access to UIManager
        for screen in self.screens.values():
            screen.ui = self

    # ------------------------------------------------
    # Screen Management
    # ------------------------------------------------
    def change_screen(self, new_screen):
        if new_screen in self.screens:
            self.clear_prompt()
            self.current_screen = new_screen

    # ------------------------------------------------
    # Pause Button
    # ------------------------------------------------
    def _position_pause_button(self):
        w = self.screen.get_width()
        self.pause_button_rect.topright = (w - 8, 8)

    # ------------------------------------------------
    # Mouse Scaling Helper
    # ------------------------------------------------
    def _scale_mouse(self, pos):
        window_w, window_h = pygame.display.get_surface().get_size()
        game_w, game_h = self.screen.get_size()

        scale_x = game_w / window_w
        scale_y = game_h / window_h

        return (pos[0] * scale_x, pos[1] * scale_y)

    # ------------------------------------------------
    # Event Handling
    # ------------------------------------------------
    def handle_event(self, event):

        # -------------------------
        # INVEST POPUP
        # -------------------------
        if self.state == "INVEST":

            scaled_pos = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                scaled_pos = self._scale_mouse(event.pos)

            result = self.invest_popup.handle_event(event, scaled_pos)

            if isinstance(result, int):
                self.clear_prompt()

                self.invest_amount = result

                # Deduct money
                self.game_state.money -= result
                self.money = self.game_state.money

                # Start mini-game
                self.screens["TRADING_SIM"].start(result)
                self.change_screen("TRADING_SIM")
                self.state = None
                return

            if result == "cancel":
                self.clear_prompt()
                self.state = None
                return

            return  # Block all other input

        # -------------------------
        # CONFIRM TRADE POPUP
        # -------------------------
        if self.state == "CONFIRM_TRADE":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                scaled_pos = self._scale_mouse(event.pos)
                action = self.confirm_trade.handle_click(scaled_pos)

                if action == "yes":
                    self.clear_prompt()

                    # Prevent negative trades
                    if self.game_state.trades_today >= self.game_state.max_trades_per_day:
                        self.game_state.time_of_day = "NIGHT"
                        self.change_screen("RECOVERY_ROOM")
                        self.state = None
                        return

                    # Spend trade + stress
                    self.game_state.record_trade()

                    # If NIGHT triggered
                    if self.game_state.time_of_day == "NIGHT":
                        self.change_screen("RECOVERY_ROOM")
                        self.state = None
                        return

                    # Open investment popup
                    self.invest_popup = InvestmentPopup(
                        self.screen, self.font, self.money
                    )
                    self.state = "INVEST"

                elif action == "no":
                    self.clear_prompt()
                    self.state = None

            return

        # -------------------------
        # PAUSE MENU
        # -------------------------
        if self.state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                scaled_pos = self._scale_mouse(event.pos)
                action = self.pause_menu.handle_click(scaled_pos)
                self._handle_pause_action(action)
            return

        # -------------------------
        # SETTINGS MENU
        # -------------------------
        if self.state == "SETTINGS":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                scaled_pos = self._scale_mouse(event.pos)
                action = self.settings_menu.handle_click(scaled_pos)
                self._handle_settings_action(action)
            return

        # -------------------------
        # NORMAL GAMEPLAY
        # -------------------------
        self.screens[self.current_screen].handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_mouse_click(event.pos)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.toggle_pause()

    # ------------------------------------------------
    # Mouse Click Handling
    # ------------------------------------------------
    def _handle_mouse_click(self, mouse_pos):
        scaled = self._scale_mouse(mouse_pos)

        if self.state is None:
            if self.pause_button_rect.collidepoint(scaled):
                self.toggle_pause()

    # ------------------------------------------------
    # Pause Menu Actions
    # ------------------------------------------------
    def _handle_pause_action(self, action):
        if action == "resume":
            self.toggle_pause()
        elif action == "settings":
            self.state = "SETTINGS"
        elif action == "exit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _handle_settings_action(self, action):
        if action == "back":
            self.state = "PAUSED"
        elif action == "toggle_fullscreen":
            pygame.display.toggle_fullscreen()

    # ------------------------------------------------
    # Prompt Text
    # ------------------------------------------------
    def show_prompt(self, text):
        self.prompt_text = text
        self.prompt_pos = None

    def show_prompt_at(self, text, x, y):
        self.prompt_text = text
        self.prompt_pos = (x, y)

    def clear_prompt(self):
        self.prompt_text = None
        self.prompt_pos = None

    # ------------------------------------------------
    # Pause Toggle
    # ------------------------------------------------
    def toggle_pause(self):
        self.paused = not self.paused
        self.state = "PAUSED" if self.paused else None

    # ------------------------------------------------
    # Update
    # ------------------------------------------------
    def update(self, dt, game_state):

        # Store reference
        self.game_state = game_state

        # Sync HUD
        self.money = game_state.money
        self.day = game_state.day
        self.actions_left = game_state.max_trades_per_day - game_state.trades_today
        self.stress = game_state.stress
        self.max_stress = game_state.max_stress

        # NIGHT triggers Recovery Room automatically
        if game_state.time_of_day == "NIGHT" and self.current_screen not in ("RECOVERY_ROOM", "NIGHTMARE", "GAME_OVER"):
            self.clear_prompt()
            self.state = None
            self.change_screen("RECOVERY_ROOM")
            return

        # Nightmare triggers immediately
        if game_state.is_nightmare() and self.current_screen != "NIGHTMARE": 
            self.clear_prompt()
            self.state = None
            self.change_screen("NIGHTMARE")
            return

        # Always update TradingSimScreen
        if self.current_screen == "TRADING_SIM":
            self.screens["TRADING_SIM"].update(dt, game_state)
            return

        # Normal updates
        if self.state is None:
            self.screens[self.current_screen].update(dt, game_state)

    # ------------------------------------------------
    # Draw
    # ------------------------------------------------
    def draw(self, surface):
        self.screens[self.current_screen].draw(surface)


        if self.current_screen == "NIGHTMARE":
            return

        if self.state is None:
            self._draw_pause_button(surface)
            self._draw_hud(surface)

        elif self.state == "PAUSED":
            self.pause_menu.draw()

        elif self.state == "SETTINGS":
            self.settings_menu.draw()

        elif self.state == "CONFIRM_TRADE":
            self.confirm_trade.draw()

        elif self.state == "INVEST":
            self.invest_popup.draw()

        if self.prompt_text and self.state is None:
            surf = self.font.render(self.prompt_text, True, (255, 255, 255))

            if self.prompt_pos:
                x, y = self.prompt_pos
                surface.blit(surf, (x - surf.get_width() // 2, y))
            else:
                h = surface.get_height()
                surface.blit(surf, (20, h - 40))

    # ------------------------------------------------
    # HUD Drawing
    # ------------------------------------------------
    def _draw_pause_button(self, surface):
        pygame.draw.rect(surface, (200, 200, 200), self.pause_button_rect)
        pygame.draw.line(surface, (0, 0, 0),
                         (self.pause_button_rect.x + 10, self.pause_button_rect.y + 8),
                         (self.pause_button_rect.x + 10, self.pause_button_rect.y + 24), 3)
        pygame.draw.line(surface, (0, 0, 0),
                         (self.pause_button_rect.x + 20, self.pause_button_rect.y + 8),
                         (self.pause_button_rect.x + 20, self.pause_button_rect.y + 24), 3)

    def _draw_hud(self, surface):
        money_surf = self.font.render(f"Money: ${self.money}", True, (255, 255, 255))
        day_surf = self.font.render(f"Day: {self.day}", True, (255, 255, 255))
        actions_surf = self.font.render(f"Trades Left: {self.actions_left}", True, (255, 255, 255))
        stress_surf = self.font.render(f"Stress: {self.stress}/{self.max_stress}", True, (255, 255, 255))

        surface.blit(money_surf, (20, 20))
        surface.blit(day_surf, (20, 50))
        surface.blit(actions_surf, (20, 80))
        surface.blit(stress_surf, (20, 110))

