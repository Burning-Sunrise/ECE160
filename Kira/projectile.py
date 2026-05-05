import pygame
from settings import WIDTH


class Pulse(pygame.sprite.Sprite):
    """
    the last 3 frames have no hitbox
    """

    SPEED = 15#[pixel]
    ANIM_SPEED = 0.07#[frame]

    
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
        x, y: pos
        flip:False:right
        frames: after resize 2x
        """
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
        # position change
        self.rect.x += self.speed

        # animation for pulse moving
        self.frame_index += self.ANIM_SPEED
        if self.frame_index >= len(self.frames):
            self.kill()
            return

        idx = int(self.frame_index)# if use frame_index += 1 here, the animation will be insanely fast—it’s twitching like a ghost

        # update image
        self.image = pygame.transform.flip(self.frames[idx], self.flip, False)

        # update hitbox
        hb = self.HITBOXES[idx]
        if hb is None:
            # disappearing
            self.is_dangerous = False
            center = self.rect.center
            self.rect = pygame.Rect(0, 0, 1, 1)
            self.rect.center = center
        else:
            center = self.rect.center
            self.rect = pygame.Rect(0, 0, hb[0], hb[1])
            self.rect.center = center

        # when outside of the screen
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
