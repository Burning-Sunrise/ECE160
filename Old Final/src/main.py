import pygame
import sys

from game.ui_manager import UIManager
from game.game_state import GameState
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FULLSCREEN, COLOR_BG, FPS,
    GAME_WIDTH, GAME_HEIGHT, NIGHTMARE_WIDTH, NIGHTMARE_HEIGHT,
)


def main():
    pygame.init()

    # Window setup
    if FULLSCREEN:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    pygame.display.set_caption("Dr. Wallstreet")
    clock = pygame.time.Clock()

    # Internal surfaces
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))                # 640x360 normal screens
    nightmare_surface = pygame.Surface((NIGHTMARE_WIDTH, NIGHTMARE_HEIGHT)) # 1280x720 boss fight

    # Temporary font
    font = pygame.font.SysFont("Arial", 20)

    # Core systems
    game_state = GameState()
    ui = UIManager(game_surface, font)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        # EVENT HANDLING
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            ui.handle_event(event)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

        # UPDATE
        ui.update(dt, game_state)

        # DRAW: pick surface based on current screen
        if ui.current_screen == "NIGHTMARE":
            nightmare_surface.fill(COLOR_BG)
            ui.draw(nightmare_surface)
            scaled = pygame.transform.scale(nightmare_surface, screen.get_size())
        else:
            game_surface.fill(COLOR_BG)
            ui.draw(game_surface)
            scaled = pygame.transform.scale(game_surface, screen.get_size())

        screen.blit(scaled, (0, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()