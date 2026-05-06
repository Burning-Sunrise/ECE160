import pygame
from settings import WIDTH


class Pulse(pygame.sprite.Sprite):



    SPEED = 15
    ANIM_SPEED = 0.07

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
    
        super().__init__()
        self.frames = frames
        self.flip = flip
        self.frame_index = 0

        self.speed = -self.SPEED if flip else self.SPEED

       
        self.image = pygame.transform.flip(self.frames[0], flip, False)
        w, h = self.HITBOXES[0]
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)

        self.is_dangerous = True

    def update(self):

        self.rect.x += self.speed

        self.frame_index += self.ANIM_SPEED
        if self.frame_index >= len(self.frames):
            self.kill()
            return

        idx = int(self.frame_index)


        self.image = pygame.transform.flip(self.frames[idx], self.flip, False)


        hb = self.HITBOXES[idx]
        if hb is None:
            self.is_dangerous = False
            center = self.rect.center
            self.rect = pygame.Rect(0, 0, 1, 1)
            self.rect.center = center
        else:
            center = self.rect.center
            self.rect = pygame.Rect(0, 0, hb[0], hb[1])
            self.rect.center = center


        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
