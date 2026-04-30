import pygame
from settings import WIDTH


class Pulse(pygame.sprite.Sprite):
    """
    Boss 的脉冲攻击。
    8 帧 spritesheet：前 5 帧有不同尺寸的碰撞箱，后 3 帧是消失动画无碰撞。
    """

    # 飞行速度（像素/帧）
    SPEED = 15
    ANIM_SPEED = 0.07

    # 每帧的碰撞箱（屏幕显示尺寸，单位：像素）
    # 第六、七帧 = None 代表消失动画，无伤害
    HITBOXES = [
        (25 , 25 ),
        (169 , 8 ),
        (210 , 8 ),
        (183 , 8 ),
        (143 , 8 ),
        None,
        None,
        None,
    ]

    def __init__(self, x, y, flip, frames):
        """
        x, y: 生成位置（脉冲中心点）
        flip: True 表示往左飞、向左翻转图像；False 表示往右
        frames: 已经按 2x 缩放好的 8 张 Surface
        """
        super().__init__()
        self.frames = frames
        self.flip = flip
        self.frame_index = 0

        # 横向速度
        self.speed = -self.SPEED if flip else self.SPEED

        # 初始图像 + 碰撞箱
        self.image = pygame.transform.flip(self.frames[0], flip, False)
        w, h = self.HITBOXES[0]
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)

        # 是否还能造成伤害（消失动画期间为 False）
        self.is_dangerous = True

    def update(self):
        # 1. 横向移动
        self.rect.x += self.speed

        # 2. 推进动画
        self.frame_index += self.ANIM_SPEED
        if self.frame_index >= len(self.frames):
            self.kill()
            return

        idx = int(self.frame_index)

        # 3. 更新图像
        self.image = pygame.transform.flip(self.frames[idx], self.flip, False)

        # 4. 更新碰撞箱
        hb = self.HITBOXES[idx]
        if hb is None:
            # 消失动画：无伤害，rect 退化为 1x1
            self.is_dangerous = False
            center = self.rect.center
            self.rect = pygame.Rect(0, 0, 1, 1)
            self.rect.center = center
        else:
            center = self.rect.center
            self.rect = pygame.Rect(0, 0, hb[0], hb[1])
            self.rect.center = center

        # 5. 飞出屏幕就消失
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
