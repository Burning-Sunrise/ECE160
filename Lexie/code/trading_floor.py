import sys
import time
import random
import pygame
from ai_pipeline import AIPipeline
from input_handler import handle_input
from tick_generator import generate_tick, add_wicks_to_existing
from config import *


class TradingFloor:
    def __init__(self, market, symbols, use_real_data=True):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("SURVIVAL TERMINAL")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier", 18)
        self.big_font = pygame.font.SysFont("Courier", 32, bold=True)

        #AI Integration
        self.ai = AIPipeline()
        self.ai_prediction = None

        # INSIDER TERMINAL STATE 
        self.insider_active = False
        self.insider_timer = 0
        self.insider_cooldown = 0
        self.insider_cost = 50


        self.market = market
        self.symbols = symbols
        self.current_index = 0
        self.current_symbol = self.symbols[self.current_index]

        # Per-symbol buffers
        self.buffers = {}
        self.current_price = {}
        self.last_tick = {}


        for sym in self.symbols:
            if use_real_data:
                hist = self.market.get_history(sym, 200)
                buf = list(hist) if hist else []
            else:
                buf = []
            # Fill to 50 candles
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
                    buf.append({
                        "open": 100.0,
                        "close": 100.0,
                        "high": 100.0,
                        "low": 100.0,
                    })
            add_wicks_to_existing(buf)

            self.buffers[sym] = buf
            self.current_price[sym] = buf[-1]["close"]
            self.last_tick[sym] = pygame.time.get_ticks()

        self.portfolio = START_CASH
        self.position = {}
        self.start_time = time.time()
        self.running = True
        self.shake_timer = 0
        self.show_holdings = False


    # DRAW CHART 
    def _draw_chart(self):
        # Vertical shake only
        frame_offset_y = random.randint(-self.shake_timer, self.shake_timer)

        buf = self.buffers[self.current_symbol]
        visible = buf[-50:]

        lows = [c["low"] for c in visible]
        highs = [c["high"] for c in visible]
        low = min(lows)
        high = max(highs)
        p_range = max(high - low, 0.1)

        def py(p):
            return 150 + 400 - ((p - low) / p_range * 400)

        # Grid (no X shake)
        for i in range(0, WIDTH, 50):
            pygame.draw.line(self.screen, GRID, (i, 0), (i, HEIGHT))
        for i in range(0, HEIGHT, 50):
            pygame.draw.line(self.screen, GRID, (0, i + frame_offset_y), (WIDTH, i + frame_offset_y))

        # REAL CANDLES — shift left to make room for ghost candles
        x = WIDTH - 350   # <-- moved left so ghost candles fit

        for c in reversed(visible):
            color = GREEN if c["close"] >= c["open"] else RED
            y_o = py(c["open"])
            y_c = py(c["close"])
            y_h = py(c["high"])
            y_l = py(c["low"])

            # wick
            pygame.draw.line(self.screen, color,
                            (x + 6, y_h + frame_offset_y),
                            (x + 6, y_l + frame_offset_y), 1)

            # body
            rect_height = max(abs(y_o - y_c), 3)
            pygame.draw.rect(self.screen, color,
                            (x, min(y_o, y_c) + frame_offset_y, 13, rect_height))

            x -= 18

        # last real candle X
        rightmost_x = WIDTH - 350

        # ghost candles start immediately to the right
        ghost_x = rightmost_x + 18
        self.chart_right_edge = ghost_x

        # GHOST FUTURE CANDLES — FIXED SCALING
        if self.insider_active and self.ai_prediction:
            print("GHOST LOOP RUNNING, COUNT:", len(self.ai_prediction))
            pygame.draw.line(
            self.screen,
            (255, 255, 0),
            (ghost_x, 150),
            (ghost_x, 550),
            3
        )

            for i, c in enumerate(self.ai_prediction[:10]):
                # use model values directly — NO SCALING
                o = c["open"]
                h = c["high"]
                l = c["low"]
                cl = c["close"]
                
                # rebase ghost candles to current price
                current = visible[-1]["close"]
                offset = current - o

                o += offset
                h += offset
                l += offset
                cl += offset

                # clamp to chart range
                # normalize ghost candles into the real chart range
                o = max(low, min(high, o))
                h = max(low, min(high, h))
                l = max(low, min(high, l))
                cl = max(low, min(high, cl))


                color = (0, 255, 0) if cl >= o else (255, 0, 0)
                alpha = 200 - int(i * (200 / 10))

                print("GHOST Y:", py(c["high"]), py(c["low"]), py(c["open"]), py(c["close"]))


                # wick
                pygame.draw.line(
                    self.screen,
                    (0, 255, 255),
                    (ghost_x + 6, py(h) + frame_offset_y),
                    (ghost_x + 6, py(l) + frame_offset_y),
                    4
                )


                # body
                top = py(max(o, cl))
                height = max(abs(py(o) - py(cl)), 4)

                s = pygame.Surface((13, height), pygame.SRCALPHA)
                s.fill((*color, alpha))
                self.screen.blit(s, (ghost_x, top + frame_offset_y))

                ghost_x += 16

    # DRAW UI
    def draw(self):
        if self.shake_timer > 0:
            self.shake_timer -= 1

        # Background glow
        current_bg = list(BG)
        if self.current_symbol in self.position:
            entry = self.position[self.current_symbol]["entry"]
            units = self.position[self.current_symbol]["units"]
            price = self.current_price[self.current_symbol]
            pnl = (price - entry) *  units
            if pnl > 0:
                current_bg[1] = min(50, 7 + int(pnl / 10))
            if pnl < 0:
                current_bg[0] = min(50, 5 + int(abs(pnl) / 10))
        self.screen.fill(current_bg)

        # Chart
        self._draw_chart()

        # Header
        pygame.draw.rect(self.screen, (10, 12, 15), (0, 0, WIDTH, 110))


        # Tabs
        tab_x = 30
        for sym in self.symbols:
            active = (sym == self.current_symbol)
            color = GOLD if active else WHITE
            label = f"[{sym}]" if active else sym
            self.screen.blit(self.font.render(label, True, color), (tab_x, 5))
            tab_x += 120

        self.screen.blit(self.font.render("[H] HOLDINGS", True, (150, 150, 160)), (30, 90))

        # Timer + portfolio
        elapsed = time.time() - self.start_time
        rem = max(0, int(SESSION_TIME - elapsed))

        cash_color = GOLD if self.portfolio >= MED_GOAL else WHITE
        self.screen.blit(self.big_font.render(f"PORTFOLIO: ${self.portfolio:.2f}", True, cash_color), (30, 35))
        self.screen.blit(self.font.render(f"TIME UNTIL MARKET CLOSE: {rem}s",
                                          True, RED if rem < 20 else WHITE), (30, 70))
        self.screen.blit(self.font.render(f"GOAL: ${MED_GOAL}", True, (100, 100, 110)), (750, 70))

        # Trade info
        if self.current_symbol in self.position:
            entry = self.position[self.current_symbol]["entry"]
            units = self.position[self.current_symbol]["units"]
            price = self.current_price[self.current_symbol]
            pnl = (price - entry) * units
            col = GREEN if pnl >= 0 else RED
            self.screen.blit(self.font.render(f"UNREALIZED PNL: ${pnl:+.2f}", True, col), (400, 35))
            self.screen.blit(self.font.render("[S] SELL (EXIT)", True, WHITE), (750, 35))
        else:
            self.screen.blit(self.font.render("[B] BUY 20 UNITS", True, GREEN), (750, 35))

        # QUANT ORACLE UI
        if self.insider_active:
            label = "[I] QUANT ORACLE (ACTIVE)"
            col = GOLD

        elif self.insider_cooldown > 0:
            label = f"[I] QUANT ORACLE (COOLDOWN {self.insider_cooldown//60}s)"
            col = (120, 120, 120)

        elif self.portfolio < self.insider_cost:
            label = "[I] QUANT ORACLE (INSUFFICIENT FUNDS)"
            col = (120, 80, 80)

        else:
            label = f"[I] QUANT ORACLE (${self.insider_cost})"
            col = GOLD


        self.screen.blit(self.font.render(label, True, col), (650, 55))

        # HOLDINGS PANEL (left slide-in)
        if self.show_holdings:
            panel_width = 250
            pygame.draw.rect(self.screen, (20, 20, 25), (0, 0, panel_width, HEIGHT))

            y = 20
            self.screen.blit(self.font.render("HOLDINGS", True, GOLD), (20, y))
            y += 40

            # Cash
            self.screen.blit(self.font.render(f"CASH: ${self.portfolio:.2f}", True, WHITE), (20, y))
            y += 30

            # Total portfolio value
            total_value = self.portfolio
            for sym, pos in self.position.items():
                total_value += pos["units"] * self.current_price[sym]

            self.screen.blit(self.font.render(f"TOTAL VALUE: ${total_value:.2f}", True, WHITE), (20, y))
            y += 40

            # Each position
            for sym, pos in self.position.items():
                price = self.current_price[sym]
                pnl = (price - pos["entry"]) * pos["units"]
                col = GREEN if pnl >= 0 else RED

                self.screen.blit(self.font.render(sym, True, GOLD), (20, y))
                y += 25
                self.screen.blit(self.font.render(f"Units: {pos['units']}", True, WHITE), (20, y))
                y += 25
                self.screen.blit(self.font.render(f"Avg: ${pos['entry']:.2f}", True, WHITE), (20, y))
                y += 25
                self.screen.blit(self.font.render(f"PNL: ${pnl:+.2f}", True, col), (20, y))
                y += 40

        pygame.display.flip()

    # MAIN LOOP 
    def run(self):
        while self.running:
            print("INSIDER ACTIVE", self.insider_active)

            handle_input(self)

            # Micro-ticks for ALL symbols
            now = pygame.time.get_ticks()
            for sym in self.symbols:
                if now - self.last_tick[sym] > TICK_SPEED:
                    generate_tick(self, sym)
                    self.last_tick[sym] = now


            # QUANT TIMERS
            if self.insider_active:
                self.insider_timer -= 1
                if self.insider_timer <= 0:
                    self.insider_active = False

            if self.insider_cooldown > 0:
                self.insider_cooldown -= 1

            # End session
            if time.time() - self.start_time > SESSION_TIME:
                self.running = False

            self.draw()
            self.clock.tick(FPS)

        self.final_screen()

        