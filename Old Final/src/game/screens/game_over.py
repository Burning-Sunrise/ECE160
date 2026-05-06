#game over, will add other screens etc
class GameOverScreen:
    def __init__(self):
        self.ui = None

    def handle_event(self, event):
        pass

    def update(self, dt, game_state):
        pass

    def draw(self, surface):
        surface.fill((0, 0, 40))  # dark blue placeholder