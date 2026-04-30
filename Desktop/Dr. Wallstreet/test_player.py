import pygame
import sys

# --- 核心配置 ---
FRAME_WIDTH = 64
FRAME_HEIGHT = 64
TOTAL_FRAMES = 8
# 确保这个路径和你文件夹里的实际情况一致
IMAGE_PATH = "player.png" 

# 动画控制
FPS = 12          
SCALE_FACTOR = 5  # 主角放大 5 倍后是 320x320 像素

# 窗口设置
SCREEN_SIZE = (1280, 720)
BG_COLOR = (50, 50, 50)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("主角动画测试")
clock = pygame.time.Clock()

def load_hero_frames():
    try:
        # 这里统一使用上面定义的 IMAGE_PATH 变量
        sheet = pygame.image.load(IMAGE_PATH).convert_alpha()
    except FileNotFoundError:
        print(f"错误：找不到文件 {IMAGE_PATH}")
        pygame.quit()
        sys.exit()

    frames = []
    for i in range(TOTAL_FRAMES):
        rect = pygame.Rect(i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT)
        frame = sheet.subsurface(rect)
        
        if SCALE_FACTOR != 1:
            frame = pygame.transform.scale(frame, (FRAME_WIDTH * SCALE_FACTOR, FRAME_HEIGHT * SCALE_FACTOR))
        frames.append(frame)
    return frames

# --- 主程序 ---
hero_frames = load_hero_frames()
current_frame = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 更新帧索引
    current_frame = (current_frame + 1) % TOTAL_FRAMES

    # --- 绘制 ---
    screen.fill(BG_COLOR)
    
    # 1. 计算位置
    # 水平居中
    draw_x = SCREEN_SIZE[0] // 2 - (FRAME_WIDTH * SCALE_FACTOR) // 2
    # 站在地平线上
    ground_y = SCREEN_SIZE[1] - 100 
    draw_y = ground_y - (FRAME_HEIGHT * SCALE_FACTOR) 

    # 2. 绘制当前帧（注意这里变量名改成了 hero_frames 和 current_frame）
    screen.blit(hero_frames[current_frame], (draw_x, draw_y))

    pygame.display.flip()
    clock.tick(FPS)