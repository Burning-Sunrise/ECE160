import pygame
import os
import time
from settings import NIGHTMARE_WIDTH, NIGHTMARE_HEIGHT
from game.boss import Boss
from game.nightmare_player import Player as NightmarePlayer

ANIMATION_INTERVAL = 0.2
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSET_DIR = os.path.join(BASE_DIR, "assets")


class NightmareScreen:
    def __init__(self):
        self.ui = None
        self.entered = False
        self.phase = "BATTLE"
        self.timer = 0
        self.player = None
        self.boss = None
        self.pulse_group = None
        self.bg_frames = None
        self.heart_full = None
        self.heart_empty = None
        self.assets_loaded = False

    def _load_assets(self):
        try:
            sheet = pygame.image.load(
                os.path.join(ASSET_DIR, "bg", "fight.png")).convert()
            frames = []
            for i in range(12):
                rect = pygame.Rect(i * 320, 0, 320, 180)
                frame = sheet.subsurface(rect)
                frames.append(pygame.transform.scale(
                    frame, (NIGHTMARE_WIDTH, NIGHTMARE_HEIGHT)))
            self.bg_frames = frames
        except Exception as e:
            print(f"Background load failed: {e}")
            self.bg_frames = [pygame.Surface((NIGHTMARE_WIDTH, NIGHTMARE_HEIGHT))] * 12

        try:
            self.heart_full = pygame.image.load(
                os.path.join(ASSET_DIR, "other", "heart.png")).convert_alpha()
            self.heart_empty = pygame.image.load(
                os.path.join(ASSET_DIR, "other", "heart_empty.png")).convert_alpha()
        except pygame.error as e:
            print(f"Heart load failed: {e}")
            self.heart_full = pygame.Surface((80, 80)); self.heart_full.fill((255, 0, 0))
            self.heart_empty = pygame.Surface((80, 80)); self.heart_empty.fill((50, 50, 50))

        self.heart_full = pygame.transform.scale(self.heart_full, (80, 80))
        self.heart_empty = pygame.transform.scale(self.heart_empty, (80, 80))
        self.assets_loaded = True

    def _new_battle(self):
        self.player = NightmarePlayer(200, 400)
        self.boss = Boss(1000, 400, self.player)
        self.pulse_group = pygame.sprite.Group()

    def reset(self):
        self.phase = "BATTLE"
        self.timer = 0
        if not self.assets_loaded:
            self._load_assets()
        self._new_battle()

    def handle_event(self, event):
        if self.phase != "BATTLE":
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.player.jump()

    def update(self, dt, game_state):
        if not self.entered:
            self.reset()
            self.entered = True

        self.timer += dt

        if self.phase == "BATTLE":
            self._update_battle()
        elif self.phase == "DEATH":
            if self.timer > 3.0:
                self.entered = False
                self.ui.change_screen("GAME_OVER")
        elif self.phase == "VICTORY":
            if self.timer > 2.0:
                game_state.add_money(500)
                game_state.stress = 0
                game_state.advance_day()
                self.entered = False
                self.ui.change_screen("TRADING_FLOOR")

    def _update_battle(self):
        self.player.update()
        self.boss.update(self.pulse_group)
        self.pulse_group.update()

        self.player.check_hit_boss(self.boss)

        if self.boss.status != 'death' and self.player.rect.colliderect(self.boss.rect):
            self.player.take_damage()

        atk_rect = self.boss.get_attack_hitbox()
        if atk_rect and self.player.rect.colliderect(atk_rect):
            self.player.take_damage()

        for pulse in self.pulse_group:
            if getattr(pulse, 'is_dangerous', True) and \
                    self.player.rect.colliderect(pulse.rect):
                self.player.take_damage()
                break

        if self.boss.hp <= 0:
            self.phase = "VICTORY"
            self.timer = 0
        elif self.player.hp <= 0:
            self.phase = "DEATH"
            self.timer = 0

    def draw(self, surface):
        if not self.entered:
            surface.fill((40, 0, 40))
            return

        self._draw_battle(surface)

        if self.phase == "DEATH":
            overlay = pygame.Surface((NIGHTMARE_WIDTH, NIGHTMARE_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            surface.blit(overlay, (0, 0))
            font = pygame.font.SysFont("Arial", 100)
            txt = font.render("You die", True, (200, 50, 50))
            rect = txt.get_rect(center=(NIGHTMARE_WIDTH // 2, NIGHTMARE_HEIGHT // 2))
            surface.blit(txt, rect)
        elif self.phase == "VICTORY":
            overlay = pygame.Surface((NIGHTMARE_WIDTH, NIGHTMARE_HEIGHT))
            overlay.fill((0, 0, 0))
            overlay.set_alpha(180)
            surface.blit(overlay, (0, 0))
            font_big = pygame.font.SysFont("Arial", 100)
            font_med = pygame.font.SysFont("Arial", 50)
            txt1 = font_big.render("Victory!", True, (50, 200, 50))
            txt2 = font_med.render("+$500", True, (255, 255, 255))
            rect1 = txt1.get_rect(center=(NIGHTMARE_WIDTH // 2, NIGHTMARE_HEIGHT // 2 - 60))
            rect2 = txt2.get_rect(center=(NIGHTMARE_WIDTH // 2, NIGHTMARE_HEIGHT // 2 + 40))
            surface.blit(txt1, rect1)
            surface.blit(txt2, rect2)

    def _draw_battle(self, surface):
        current_time = time.time()
        bg_idx = (int(current_time / ANIMATION_INTERVAL)) % 12
        surface.blit(self.bg_frames[bg_idx], (0, 0))

        self.boss.draw(surface)

        for pulse in self.pulse_group:
            img_rect = pulse.image.get_rect(center=pulse.rect.center)
            surface.blit(pulse.image, img_rect)

        self.player.draw(surface)

        self._draw_battle_ui(surface)

    def _draw_battle_ui(self, surface):
        for i in range(7):
            img = self.heart_full if i < self.player.hp else self.heart_empty
            surface.blit(img, (30 + i * 90, 30))

        bar_w = 600
        bar_h = 20
        bar_x = (NIGHTMARE_WIDTH - bar_w) // 2
        bar_y = NIGHTMARE_HEIGHT - 50
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
        if self.boss.hp > 0:
            ratio = self.boss.hp / self.boss.max_hp
            pygame.draw.rect(surface, (200, 30, 30),
                             (bar_x, bar_y, int(bar_w * ratio), bar_h))
        pygame.draw.rect(surface, (255, 255, 255),
                         (bar_x, bar_y, bar_w, bar_h), 2)