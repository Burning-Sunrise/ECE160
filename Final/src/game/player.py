import pygame
import os
from settings import PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")


class Player:
    IDLE_SHEET_PATH = os.path.join(ASSET_DIR, "player", "tiny_idle.png")
    WALK_SHEET_PATH = os.path.join(ASSET_DIR, "player", "tiny_walk.png")

    FRAME_W = 32
    FRAME_H = 32

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 16, 16)

        # Movement
        self.speed = PLAYER_SPEED
        self.vel_x = 0
        self.vel_y = 0

        # Animation
        self.status = "idle"
        self.frame_index = 0
        self.animation_speed = 0.08
        self.flip = False  

        # Load sprite sheets
        self.animations = self._load_animations()
        self.image = self.animations[self.status][0]

    # ----------------------------------------
    # Asset loading
    # ----------------------------------------
    def _load_animations(self):
        return {
            "idle": self._slice_sheet(self.IDLE_SHEET_PATH, 2),
            "walk": self._slice_sheet(self.WALK_SHEET_PATH, 4),
        }

    def _slice_sheet(self, path, frame_count):
        try:
            sheet = pygame.image.load(path).convert_alpha()
        except Exception as e:
            print(f"Failed to load {path}: {e}")
            return [self._placeholder() for _ in range(frame_count)]

        frames = []
        for i in range(frame_count):
            rect = pygame.Rect(i * self.FRAME_W, 0, self.FRAME_W, self.FRAME_H)
            frames.append(sheet.subsurface(rect))
        return frames

    def _placeholder(self):
        surf = pygame.Surface((self.FRAME_W, self.FRAME_H))
        surf.fill((255, 0, 0))
        return surf

    # ----------------------------------------
    # Input
    # ----------------------------------------
    def handle_input(self, keys):
        self.vel_x = 0
        self.vel_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vel_y = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vel_y = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
            self.flip = True   
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = self.speed
            self.flip = False  

    # ----------------------------------------
    # Update
    # ----------------------------------------
    def update(self, walls):
        # Horizontal
        self.rect.x += self.vel_x
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_x > 0:
                    self.rect.right = wall.left
                elif self.vel_x < 0:
                    self.rect.left = wall.right

        # Vertical
        self.rect.y += self.vel_y
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_y > 0:
                    self.rect.bottom = wall.top
                elif self.vel_y < 0:
                    self.rect.top = wall.bottom

        # Screen bounds
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

        # Switch status based on movement
        if self.vel_x == 0 and self.vel_y == 0:
            self.status = "idle"
        else:
            self.status = "walk"

        self._animate()

    def _animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        img = animation[int(self.frame_index)]
        self.image = pygame.transform.flip(img, self.flip, False)

    # ----------------------------------------
    # Draw
    # ----------------------------------------
    def draw(self, surface):
        draw_x = self.rect.centerx - self.FRAME_W // 2
        draw_y = self.rect.centery - self.FRAME_H // 2
        surface.blit(self.image, (draw_x, draw_y))