import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
import pygame
import random
from settings import (
    WIDTH, GROUND_Y, HEIGHT, 
    BOSS_WALK_SPEED, BOSS_RUN_SPEED, BOSS_DASH_SPEED,
    BOSS_ATTACK_RANGE, BOSS_ATTACK_COOLDOWN,
    BOSS_PULSE_RECOVER, BOSS_INTRO_DELAY,
)
from game.projectile import Pulse


class Boss(pygame.sprite.Sprite):


    def __init__(self, x, y, player):
        print("Boss init")
        super().__init__()
        self.player = player#(we need to use the player's location)
        self.scale = 5
        self.size = 150  # the size for the initial frame (150x150)

        #---stats---
        self.hp = 10
        self.max_hp = 10
        self.is_invincible = False  
        self.has_hit_player = False  


        self.status = 'idle'
        self.flip = True  
        self.start_time = pygame.time.get_ticks()
        self.last_attack_end = 0
        self.pulse_spawned = False 
        self.pulse_recover_until = 0  


        self.frame_index = 0
        self.animations = self.load_assets()
        self.pulse_frames = self.load_pulse_assets()


        self.image = self.animations['idle'][0]
        self.rect = pygame.Rect(0, 0, 16 * self.scale, 54 * self.scale)
        self.rect.centerx = x
        self.rect.bottom = GROUND_Y  


    def load_assets(self):

        asset_info = {
            'idle':   (os.path.join(ASSETS_DIR, "boss/boss_idle/boss_idle.png"), 17, 6),
            'walk':   (os.path.join(ASSETS_DIR, "boss/boss_walk/boss_walk.png"), 12, 12),
            'run':    (os.path.join(ASSETS_DIR, "boss/boss_run/boss_run.png"), 6, 6),
            'attack': (os.path.join(ASSETS_DIR, "boss/boss_attack_air/boss_attack_air.png"), 7, 3),
            'pulse':  (os.path.join(ASSETS_DIR, "boss/boss_attack_pulse/boss_attack_pulse.png"), 5, 5),
            'dash':   (os.path.join(ASSETS_DIR, "boss/boss_attack_dash/boss_attack_dash.png"), 11, 11),
            'hit':    (os.path.join(ASSETS_DIR, "boss/boss_hit/boss_hit.png"), 3, 3),
            'death':  (os.path.join(ASSETS_DIR, "boss/boss_death/boss_death.png"), 19, 3),
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
                print(f"cannot find: {path}，error: {e}")
                all_anims[action] = [
                    pygame.Surface((self.size * self.scale, self.size * self.scale))
                ]
        return all_anims

    def load_pulse_assets(self):
        path = os.path.join(ASSETS_DIR, "boss/effects/pulse.png")
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
            print(f"cannot find pulse png: {path}，error: {e}")
            return [pygame.Surface((256 ,
                                    128 )) for _ in range(8)]


    def update(self, pulse_group):
        print("Boss update")
        if self.status == 'death':
            self.animate(pulse_group)
            return

        now = pygame.time.get_ticks()

  
        if now - self.start_time < BOSS_INTRO_DELAY:
            self.status = 'idle'
            self.flip = self.player.rect.centerx < self.rect.centerx
            self.animate(pulse_group)
            return

        if self.status == 'hit':
            self.animate(pulse_group)
            return


        if self.status == 'idle':
            self.flip = self.player.rect.centerx < self.rect.centerx
          
            if now - self.last_attack_end > BOSS_ATTACK_COOLDOWN \
                    and now > self.pulse_recover_until:
                self.decide_attack()

        elif self.status == 'run':
            self._chase(BOSS_RUN_SPEED)

        elif self.status == 'walk':
            self._chase(BOSS_WALK_SPEED)

        elif self.status == 'dash':

            self.rect.y += BOSS_DASH_SPEED
            if self.rect.bottom >= HEIGHT - 80:
                self.rect.bottom = HEIGHT - 80

  

        self.animate(pulse_group)

    def _chase(self, speed):
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

    def decide_attack(self):
        choice = random.choice(['normal', 'pulse', 'dash'])
        self.frame_index = 0
        self.has_hit_player = False

        if choice == 'normal':
            dist = abs(self.player.rect.centerx - self.rect.centerx)
            self.flip = self.player.rect.centerx < self.rect.centerx
            if dist > BOSS_ATTACK_RANGE:
                self.status = 'run'
            else:
                self.status = 'attack'

        elif choice == 'pulse':
            if self.player.rect.centerx < WIDTH // 2:
                self.rect.right = WIDTH - 50
                self.flip = True  
            else:
                self.rect.left = 50
                self.flip = False 
            self.rect.bottom = GROUND_Y
            self.status = 'pulse'
            self.pulse_spawned = False

        elif choice == 'dash':
            self.rect.centerx = self.player.rect.centerx
            self.rect.bottom = -20
            self.flip = self.player.rect.centerx < self.rect.centerx
            self.status = 'dash'


    def animate(self, pulse_group):
        anim = self.animations[self.status]
        if self.status in ('attack', 'pulse', 'dash'):
            self.frame_index += 0.1 
        else:
            self.frame_index += 0.2

  
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
                self.frame_index = 0
            else:
                ended = self.status
                if ended in ('attack', 'pulse', 'dash'):
                    self.last_attack_end = pygame.time.get_ticks()
                self.status = 'idle'
                self.frame_index = 0
                self.has_hit_player = False
                if self.rect.bottom > GROUND_Y:
                    self.rect.bottom = GROUND_Y
                if ended == 'pulse':
                    self.pulse_recover_until = (
                        pygame.time.get_ticks() + 800 + BOSS_PULSE_RECOVER
                    )

        idx = min(int(self.frame_index), len(anim) - 1)
        self.image = pygame.transform.flip(anim[idx], self.flip, False)


    def get_attack_hitbox(self):
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

    def draw(self, surface):
        foot_offset = 180 
        draw_x = self.rect.centerx - (self.size * self.scale) // 2
        draw_y = self.rect.bottom - (self.size * self.scale) + foot_offset
        surface.blit(self.image, (draw_x, draw_y))


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
