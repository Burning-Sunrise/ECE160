import pygame
from game.interaction_zone import InteractionZone
from game.player import Player
from settings import GAME_WIDTH, GAME_HEIGHT

# ------------------------------------
# Debug Toggles
# ------------------------------------
DEBUG_WALLS = False       # Show wall rectangles if true
DEBUG_ZONES = True       # Show interaction zones (otherwise unplayable as user wouldn't know where to interact KEEP TRUE)


class TradingFloorScreen:
    def __init__(self):
        self.ui = None
        self.player = Player(250, 150)

        self.walls = []
        self.interaction_zones = []
        self.current_interaction = None

        # Background image
        self.background = pygame.transform.scale(
            pygame.image.load("assets/trading_floor/trading_floor.jpg").convert(),
            (640, 360)
        )

        self._build_test_room()

    # ------------------------------------
    # Helper functions
    # ------------------------------------
    def add_wall(self, x, y, w, h):
        self.walls.append(pygame.Rect(x, y, w, h))

    def add_interaction_zone(self, x, y, w, h, zone_type, data=None):
        self.interaction_zones.append(
            InteractionZone(x, y, w, h, zone_type, data)
        )

    # ------------------------------------
    # Build the room ****** IMPORTANT WALL LAYOUTS ARE HERE
    # ------------------------------------
    def _build_outer_walls(self):
        thickness = 20
        w, h = GAME_WIDTH, GAME_HEIGHT

        self.add_wall(0, 0, w, thickness)              # Top
        self.add_wall(0, h - thickness, w, thickness)  # Bottom
        self.add_wall(0, 0, thickness, h)              # Left
        self.add_wall(w - thickness, 0, thickness, h)  # Right

    def _build_inner_walls(self):
        #tippy top Flag? obstruct entrance to background

        self.add_wall(0, 40, 1000, 20)
        
        # Top row, walls
        
        self.add_wall(245, 85, 150, 20)
        self.add_wall(75, 85, 130, 20)
        self.add_wall(437, 85, 140, 20)

        #2nd row, walls
        self.add_wall(245, 110, 150, 40)
        self.add_wall(75, 110, 130, 40)
        self.add_wall(437, 110, 140, 40)

        #Vertical Walls
        self.add_wall(55, 155, 20, 90)
        self.add_wall(110, 155, 20, 90)
        self.add_wall(520, 155, 20, 90)
        self.add_wall(570, 155, 20, 90)

        #4th row Walls
        self.add_wall(55, 250, 128, 30)
        self.add_wall(237, 250, 123, 30)
        self.add_wall(415, 250, 140, 30)

        #Bottom Row Walls
        self.add_wall(45, 280, 150, 100)
        self.add_wall(226, 280, 150, 100)
        self.add_wall(406, 280, 156, 100)

    def _build_interaction_zones(self):
        # interactions on 3 benches
        self.add_interaction_zone(75, 110, 132, 45, "terminal")
        self.add_interaction_zone(240, 110, 160, 45, "terminal")
        self.add_interaction_zone(434, 110, 160, 45, "terminal")

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

        # Player movement + collision
        self.player.handle_input(keys)
        self.player.update(self.walls)

        # Interaction detection
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

        # Background
        surface.blit(self.background, (0, 0))

        # Walls (debug only)
        if DEBUG_WALLS:
            for wall in self.walls:
                pygame.draw.rect(surface, (100, 100, 100), wall, 2)

        # Interaction zones (debug only)
        if DEBUG_ZONES:
            for zone in self.interaction_zones:
                pygame.draw.rect(surface, (0, 150, 255), zone.rect, 2)

        # Player
        self.player.draw(surface)

    # ------------------------------------
    # Interaction logic
    # ------------------------------------
    def _trigger_interaction(self, zone):
        if not self.ui:
            return

        self.ui.clear_prompt()

        if zone.type == "terminal":
            self.ui.state = "CONFIRM_TRADE"
