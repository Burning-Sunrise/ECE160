import pygame
import sys

# --- 核心配置 ---
# 根据你提供的信息
FRAME_WIDTH = 150
FRAME_HEIGHT = 150
TOTAL_FRAMES = 7  # 实际有效的动作帧数
SHEET_COLS = 3    # 精灵图是 3列 x 3行 的矩阵
SHEET_ROWS = 3

# 动画控制
FPS = 10          # 帧率（每秒播放多少帧），像素动画通常 8-12 比较合适
SCALE_FACTOR = 5 # 放大倍数，原图 150x150 有点小，放大 2 倍看更清楚

# 窗口设置
SCREEN_SIZE = (1280, 720)  # 换成这个，视野更开阔
BG_COLOR = (50, 50, 50)  # 深灰色背景，能看清白色和黑色元素

# --- 初始化 Pygame ---
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption("扇子攻击动画演示")
clock = pygame.time.Clock()

def load_animation_frames():
    """核心函数：从 3x3 矩阵中抠取 7 个有效帧"""
    try:
        # 加载原图，使用 convert_alpha() 保证透明度
        sheet = pygame.image.load("boss_attack_air.png").convert_alpha()
    except FileNotFoundError:
        print("错误：找不到 'fan_attack_sheet.png' 文件。")
        print("请确保图片与脚本在同一文件夹，且文件名正确。")
        pygame.quit()
        sys.exit()

    frames = []
    # 遍历矩阵，直到取满 7 帧
    frame_count = 0
    for row in range(SHEET_ROWS):
        for col in range(SHEET_COLS):
            if frame_count >= TOTAL_FRAMES:
                break # 已经取够 7 帧，停止
            
            # 1. 计算当前帧在原图上的像素矩形区域
            x = col * FRAME_WIDTH
            y = row * FRAME_HEIGHT
            rect = pygame.Rect(x, y, FRAME_WIDTH, FRAME_HEIGHT)
            
            # 2. 抠取图像
            frame = sheet.subsurface(rect)
            
            # 3. 放大图像（可选，为了看得更清楚）
            if SCALE_FACTOR != 1:
                new_size = (FRAME_WIDTH * SCALE_FACTOR, FRAME_HEIGHT * SCALE_FACTOR)
                frame = pygame.transform.scale(frame, new_size)
                
            frames.append(frame)
            frame_count += 1
            
    return frames

# --- 主程序逻辑 ---

# 1. 加载并切分所有帧
animation_frames = load_animation_frames()
current_frame_index = 0

# 2. 计算人物显示时的中心位置
if SCALE_FACTOR != 1:
    final_width = FRAME_WIDTH * SCALE_FACTOR
    final_height = FRAME_HEIGHT * SCALE_FACTOR
else:
    final_width = FRAME_WIDTH
    final_height = FRAME_HEIGHT

target_pos = (SCREEN_SIZE[0] // 2 - final_width // 2, 
              SCREEN_SIZE[1] // 2 - final_height // 2)

# --- 游戏主循环 ---
running = True
while running:
    # 1. 事件处理
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # 2. 更新：自动轮播帧索引
    current_frame_index += 1
    if current_frame_index >= TOTAL_FRAMES:
        current_frame_index = 0

   # --- 绘制 ---
    screen.fill(BG_COLOR)  # 清屏
    
    # 1. 计算位置（让 Boss 站在地平线上，而不是飘在空中）
    draw_x = SCREEN_SIZE[0] // 2 - (FRAME_WIDTH * SCALE_FACTOR) // 2
    ground_y = SCREEN_SIZE[1] - 100 # 距离底部 100 像素作为地面
    draw_y = ground_y - (FRAME_HEIGHT * SCALE_FACTOR) 

    # 2. 绘制当前帧
    screen.blit(animation_frames[current_frame_index], (draw_x, draw_y))

    # 4. 刷新屏幕并控制帧率
    pygame.display.flip()
    clock.tick(FPS)  # 这里的 FPS 直接控制动画播放速度

pygame.quit()
sys.exit()