import pygame
import os
import random
import time

from game.lexie.ai_pipeline import AIPipeline
from game.lexie.tick_generator import generate_tick, add_wicks_to_existing
from game.lexie.market_layer import MarketLayer
from game.lexie import config as lexie_config

W = lexie_config.WIDTH       # 1000
H = lexie_config.HEIGHT      # 700
BG = lexie_config.BG
GRID = lexie_config.GRID
WHITE = lexie_config.WHITE
GREEN = lexie_config.GREEN
RED = lexie_config.RED
GOLD = lexie_config.GOLD

SYMBOLS = ["NVDA", "TSLA", "AAPL", "MSFT", "AMZN"]


class TradingPanelScreen:
    def __init__(self):
        self.ui = None
        self.entered = False
        self.initialized = False

        # Trading state
        self.symbols = SYMBOLS
        self.current_index = 0
        self.current_symbol = self.symbols[0]
        self.buffers = {}
        self.current_price = {}
        self.last_tick = {}
        self.position = {}
        self.shake_timer = 0
        self.show_holdings = False

        # Insider state
        self.insider_active = False
        self.insider_timer = 0
        self.insider_cooldown = 0
        self.insider_cost = 50
        self.ai_prediction = None

        # Compatibility — input_handler / draw use self.portfolio
        self.portfolio = 0

        # Lazy
        self.market = None
        self.ai = None
        self.font = None
        self.big_font = None

    # ----------------------------------------
    # First-time setup (loads market + AI)
    # ----------------------------------------
    def _initialize(self):
        if self.initialized:
            return

        self.font = pygame.font.SysFont("Courier", 18)
        self.big_font = pygame.font.SysFont("Courier", 32, bold=True)

        print("Loading market data...")
        self.market = MarketLayer(self.symbols)
        print("Loading AI model...")
        self.ai = AIPipeline()

        for sym in self.symbols:
            hist = self.market.get_history(sym, 200)
            buf = list(hist) if hist else []
            while len(buf) < 50:
                if buf:
                    last = buf[-1]
                    move = random.uniform(-5, 5)
                    new_close = last["close"] + move
                    buf.append({
                        "open": last["close"],
                        "close": new_close,
                        "high": max(last["close"], new_close),
                        "low": min(last["close"], new_close),
                    })
                else:
                    buf.append({"open": 100.0, "close": 100.0,
                                "high": 100.0, "low": 100.0})
            add_wicks_to_existing(buf)
            self.buffers[sym] = buf
            self.current_price[sym] = buf[-1]["close"]
            self.last_tick[sym] = pygame.time.get_ticks()

        self.initialized = True

    def reset(self):
        self._initialize()
        self.show_holdings = False

    # ----------------------------------------
    # Events
    # ----------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._exit_panel()
                return

            # 1-5: switch symbol
            if pygame.K_1 <= event.key <= pygame.K_5:
                idx = event.key - pygame.K_1
                if idx < len(self.symbols):
                    self.current_index = idx
                    self.current_symbol = self.symbols[idx]
                    self.shake_timer = 5
                return

            if event.key == pygame.K_b:
                self._buy()
            elif event.key == pygame.K_s:
                self._sell()
            elif event.key == pygame.K_i:
                self._insider()
            elif event.key == pygame.K_h:
                self.show_holdings = not self.show_holdings

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if my < 40:
                tab_x = 30
                for i, sym in enumerate(self.symbols):
                    if tab_x <= mx <= tab_x + 100:
                        self.current_index = i
                        self.current_symbol = sym
                        self.shake_timer = 5
                        break
                    tab_x += 120

    # ----------------------------------------
    # Trading actions (each B/S counts as 1 trade)
    # ----------------------------------------
    def _buy(self):
        gs = self.ui.game_state
        if gs.trades_today >= gs.max_trades_per_day:
            self._exit_panel()
            return

        sym = self.current_symbol
        price = self.current_price[sym]
        units = 2
        cost = price * units
        if gs.money < cost:
            return

        gs.money = int(gs.money - cost)
        if sym not in self.position:
            self.position[sym] = {"entry": price, "units": units}
        else:
            old_entry = self.position[sym]["entry"]
            old_units = self.position[sym]["units"]
            new_units = old_units + units
            new_entry = (old_entry * old_units + price * units) / new_units
            self.position[sym]["entry"] = new_entry
            self.position[sym]["units"] = new_units
        self.shake_timer = 5
        gs.record_trade()
        

    def _sell(self):
        gs = self.ui.game_state
        if gs.trades_today >= gs.max_trades_per_day:
            self._exit_panel()
            return

        sym = self.current_symbol
        if sym not in self.position:
            return
        units = self.position[sym]["units"]
        price = self.current_price[sym]
        value = price * units * 1.5
        gs.money = int(gs.money + value)
        del self.position[sym]
        self.shake_timer = 8
        gs.record_trade()

    def _insider(self):
        gs = self.ui.game_state
        if self.insider_cooldown != 0 or self.insider_active:
            return
        if gs.money < self.insider_cost:
            return

        gs.money = int(gs.money - self.insider_cost)
        seq = self.buffers[self.current_symbol][-50:]
        pred = self.ai.predict(seq)
        converted = [{"open": float(p[0]), "high": float(p[1]),
                      "low": float(p[2]), "close": float(p[3])} for p in pred]
        self.ai_prediction = converted
        self.insider_active = True
        self.insider_timer = 180
        self.insider_cooldown = 300

    def _exit_panel(self):
        self.entered = False
        self.ui.change_screen("TRADING_FLOOR")

    # ----------------------------------------
    # Update
    # ----------------------------------------
    def update(self, dt, game_state):
        if not self.entered:
            self.reset()
            self.entered = True

        # Sync portfolio from game_state (so HUD and panel show same money)
        self.portfolio = game_state.money

        # Tick generation
        now = pygame.time.get_ticks()
        for sym in self.symbols:
            if now - self.last_tick[sym] > lexie_config.TICK_SPEED:
                generate_tick(self, sym)
                self.last_tick[sym] = now

        # Insider timers
        if self.insider_active:
            self.insider_timer -= 1
            if self.insider_timer <= 0:
                self.insider_active = False
        if self.insider_cooldown > 0:
            self.insider_cooldown -= 1

        # If trades hit max, switch to night automatically
        if game_state.trades_today >= game_state.max_trades_per_day:
            self._exit_panel()

    # ----------------------------------------
    # Draw
    # ----------------------------------------
    def draw(self, surface):
        if not self.entered or not self.initialized:
            surface.fill((0, 0, 0))
            return

        if self.shake_timer > 0:
            self.shake_timer -= 1

        # Background glow based on PNL
        bg = list(BG)
        if self.current_symbol in self.position:
            entry = self.position[self.current_symbol]["entry"]
            units = self.position[self.current_symbol]["units"]
            price = self.current_price[self.current_symbol]
            pnl = (price - entry) * units
            if pnl > 0:
                bg[1] = min(50, 7 + int(pnl / 10))
            if pnl < 0:
                bg[0] = min(50, 5 + int(abs(pnl) / 10))
        surface.fill(bg)

        self._draw_chart(surface)
        self._draw_header(surface)
        if self.show_holdings:
            self._draw_holdings(surface)

    def _draw_chart(self, surface):
        offset_y = random.randint(-self.shake_timer, self.shake_timer)
        buf = self.buffers[self.current_symbol]
        visible = buf[-50:]
        lows = [c["low"] for c in visible]
        highs = [c["high"] for c in visible]
        low = min(lows)
        high = max(highs)
        p_range = max(high - low, 0.1)

        def py(p):
            return 150 + 400 - ((p - low) / p_range * 400)

        for i in range(0, W, 50):
            pygame.draw.line(surface, GRID, (i, 0), (i, H))
        for i in range(0, H, 50):
            pygame.draw.line(surface, GRID, (0, i + offset_y), (W, i + offset_y))

        x = W - 350
        for c in reversed(visible):
            color = GREEN if c["close"] >= c["open"] else RED
            y_o = py(c["open"]); y_c = py(c["close"])
            y_h = py(c["high"]); y_l = py(c["low"])
            pygame.draw.line(surface, color, (x + 6, y_h + offset_y), (x + 6, y_l + offset_y), 1)
            rect_h = max(abs(y_o - y_c), 3)
            pygame.draw.rect(surface, color, (x, min(y_o, y_c) + offset_y, 13, rect_h))
            x -= 18

        if self.insider_active and self.ai_prediction:
            ghost_x = W - 350 + 18
            for i, c in enumerate(self.ai_prediction[:10]):
                o, h, l, cl = c["open"], c["high"], c["low"], c["close"]
                offset = visible[-1]["close"] - o
                o += offset; h += offset; l += offset; cl += offset
                o = max(low, min(high, o))
                h = max(low, min(high, h))
                l = max(low, min(high, l))
                cl = max(low, min(high, cl))
                color = (0, 255, 0) if cl >= o else (255, 0, 0)
                alpha = 200 - int(i * 20)
                pygame.draw.line(surface, (0, 255, 255),
                                (ghost_x + 6, py(h) + offset_y),
                                (ghost_x + 6, py(l) + offset_y), 4)
                top = py(max(o, cl))
                hh = max(abs(py(o) - py(cl)), 4)
                s = pygame.Surface((13, hh), pygame.SRCALPHA)
                s.fill((*color, alpha))
                surface.blit(s, (ghost_x, top + offset_y))
                ghost_x += 16

    def _draw_header(self, surface):
        gs = self.ui.game_state
        pygame.draw.rect(surface, (10, 12, 15), (0, 0, W, 110))

        # Tabs
        tab_x = 30
        for sym in self.symbols:
            active = (sym == self.current_symbol)
            color = GOLD if active else WHITE
            label = f"[{sym}]" if active else sym
            surface.blit(self.font.render(label, True, color), (tab_x, 5))
            tab_x += 120

        surface.blit(self.font.render("[H] HOLDINGS", True, (150, 150, 160)), (30, 90))

        cash_color = GOLD if gs.money >= lexie_config.MED_GOAL else WHITE
        surface.blit(self.big_font.render(f"PORTFOLIO: ${gs.money:.2f}", True, cash_color), (30, 35))
        surface.blit(self.font.render(f"Trades left: {gs.max_trades_per_day - gs.trades_today}",
                                      True, WHITE), (30, 70))
        surface.blit(self.font.render(f"GOAL: ${lexie_config.MED_GOAL}", True, (100, 100, 110)), (750, 70))

        if self.current_symbol in self.position:
            entry = self.position[self.current_symbol]["entry"]
            units = self.position[self.current_symbol]["units"]
            price = self.current_price[self.current_symbol]
            pnl = (price - entry) * units
            col = GREEN if pnl >= 0 else RED
            surface.blit(self.font.render(f"UNREALIZED PNL: ${pnl:+.2f}", True, col), (400, 35))
            surface.blit(self.font.render("[S] SELL (EXIT)", True, WHITE), (750, 35))
        else:
            surface.blit(self.font.render("[B] BUY 2 UNITS", True, GREEN), (750, 35))

        # Insider
        if self.insider_active:
            label, col = "[I] QUANT ORACLE (ACTIVE)", GOLD
        elif self.insider_cooldown > 0:
            label, col = f"[I] QUANT ORACLE (CD {self.insider_cooldown // 60}s)", (120, 120, 120)
        elif gs.money < self.insider_cost:
            label, col = "[I] QUANT ORACLE (LOW FUNDS)", (120, 80, 80)
        else:
            label, col = f"[I] QUANT ORACLE (${self.insider_cost})", GOLD
        surface.blit(self.font.render(label, True, col), (650, 55))

        # ESC hint
        surface.blit(self.font.render("[ESC] LEAVE TERMINAL", True, (150, 150, 150)), (W - 220, 90))

    def _draw_holdings(self, surface):
        gs = self.ui.game_state
        panel_w = 250
        pygame.draw.rect(surface, (20, 20, 25), (0, 0, panel_w, H))
        y = 20
        surface.blit(self.font.render("HOLDINGS", True, GOLD), (20, y)); y += 40
        surface.blit(self.font.render(f"CASH: ${gs.money:.2f}", True, WHITE), (20, y)); y += 30

        total = gs.money
        for sym, pos in self.position.items():
            total += pos["units"] * self.current_price[sym]
        surface.blit(self.font.render(f"TOTAL: ${total:.2f}", True, WHITE), (20, y)); y += 40

        for sym, pos in self.position.items():
            price = self.current_price[sym]
            pnl = (price - pos["entry"]) * pos["units"]
            col = GREEN if pnl >= 0 else RED
            surface.blit(self.font.render(sym, True, GOLD), (20, y)); y += 25
            surface.blit(self.font.render(f"Units: {pos['units']}", True, WHITE), (20, y)); y += 25
            surface.blit(self.font.render(f"Avg: ${pos['entry']:.2f}", True, WHITE), (20, y)); y += 25
            surface.blit(self.font.render(f"PNL: ${pnl:+.2f}", True, col), (20, y)); y += 40