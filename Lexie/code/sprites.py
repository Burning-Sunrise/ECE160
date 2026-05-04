import pygame
import random
from settings import *


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups, ground=False):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.ground = ground



class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)


class Gun(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        self.player = player
        self.image = pygame.image.load(join( "images", 'Player', "regularpisto.png")).convert_alpha()
        self.original_image = self.image
        self.rect = self.image.get_rect(center=player.rect.center)
        self.player_direction = pygame.Vector2(1, 0)

    def update(self, dt):
        self.rect.center = self.player.rect.center
        mouse_pos = pygame.mouse.get_pos()
        direction = pygame.Vector2(mouse_pos) - pygame.Vector2(self.rect.center)
        if direction.length() > 0:
            self.player_direction = direction.normalize()
            angle = -self.player_direction.angle_to(pygame.Vector2(1, 0))
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center=pos)
        self.direction = direction
        self.speed = 600

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if not pygame.display.get_surface().get_rect().collidepoint(self.rect.center):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, player, collision_sprites):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

        self.player = player
        self.collision_sprites = collision_sprites

        self.mode = "npc"
        self.speed = 100
        self.aggressive_speed = 200

        self.wander_timer = 0
        self.wander_dir = pygame.Vector2(0, 0)



    def set_mode(self, mode):
        self.mode = mode

    def has_line_of_sight(self, player, collision_sprites):
        # same row
        if abs(self.rect.centery - player.rect.centery) < 10:
            step = 1 if player.rect.centerx > self.rect.centerx else -1
            for x in range(self.rect.centerx, player.rect.centerx, step * 5):
                test_rect = pygame.Rect(x, self.rect.centery, 5, 5)
                for wall in collision_sprites:
                    if wall.rect.colliderect(test_rect):
                        return False
            return True

        # same column
        if abs(self.rect.centerx - player.rect.centerx) < 10:
            step = 1 if player.rect.centery > self.rect.centery else -1
            for y in range(self.rect.centery, player.rect.centery, step * 5):
                test_rect = pygame.Rect(self.rect.centerx, y, 5, 5)
                for wall in collision_sprites:
                    if wall.rect.colliderect(test_rect):
                        return False
            return True

        return False

    def npc_behavior(self, dt):
        self.wander_timer -= dt
        if self.wander_timer <= 0:
            self.wander_timer = 1.2
            if random.random() < 0.7:
                self.wander_dir = pygame.Vector2(
                    random.choice([-1, 0, 1]),
                    random.choice([-1, 0, 1])
                )
                if self.wander_dir.length() > 0:
                    self.wander_dir = self.wander_dir.normalize()
            else:
                self.wander_dir = pygame.Vector2(0, 0)

        move = self.wander_dir * self.speed * dt
        self.rect.centerx += move.x
        self.rect.centery += move.y

    def aggressive_behavior(self, dt):
        direction = pygame.Vector2(
            self.player.rect.centerx - self.rect.centerx,
            self.player.rect.centery - self.rect.centery
        )
        if direction.length() > 0:
            direction = direction.normalize()

        move = direction * self.aggressive_speed * dt
        self.rect.centerx += move.x
        self.rect.centery += move.y

    def update(self, dt):
        if self.mode == "npc":
            self.npc_behavior(dt)
        else:
            self.aggressive_behavior(dt)

        self.frame_index += 6 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def destroy(self):
        self.kill()