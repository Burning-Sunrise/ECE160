import pygame
import random
from settings import (
    WIDTH, GROUND_Y, HEIGHT, 
    BOSS_WALK_SPEED, BOSS_RUN_SPEED, BOSS_DASH_SPEED,
    BOSS_ATTACK_RANGE, BOSS_ATTACK_COOLDOWN,
    BOSS_PULSE_RECOVER, BOSS_INTRO_DELAY,
)
from projectile import Pulse


class Boss(pygame.sprite.Sprite):
    # 状态枚举（仅作注释参考）
    # idle / walk / run / attack / pulse / dash / hit / death

    def __init__(self, x, y, player):
        super().__init__()
        self.player = player
        self.scale = 5
        self.size = 150  # 原始帧尺寸 (150x150)

        # --- 1. 战斗属性 ---
        self.hp = 10
        self.max_hp = 10
        self.is_invincible = False  # player.check_hit_boss 会读这个
        self.has_hit_player = False  # 单次攻击只伤害玩家一次

        # --- 2. 状态/朝向/计时 ---
        self.status = 'idle'
        self.flip = True  # 玩家在左侧 -> 默认朝左
        self.start_time = pygame.time.get_ticks()
        self.last_attack_end = 0
        self.pulse_spawned = False
        self.pulse_recover_until = 0  # 脉冲消失后的额外硬直时间戳

        # --- 3. 加载动画 ---
        self.frame_index = 0
        self.animations = self.load_assets()
        self.pulse_frames = self.load_pulse_assets()

        # --- 4. 碰撞箱 14x54 -> 70x270 ---
        self.image = self.animations['idle'][0]
        self.rect = pygame.Rect(0, 0, 16 * self.scale, 54 * self.scale)
        self.rect.centerx = x
        self.rect.bottom = GROUND_Y  # 强制贴地，y 参数仅作语义保留

    # ----------------------------------------------------------
    # 资源加载
    # ----------------------------------------------------------
    def load_assets(self):
        # 格式: '动作': (路径, 总帧数, 每行列数)
        # 如果你的 spritesheet 是单行排布，把 cols 改成 总帧数 即可
        asset_info = {
            'idle':   ("image/boss/boss_idle/boss_idle.png",         17, 6),
            'walk':   ("image/boss/boss_walk/boss_walk.png",         12, 12),
            'run':    ("image/boss/boss_run/boss_run.png",           6,  6),
            'attack': ("image/boss/boss_attack_air/boss_attack_air.png", 7, 3),
            'pulse':  ("image/boss/boss_attack_pulse/boss_attack_pulse.png", 5, 5),
            'dash':   ("image/boss/boss_attack_dash/boss_attack_dash.png", 11, 11),
            'hit':    ("image/boss/boss_hit/boss_hit.png",           3,  3),
            'death':  ("image/boss/boss_death/boss_death.png",       19, 3),
        }

        all_anims = {}
        for action, (path, count, cols) in asset_info.items():
            try:
                sheet = pygame.image.load(path).convert_alpha()
                frames = []
                for i in range(count):
                    r = i // cols
                    c = i % cols
                    rect = pygame.Rect(c * self.size, r * self.size,
                                       self.size, self.size)
                    frame = sheet.subsurface(rect)
                    scaled = pygame.transform.scale(
                        frame, (self.size * self.scale, self.size * self.scale))
                    frames.append(scaled)
                all_anims[action] = frames
            except Exception as e:
                print(f"找不到/加载失败: {path}，错误: {e}")
                all_anims[action] = [
                    pygame.Surface((self.size * self.scale, self.size * self.scale))
                ]
        return all_anims

    def load_pulse_assets(self):
        path = "image/boss/effects/pulse.png"
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frames = []
            for i in range(8):
                sub = sheet.subsurface(
                    (i * 256, 0, 256, 128))
                scaled = pygame.transform.scale(
                    sub, (256 , 128 ))
                frames.append(scaled)
            return frames
        except Exception as e:
            print(f"找不到脉冲图片: {path}，错误: {e}")
            return [pygame.Surface((256 ,
                                    128 )) for _ in range(8)]

    # ----------------------------------------------------------
    # 主更新
    # ----------------------------------------------------------
    def update(self, pulse_group):
        if self.status == 'death':
            self.animate(pulse_group)
            return

        now = pygame.time.get_ticks()

        # 1. 开局静止
        if now - self.start_time < BOSS_INTRO_DELAY:
            self.status = 'idle'
            self.flip = self.player.rect.centerx < self.rect.centerx
            self.animate(pulse_group)
            return

        # 2. 受击硬直
        if self.status == 'hit':
            self.animate(pulse_group)
            return

        # 3. 各状态行为
        if self.status == 'idle':
            self.flip = self.player.rect.centerx < self.rect.centerx
            # 冷却结束才决定下一次攻击
            if now - self.last_attack_end > BOSS_ATTACK_COOLDOWN \
                    and now > self.pulse_recover_until:
                self.decide_attack()

        elif self.status == 'run':
            self._chase(BOSS_RUN_SPEED)

        elif self.status == 'walk':
            self._chase(BOSS_WALK_SPEED)

        elif self.status == 'dash':
            # 纵向冲刺
            self.rect.y += BOSS_DASH_SPEED
            if self.rect.bottom >= HEIGHT - 80:
                self.rect.bottom = HEIGHT - 80

        # attack / pulse 只播动画，不需要额外物理

        self.animate(pulse_group)

    def _chase(self, speed):
        """追踪玩家；进入攻击范围就改为 attack。"""
        self.flip = self.player.rect.centerx < self.rect.centerx
        dist = abs(self.player.rect.centerx - self.rect.centerx)
        if dist > BOSS_ATTACK_RANGE:
            if self.player.rect.centerx > self.rect.centerx:
                self.rect.x += speed
            else:
                self.rect.x -= speed
        else:
            self.status = 'attack'
            self.frame_index = 0
            self.has_hit_player = False

    # ----------------------------------------------------------
    # 决定攻击
    # ----------------------------------------------------------
    def decide_attack(self):
        choice = random.choice(['normal', 'pulse', 'dash'])
        self.frame_index = 0
        self.has_hit_player = False

        if choice == 'normal':
            dist = abs(self.player.rect.centerx - self.rect.centerx)
            self.flip = self.player.rect.centerx < self.rect.centerx
            if dist > BOSS_ATTACK_RANGE:
                # 远距离 -> 用 run 接近，靠近后会自动切到 attack
                self.status = 'run'
            else:
                self.status = 'attack'

        elif choice == 'pulse':
            # 瞬移到与玩家相反的屏幕边缘，然后面朝玩家发射
            if self.player.rect.centerx < WIDTH // 2:
                # 玩家在左 -> boss 去右
                self.rect.right = WIDTH - 50
                self.flip = True   # 朝左发射
            else:
                self.rect.left = 50
                self.flip = False  # 朝右发射
            self.rect.bottom = GROUND_Y
            self.status = 'pulse'
            self.pulse_spawned = False

        elif choice == 'dash':
            # 瞬移到玩家正上方屏幕外
            self.rect.centerx = self.player.rect.centerx
            self.rect.bottom = -20
            self.flip = self.player.rect.centerx < self.rect.centerx
            self.status = 'dash'

    # ----------------------------------------------------------
    # 动画 + 帧事件
    # ----------------------------------------------------------
    def animate(self, pulse_group):
        anim = self.animations[self.status]
        if self.status in ('attack', 'pulse', 'dash'):
            self.frame_index += 0.1     # ← 越小前摇越长（默认 0.2）
        else:
            self.frame_index += 0.2

        # 脉冲发射 -> 第三帧
        if self.status == 'pulse' and not self.pulse_spawned \
                and int(self.frame_index) >= 2:
            offset = -100 if self.flip else 100
            p = Pulse(self.rect.centerx + offset, self.rect.centery-80,
                    self.flip, self.pulse_frames)
            pulse_group.add(p)
            self.pulse_spawned = True

        if self.frame_index >= len(anim):
            if self.status == 'death':
                self.frame_index = len(anim) - 1
            elif self.status in ('idle', 'walk', 'run'):
                # 循环动画：不重置冷却，状态由 update() 决定何时切换
                self.frame_index = 0
            else:
                # 一次性动作 (attack / pulse / dash / hit) 播完
                ended = self.status
                # ← 只有真正发动攻击才进冷却；受击不算
                if ended in ('attack', 'pulse', 'dash'):
                    self.last_attack_end = pygame.time.get_ticks()
                self.status = 'idle'
                self.frame_index = 0
                self.has_hit_player = False
                if self.rect.bottom > GROUND_Y:
                    self.rect.bottom = GROUND_Y
                if ended == 'pulse':
                    # 脉冲动作播完 + 脉冲飞行 + 0.5 秒额外硬直
                    self.pulse_recover_until = (
                        pygame.time.get_ticks() + 800 + BOSS_PULSE_RECOVER
                    )

        idx = min(int(self.frame_index), len(anim) - 1)
        self.image = pygame.transform.flip(anim[idx], self.flip, False)

    # ----------------------------------------------------------
    # 攻击判定盒（普通攻击专用；脉冲/冲刺各自处理）
    # ----------------------------------------------------------
    def get_attack_hitbox(self):
        """普通攻击中段才返回判定盒。"""
        if self.status == 'attack' and 2 <= int(self.frame_index) <= 4:
            w = 57 * self.scale   # 285
            h = 31 * self.scale   # 155
            if self.flip:
                x = self.rect.left - w
            else:
                x = self.rect.right
            y = self.rect.centery - h // 2
            return pygame.Rect(x, y, w, h)
        return None

    # ----------------------------------------------------------
    # 渲染
    # ----------------------------------------------------------
    def draw(self, surface):
        foot_offset = 180   # 正数往下移；你调到脚刚好贴地为止
        draw_x = self.rect.centerx - (self.size * self.scale) // 2
        draw_y = self.rect.bottom - (self.size * self.scale) + foot_offset
        surface.blit(self.image, (draw_x, draw_y))

    # ----------------------------------------------------------
    # 受伤
    # ----------------------------------------------------------
    def take_damage(self, dmg):
        if self.status in ('death', 'hit'):
            return
        self.hp -= dmg
        if self.hp <= 0:
            self.hp = 0
            self.status = 'death'
        else:
            self.status = 'hit'
        self.frame_index = 0
        self.has_hit_player = False
