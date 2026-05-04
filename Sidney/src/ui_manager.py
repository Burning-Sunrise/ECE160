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

        self.state = None
        self.paused = False

        self.pause_menu = PauseMenu(self.screen, self.font)
        self.settings_menu = SettingsMenu(self.screen, self.font)

        self.pause_button_rect = pygame.Rect(0, 0, 32, 32)
        self._position_pause_button()

        self.money = 0
        self.day = 1
        self.actions_left = 3
        self.mood = 0
        self.max_mood = 100

        self.invest_popup = None
        self.invest_amount = None

        self.prompt_text = None
        self.prompt_pos = None

        self.screens = {
            "TRADING_FLOOR": TradingFloorScreen(),
            "TRADING_SIM": TradingSimScreen(),
            "RECOVERY_ROOM": RecoveryRoomScreen(),
            "NIGHTMARE": NightmareScreen(),
            "GAME_OVER": GameOverScreen(),
        }
        self.current_screen = "TRADING_FLOOR"
        self.confirm_trade = ConfirmTradePopup(self.screen, self.font)

        for screen in self.screens.values():
            screen.ui = self

    # ------------------------------------------------
    # Screen Management
    # ------------------------------------------------
    def change_screen(self, new_screen):
        if new_screen in self.screens:
            self.current_screen = new_screen

    # ------------------------------------------------
    # Pause Button
    # ------------------------------------------------
    def _position_pause_button(self):
        w = self.screen.get_width()
        self.pause_button_rect.topright = (w - 8, 8)

    # ------------------------------------------------
    # Event Handling
    # ------------------------------------------------
    def handle_event(self, event):

        # -------------------------
        # INVEST POPUP
        # -------------------------
        if self.state == "INVEST":
            result = self.invest_popup.handle_event(event)

            if isinstance(result, int):
                self.invest_amount = result
                self.screens["TRADING_SIM"].start(self.invest_amount)
                self.change_screen("TRADING_SIM")
                self.state = None

            elif result == "cancel":
                self.state = None

            return  # block all other input

        # -------------------------
        # CONFIRM TRADE POPUP
        # -------------------------
        if self.state == "CONFIRM_TRADE":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self.confirm_trade.handle_click(event.pos)

                if action == "yes":
                    self.invest_popup = InvestmentPopup(
                        self.screen, self.font, self.money
                    )
                    self.state = "INVEST"

                elif action == "no":
                    self.state = None

            return

        # -------------------------
        # PAUSE MENU
        # -------------------------
        if self.state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self.pause_menu.handle_click(event.pos)
                self._handle_pause_action(action)
            return

        # -------------------------
        # SETTINGS MENU
        # -------------------------
        if self.state == "SETTINGS":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                action = self.settings_menu.handle_click(event.pos)
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
        window_w, window_h = pygame.display.get_surface().get_size()
        game_w, game_h = self.screen.get_size()

        scale_x = game_w / window_w
        scale_y = game_h / window_h

        mouse_pos = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

        if self.state is None:
            if self.pause_button_rect.collidepoint(mouse_pos):
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

        # Sync HUD values
        self.money = game_state.money
        self.day = game_state.day
        self.actions_left = game_state.max_trades_per_day - game_state.trades_today
        self.mood = game_state.stress

        if self.state is None:
            self.screens[self.current_screen].update(dt, game_state)

    # ------------------------------------------------
    # Draw
    # ------------------------------------------------
    def draw(self, surface):
        self.screens[self.current_screen].draw(surface)

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
    def _draw_hud(self, surface):
        x = 20
        y = 20

        self.draw_mood_bar(surface, x, y, 200, 20, self.mood, self.max_mood)
        y += 30

        self.draw_money(surface, x, y, self.money)
        y += 24

        self.draw_day(surface, x, y, self.day)
        y += 24

        self.draw_actions_left(surface, x, y, self.actions_left)

    def draw_mood_bar(self, surface, x, y, width, height, mood_value, max_mood):
        pygame.draw.rect(surface, (0, 0, 0), (x, y, width, height), 3)

        mood_value = max(0, min(max_mood, mood_value))
        inner_width = width - 6
        fill_width = int((mood_value / max_mood) * inner_width)

        if mood_value < max_mood * 0.4:
            color = (80, 200, 80)
        elif mood_value < max_mood * 0.7:
            color = (230, 200, 40)
        else:
            color = (200, 60, 60)

        pygame.draw.rect(surface, color, (x + 3, y + 3, fill_width, height - 6))

        label = self.font.render("Mood", False, (255, 255, 255))
        surface.blit(label, (x + width + 8, y))

    def draw_money(self, surface, x, y, money):
        text = self.font.render(f"Money: ${money}", False, (255, 255, 255))
        surface.blit(text, (x, y))

    def draw_day(self, surface, x, y, day):
        text = self.font.render(f"Day: {day}", False, (255, 255, 255))
        surface.blit(text, (x, y))

    def draw_actions_left(self, surface, x, y, actions_left):
        text = self.font.render(f"Trades left: {actions_left}", False, (255, 255, 255))
        surface.blit(text, (x, y))

    # ------------------------------------------------
    # Pause Button Drawing
    # ------------------------------------------------
    def _draw_pause_button(self, surface):
        pygame.draw.rect(surface, (40, 40, 40), self.pause_button_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.pause_button_rect, 2)

        bar_width = 6
        bar_height = 16
        gap = 4

        x1 = self.pause_button_rect.x + 8
        x2 = x1 + bar_width + gap
        y = self.pause_button_rect.y + (self.pause_button_rect.height - bar_height) // 2

        pygame.draw.rect(surface, (220, 220, 220), (x1, y, bar_width, bar_height))
        pygame.draw.rect(surface, (220, 220, 220), (x2, y, bar_width, bar_height))
#end of code