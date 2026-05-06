import pygame
from settings import PLAYER_SPEED, SCREEN_WIDTH, SCREEN_HEIGHT

class Player:
    def __init__(self, x, y):
        # Player is a simple square for now
        self.rect = pygame.Rect(x, y, 16, 16)
        self.color = (255, 255, 255)

        # Movement
        self.speed = PLAYER_SPEED
        self.vel_x = 0
        self.vel_y = 0

    def handle_input(self, keys):
        """Reads keyboard input and sets velocity."""
        self.vel_x = 0
        self.vel_y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.vel_y = -self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.vel_y = self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.vel_x = -self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.vel_x = self.speed

    def update(self, walls):
        """Moves the player and keeps them inside the screen."""
       
        #Horizontal Movement
        self.rect.x += self.vel_x
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_x > 0:
                    self.rect.right = wall.left
                elif self.vel_x < 0:
                    self.rect.left = wall.right
        
        #Vertical Movement
        self.rect.y += self.vel_y
        for wall in walls:
            if self.rect.colliderect(wall):
                if self.vel_y > 0:
                    self.rect.bottom = wall.top
                elif self.vel_y < 0:
                    self.rect.top = wall.bottom


        # Keep inside screen bounds
        self.rect.x = max(0, min(self.rect.x, SCREEN_WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, SCREEN_HEIGHT - self.rect.height))

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)