import pygame
from settings import NIGHTMARE_WIDTH, NIGHTMARE_HEIGHT


class NightmareScreen:
    def __init__(self):
        self.ui = None
        self.phase = "BATTLE"      # BATTLE / DEATH / VICTORY
        self.timer = 0
        self.entered = False        # 是否第一次进入（用来 reset）

    def reset(self):
        """每次进入梦魇时调用，重置状态"""
        self.phase = "BATTLE"
        self.timer = 0

    # ----------------------------------------
    # Input
    # ----------------------------------------
    def handle_event(self, event):
        # 临时：按键模拟胜负，方便测试流程
        if self.phase == "BATTLE" and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.phase = "VICTORY"
                self.timer = 0
            elif event.key == pygame.K_l:
                self.phase = "DEATH"
                self.timer = 0

    # ----------------------------------------
    # Update
    # ----------------------------------------
    def update(self, dt, game_state):
        # 第一次进入时 reset
        if not self.entered:
            self.reset()
            self.entered = True

        self.timer += dt

        if self.phase == "DEATH":
            # 显示 "You die" 3 秒后进 GAME_OVER
            if self.timer > 3.0:
                self.entered = False  # 下次再进重置
                self.ui.change_screen("GAME_OVER")

        elif self.phase == "VICTORY":
            # 显示 "+$500" 2 秒后进入新一天
            if self.timer > 2.0:
                game_state.add_money(500)
                game_state.stress = 0  # 战胜梦魇 → 压力全清
                game_state.advance_day()
                self.entered = False
                self.ui.change_screen("TRADING_FLOOR")

    # ----------------------------------------
    # Draw
    # ----------------------------------------
    def draw(self, surface):
        font_big = pygame.font.SysFont("Arial", 80)
        font_med = pygame.font.SysFont("Arial", 40)

        if self.phase == "BATTLE":
            # 临时背景
            surface.fill((40, 0, 40))
            txt = font_med.render("Boss fight here (W=win, L=lose)", True, (255, 255, 255))
            rect = txt.get_rect(center=(NIGHTMARE_WIDTH // 2, NIGHTMARE_HEIGHT // 2))
            surface.blit(txt, rect)

        elif self.phase == "DEATH":
            surface.fill((0, 0, 0))
            txt = font_big.render("You die", True, (200, 50, 50))
            rect = txt.get_rect(center=(NIGHTMARE_WIDTH // 2, NIGHTMARE_HEIGHT // 2))
            surface.blit(txt, rect)

        elif self.phase == "VICTORY":
            surface.fill((0, 0, 0))
            txt1 = font_big.render("Victory!", True, (50, 200, 50))
            txt2 = font_med.render("+$500", True, (255, 255, 255))
            rect1 = txt1.get_rect(center=(NIGHTMARE_WIDTH // 2, NIGHTMARE_HEIGHT // 2 - 50))
            rect2 = txt2.get_rect(center=(NIGHTMARE_WIDTH // 2, NIGHTMARE_HEIGHT // 2 + 50))
            surface.blit(txt1, rect1)
            surface.blit(txt2, rect2)