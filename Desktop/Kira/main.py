import pygame
import os
import time
from boss import Boss
from player import Player
from settings import WIDTH, HEIGHT, FPS, GROUND_Y

ANIMATION_INTERVAL = 0.2

# --- 初始化 ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DR. WALLSTREET")
clock = pygame.time.Clock()

# --- 实例化 ---
player = Player(200, 400)
boss = Boss(1000, 400, player)   # y 仅作占位，Boss 内部会强制贴地

pulse_group = pygame.sprite.Group()


# --- 资源 ---
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
        print("背景图加载失败")
        return [pygame.Surface((WIDTH, HEIGHT))] * 12


bg_frames = load_bg()

try:
    heart_full = pygame.image.load(
        os.path.join("image", "other", "heart.png")).convert_alpha()
    heart_empty = pygame.image.load(
        os.path.join("image", "other", "heart_empty.png")).convert_alpha()
except pygame.error as e:
    print(f"UI资源加载失败: {e}")
    heart_full = pygame.Surface((80, 80)); heart_full.fill((255, 0, 0))
    heart_empty = pygame.Surface((80, 80)); heart_empty.fill((50, 50, 50))

heart_full = pygame.transform.scale(heart_full, (80, 80))
heart_empty = pygame.transform.scale(heart_empty, (80, 80))


def draw_ui(screen, hp, boss):
    # 玩家血量（爱心）
    for i in range(7):
        img = heart_full if i < hp else heart_empty
        screen.blit(img, (30 + i * 90, 30))

    # boss 血条
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


# --- 主循环 ---
running = True
while running:
    # A. 事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    # B. 逻辑更新
    player.update()
    boss.update(pulse_group)
    pulse_group.update()

    # C. 碰撞检测
    # 1) 玩家攻击 -> boss
    player.check_hit_boss(boss)

    # 2) boss 身体接触 -> 玩家扣血
    if boss.status != 'death' and player.rect.colliderect(boss.rect):
        player.take_damage()

    # 3) boss 普通攻击 -> 玩家扣血
    atk_rect = boss.get_attack_hitbox()
    if atk_rect and player.rect.colliderect(atk_rect):
        player.take_damage()

    # 4) 脉冲 -> 玩家扣血
    for pulse in pulse_group:
        if getattr(pulse, 'is_dangerous', True) and \
                player.rect.colliderect(pulse.rect):
            player.take_damage()
            break

    # D. 绘制
    # 1) 背景
    current_time = time.time()
    bg_idx = (int(current_time / ANIMATION_INTERVAL)) % 12
    screen.blit(bg_frames[bg_idx], (0, 0))

    # 2) Boss
    boss.draw(screen)

  # 3) 脉冲
    for pulse in pulse_group:
        img_rect = pulse.image.get_rect(center=pulse.rect.center)
        screen.blit(pulse.image, img_rect)

    # 4) 玩家
    player.draw(screen)

    # 5) UI
    draw_ui(screen, player.hp, boss)

    # --- 调试用：把碰撞箱画出来，确认无误后可注释掉 ---
    # pygame.draw.rect(screen, (255, 0, 0), boss.rect, 2)
    # pygame.draw.rect(screen, (0, 255, 0), player.rect, 2)
    # if atk_rect:
    #     pygame.draw.rect(screen, (255, 165, 0), atk_rect, 2)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
