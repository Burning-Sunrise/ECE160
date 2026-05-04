import pygame
import sys

from Sidney.src.ui_manager import UIManager
from game.game_state import GameState
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN, COLOR_BG, FPS

# Internal fixed resolution
GAME_WIDTH = 640
GAME_HEIGHT = 360


def main():
    pygame.init()

    # Window setup
    if FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Dr. Wallstreet")
    clock = pygame.time.Clock()

    # Internal game surface (for pixel scaling)
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))

    # Temporary font
    font = pygame.font.SysFont("Arial", 20)

    # Core systems
    game_state = GameState()
    ui = UIManager(game_surface, font)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        # -------------------------
        # EVENT HANDLING
        # -------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            ui.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

        # -------------------------
        # UPDATE
        # -------------------------
        ui.update(dt, game_state)

        # -------------------------
        # DRAW TO INTERNAL SURFACE
        # -------------------------
        game_surface.fill(COLOR_BG)
        ui.draw(game_surface)

        # -------------------------
        # SCALE TO WINDOW
        # -------------------------
        scaled = pygame.transform.scale(game_surface, screen.get_size())
        screen.blit(scaled, (0, 0))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

## Saving all files is Ctrl + K  then S
##Personally, when wanting to run code,type "python3 src\main.py" into the terminal to run

### Major edit, making the interactables and the walls all modular for future customizable use 4/20/26