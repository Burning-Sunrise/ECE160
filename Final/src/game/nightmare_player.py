import pygame
import os
from settings import GROUND_Y, PLAYER_INVINCIBLE_FRAMES, NIGHTMARE_WIDTH

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # --- 1. 基础配置 ---
        self.scale = 5
        self.orig_size = 64
        self.display_size = self.orig_size * self.scale  # 320x320

        # --- Sprite Sheet ---
        img_path = os.path.join(ASSET_DIR, "player", "player.png")
        try:
            self.sheet = pygame.image.load(img_path).convert_alpha()
        except Exception as e:
            print(f"加载失败: {e}")
            self.sheet = pygame.Surface((64 * 17, 64 * 14))

        self.frame_counts = [8, 12, 7, 10, 17, 5, 5, 5, 7, 6, 6, 5, 5, 15]
        self.animations = self.load_all_animations()

        # --- 3. 状态与动画 ---
        self.status = 'idle'
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations[self.status][0]
        self.flip = False

        # --- 4. 物理 ---
        self.rect = pygame.Rect(x, y, 9 * self.scale, 18 * self.scale)
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 6
        self.gravity = 1.0
        self.jump_speed = -20
        self.jump_count = 0
        self.is_on_ground = False

        # --- 5. 战斗属性 ---
        self.hp = 7
        self.is_attacking = False
        self.is_dashing = False
        self.dash_timer = 0
        self.damage_toggle = 1

        # --- 6. 无敌 & 单次攻击命中标记 ---
        self.invincible = False
        self.invincible_timer = 0
        self.attack_hit_done = False  # 当前一次攻击是否已击中过 boss

    # ----------------------------------------------------------
    # 资源
    # ----------------------------------------------------------
    def load_all_animations(self):
        actions = [
            'run', 'idle', 'dash', 'dashattack', 'whirlwind',
            'attack_up', 'attack', 'attack_down',
            'jumpup', 'jumpmid', 'jumpfall',
            'damage1', 'damage2', 'death'
        ]
        all_anims = {}
        for row, (action, count) in enumerate(zip(actions, self.frame_counts)):
            frames = []
            for col in range(count):
                rect = pygame.Rect(col * self.orig_size, row * self.orig_size,
                                   self.orig_size, self.orig_size)
                frame = self.sheet.subsurface(rect)
                scaled = pygame.transform.scale(
                    frame, (self.display_size, self.display_size))
                frames.append(scaled)
            all_anims[action] = frames
        return all_anims

    # ----------------------------------------------------------
    # 输入
    # ----------------------------------------------------------
    def get_input(self):
        keys = pygame.key.get_pressed()

        # 移动输入：冲刺(K)中和冲刺攻击中不响应；其他状态（包括普通攻击）都响应
        if not self.is_dashing and self.status != 'dashattack':
            if keys[pygame.K_d]:
                self.direction.x = 1
                self.flip = False
            elif keys[pygame.K_a]:
                self.direction.x = -1
                self.flip = True
            else:
                self.direction.x = 0

            # 只有非攻击状态才用移动来切换 run/idle，否则会打断攻击动画
            if not self.is_attacking:
                if self.direction.x != 0:
                    self.status = 'run'
                elif self.is_on_ground:
                    self.status = 'idle'

        # 冲刺 (K)
        if keys[pygame.K_k] and not self.is_dashing and not self.is_attacking:
            if self.dash_timer <= 0:
                self.is_dashing = True
                self.dash_timer = 15
                self.status = 'dash'
                self.frame_index = 0
                self.dash_direction = -1 if self.flip else 1

        # 攻击 (J)
        if keys[pygame.K_j] and not self.is_attacking:
            if self.is_dashing:
                self.is_dashing = False
                self.dash_timer = 0
                self.status = 'dashattack'
                self.direction.x = 0          # ← dashattack 期间钉住不动
            elif keys[pygame.K_w]:
                self.status = 'attack_up'
            elif keys[pygame.K_s]:
                self.status = 'attack_down'
            else:
                self.status = 'attack'

            self.is_attacking = True
            self.frame_index = 0
            self.attack_hit_done = False

    # ----------------------------------------------------------
    # 物理
    # ----------------------------------------------------------
    def apply_physics(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

        if self.is_dashing:
            move_speed = self.speed * 3.0
            self.rect.x += self.dash_direction * move_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0:
                self.is_dashing = False
                self.direction.x = 0
        else:
            self.rect.x += self.direction.x * self.speed
            if self.dash_timer > 0:
                self.dash_timer -= 1

        # 地面（用 settings.GROUND_Y）
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.direction.y = 0
            self.is_on_ground = True
            self.jump_count = 0
            if not self.is_attacking and not self.is_dashing:
                if self.direction.x == 0:
                    self.status = 'idle'
                else:
                    self.status = 'run'
        else:
            self.is_on_ground = False
            if not self.is_attacking and not self.is_dashing:
                if self.direction.y < -2:
                    self.status = 'jumpup'
                elif -2 <= self.direction.y <= 2:
                    self.status = 'jumpmid'
                else:
                    self.status = 'jumpfall'

        if self.rect.left <= 0:
            self.rect.left = 0
            if self.is_dashing:
                self.is_dashing = False
                self.dash_timer = 0
        if self.rect.right >= NIGHTMARE_WIDTH:
            self.rect.right = NIGHTMARE_WIDTH
            if self.is_dashing:
                self.is_dashing = False
                self.dash_timer = 0

    # ----------------------------------------------------------
    # 动作
    # ----------------------------------------------------------
    def jump(self):
        if self.jump_count < 2:
            self.direction.y = self.jump_speed
            self.jump_count += 1
            if not self.is_attacking:
                self.status = 'jumpup'
                self.frame_index = 0

    def get_attack_rect(self):
        if not self.is_attacking:
            return None
        if self.status == 'attack_up':
            return pygame.Rect(self.rect.centerx - 100, self.rect.top - 90, 200, 90)
        elif self.status == 'attack_down':
            return pygame.Rect(self.rect.centerx - 100, self.rect.bottom, 200, 90)
        elif self.status == 'attack':
            x = self.rect.right if not self.flip else self.rect.left - 130
            return pygame.Rect(x, self.rect.centery - 55, 130, 110)
        elif self.status == 'dashattack':
            x = self.rect.centerx - 82
            return pygame.Rect(x, self.rect.centery - 67, 165, 135)
        return None

    # ----------------------------------------------------------
    # 受伤
    # ----------------------------------------------------------
    def take_damage(self):
        if self.invincible or self.status == 'death':
            return
        self.hp -= 1
        self.invincible = True
        self.invincible_timer = PLAYER_INVINCIBLE_FRAMES
        if self.hp <= 0:
            self.hp = 0
            self.status = 'death'
        else:
            self.status = f'damage{self.damage_toggle}'
            self.damage_toggle = 2 if self.damage_toggle == 1 else 1
        self.frame_index = 0

    # ----------------------------------------------------------
    # 动画
    # ----------------------------------------------------------
    def animate(self):
        animation = self.animations[self.status]
        self.frame_index += self.animation_speed

        if self.frame_index >= len(animation):
            if self.status == 'death':
                self.frame_index = len(animation) - 1
            else:
                self.frame_index = 0
                self.is_attacking = False
                self.is_dashing = False
                self.attack_hit_done = False

        if self.status == 'dashattack' and self.frame_index < 3:
            self.frame_index += 0.4

        img = animation[int(self.frame_index)]
        self.image = pygame.transform.flip(img, self.flip, False)

    # ----------------------------------------------------------
    # 主动攻击命中检测（每帧从 main 调用）
    # ----------------------------------------------------------
    def check_hit_boss(self, boss):
        if self.attack_hit_done:
            return
        attack_rect = self.get_attack_rect()
        if attack_rect and attack_rect.colliderect(boss.rect):
            if boss.status not in ('death', 'hit'):
                boss.take_damage(1)
                self.attack_hit_done = True

    # ----------------------------------------------------------
    # 渲染 & 主循环
    # ----------------------------------------------------------
    def draw(self, surface):
        draw_x = self.rect.centerx - self.display_size // 2
        draw_y = self.rect.bottom - self.display_size
        # 无敌时让玩家闪烁
        if self.invincible and (self.invincible_timer // 4) % 2 == 0:
            return
        surface.blit(self.image, (draw_x, draw_y))

    def update(self):
        if self.status != 'death':
            self.get_input()
            self.apply_physics()
        self.animate()
        # 无敌计时
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
