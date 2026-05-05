import pygame
import os
import time
from boss import Boss
from player import Player
from settings import WIDTH, HEIGHT, FPS, GROUND_Y

ANIMATION_INTERVAL = 0.2


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DR. WALLSTREET")
clock = pygame.time.Clock()


player = Player(200, 400)
boss = Boss(1000, 400, player)   # y is just to take the place

pulse_group = pygame.sprite.Group()


def load_bg():
    img_path = os.path.join("image", "bg", "fight.png")
    try:
        sheet = pygame.image.load(img_path).convert()
        frames = []
        for i in range(12):
            rect = pygame.Rect(i * 320, 0, 320, 180)
            frame = sheet.subsurface(rect)
            frames.append(pygame.transform.scale(frame, (WIDTH, HEIGHT)))
        return frames
    except Exception:
        print("failed")
        return [pygame.Surface((WIDTH, HEIGHT))] * 12


bg_frames = load_bg()

try:
    heart_full = pygame.image.load(
        os.path.join("image", "other", "heart.png")).convert_alpha()
    heart_empty = pygame.image.load(
        os.path.join("image", "other", "heart_empty.png")).convert_alpha()
except pygame.error as e:
    print(f"UI failed: {e}")
    heart_full = pygame.Surface((80, 80)); heart_full.fill((255, 0, 0))
    heart_empty = pygame.Surface((80, 80)); heart_empty.fill((50, 50, 50))

heart_full = pygame.transform.scale(heart_full, (80, 80))
heart_empty = pygame.transform.scale(heart_empty, (80, 80))


def draw_ui(screen, hp, boss):
    # player's hp
    for i in range(7):
        img = heart_full if i < hp else heart_empty
        screen.blit(img, (30 + i * 90, 30))

    # boss hp
    bar_w = 600
    bar_h = 20
    bar_x = (WIDTH - bar_w) // 2
    bar_y = HEIGHT - 50
    pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
    if boss.hp > 0:
        ratio = boss.hp / boss.max_hp
        pygame.draw.rect(screen, (200, 30, 30),
                         (bar_x, bar_y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(screen, (255, 255, 255),
                     (bar_x, bar_y, bar_w, bar_h), 2)


# main loop
running = True
while running:
    # A. 事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    
    player.update()
    boss.update(pulse_group)
    pulse_group.update()

    # rect_hit
    # player -> boss
    player.check_hit_boss(boss)

    # boss attach/collide
    if boss.status != 'death' and player.rect.colliderect(boss.rect):
        player.take_damage()

    # boss attack
    atk_rect = boss.get_attack_hitbox()
    if atk_rect and player.rect.colliderect(atk_rect):
        player.take_damage()

    # pulse
    for pulse in pulse_group:
        if getattr(pulse, 'is_dangerous', True) and \
                player.rect.colliderect(pulse.rect):
            player.take_damage()
            break
# draw sth
    # bg
    current_time = time.time()
    bg_idx = (int(current_time / ANIMATION_INTERVAL)) % 12
    screen.blit(bg_frames[bg_idx], (0, 0))

    # boss
    boss.draw(screen)

  # pulse
    for pulse in pulse_group:
        img_rect = pulse.image.get_rect(center=pulse.rect.center)
        screen.blit(pulse.image, img_rect)

    # player
    player.draw(screen)

    # UI
    draw_ui(screen, player.hp, boss)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
