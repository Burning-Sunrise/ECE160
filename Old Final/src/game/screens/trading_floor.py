import pygame
from game.interaction_zone import InteractionZone
from game.player import Player
from settings import GAME_WIDTH, GAME_HEIGHT

DEBUG = True


class TradingFloorScreen:
    def __init__(self):
        self.ui = None  # UIManager will assign this later
        self.player = Player(200, 200)

        self.walls = []
        self.interaction_zones = []
        self.current_interaction = None

        self._build_test_room()

    # ------------------------------------
    # Modular helper functions
    # ------------------------------------
    def add_wall(self, x, y, w, h):
        self.walls.append(pygame.Rect(x, y, w, h))

    def add_interaction_zone(self, x, y, w, h, zone_type, data=None):
        self.interaction_zones.append(
            InteractionZone(x, y, w, h, zone_type, data)
        )

    # ------------------------------------
    # Build the room
    # ------------------------------------
    def _build_outer_walls(self):
        thickness = 20
        w, h = GAME_WIDTH, GAME_HEIGHT

        self.add_wall(0, 0, w, thickness)
        self.add_wall(0, h - thickness, w, thickness)
        self.add_wall(0, 0, thickness, h)
        self.add_wall(w - thickness, 0, thickness, h)

    def _build_inner_walls(self):
        self.add_wall(200, 200, 400, 20)
        self.add_wall(100, 100, 200, 20)

    def _build_interaction_zones(self):
        self.add_interaction_zone(150, 150, 40, 40, "terminal")

    def _build_test_room(self):
        self._build_outer_walls()
        self._build_inner_walls()
        self._build_interaction_zones()

    # ------------------------------------
    # Event Handling
    # ------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e and self.current_interaction:
                self._trigger_interaction(self.current_interaction)

    # ------------------------------------
    # Update
    # ------------------------------------
    def update(self, dt, game_state):
        keys = pygame.key.get_pressed()

        #Player movement
        self.player.handle_input(keys)
        self.player.update(self.walls)

        # ------------------------------------
        # NEW DAY FIX
        # ------------------------------------
        # If trades reset, clear interaction state + prompt
        if game_state.trades_today == 0:
            self.current_interaction = None
            if self.ui:
                self.ui.clear_prompt()

        # ------------------------------------
        # Interaction detection
        # ------------------------------------
        self.current_interaction = None
        for zone in self.interaction_zones:
            if self.player.rect.colliderect(zone.rect):
                self.current_interaction = zone
                if self.ui:
                    self.ui.show_prompt_at(
                        "Press E to interact",
                        zone.rect.centerx,
                        zone.rect.top - 20
                    )
                break

        if self.current_interaction is None and self.ui:
            self.ui.clear_prompt()

    # ------------------------------------
    # Draw
    # ------------------------------------
    def draw(self, surface):
        # Draw walls
        for wall in self.walls:
            pygame.draw.rect(surface, (100, 100, 100), wall)

        # Draw interaction zones (debug)
        if DEBUG:
            for zone in self.interaction_zones:
                pygame.draw.rect(surface, (0, 150, 255), zone.rect, 2)

        # Draw player
        self.player.draw(surface)

    # ------------------------------------
    # Interaction logic
    # ------------------------------------
    def _trigger_interaction(self, zone):
        if not self.ui:
            return

        # Clear the "Press E" prompt immediately
        self.ui.clear_prompt()

        if zone.type == "terminal":
            self.ui.state = "CONFIRM_TRADE"

