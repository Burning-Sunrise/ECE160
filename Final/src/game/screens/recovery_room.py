#Kira is doing the art and design for this one... I'm taking care of the logic
# recovery_room.py
import pygame
import os
from settings import GAME_WIDTH, GAME_HEIGHT

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
ASSET_DIR = os.path.join(BASE_DIR, "assets")


class RecoveryRoomScreen:
    def __init__(self):
        self.ui = None
        self.timer = 0
        self.phase = "ENTER"
        self.choice = None
        self.applied_result = False

        # Load art
        self.doctor_open = pygame.image.load(
            os.path.join(ASSET_DIR, "pharmacy", "pharmacist_begin.png")
        ).convert_alpha()

        self.doctor_closed = pygame.image.load(
            os.path.join(ASSET_DIR, "pharmacy", "pharmacist_end.png")
        ).convert_alpha()

        # Scale to internal resolution
        self.doctor_open = pygame.transform.scale(self.doctor_open, (GAME_WIDTH, GAME_HEIGHT))
        self.doctor_closed = pygame.transform.scale(self.doctor_closed, (GAME_WIDTH, GAME_HEIGHT))

        # Fade
        self.fade_alpha = 0
        self.fade_speed = 200

        self.result_text = ""
        self.outcome = None
        self.entered = False

    def _reset(self):

        self.timer = 0
        self.phase = "ENTER"
        self.choice = None
        self.applied_result = False
        self.fade_alpha = 0
        self.result_text = ""
        self.outcome = None

    # ----------------------------------------
    # Input
    # ----------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if self.phase == "CHOICE":
                if event.key == pygame.K_1:
                    self.choice = "TAKE"
                    self.phase = "RESULT"
                elif event.key == pygame.K_2:
                    self.choice = "SKIP"
                    self.phase = "RESULT"

            elif self.phase == "RESULT":
                if event.key == pygame.K_SPACE:
                    self.phase = "FADE"

    # ----------------------------------------
    # Update
    # ----------------------------------------
    def update(self, dt, game_state):
        #for pharmacy check

        if not self.entered:
            self._reset()
            self.entered = True

        # Reset result application each visit
        if self.phase == "ENTER":
            self.applied_result = False

        # ENTER
        if self.phase == "ENTER":
            self.timer += dt
            if self.timer > 1.0:
                self.phase = "CHOICE"

        # RESULT
        elif self.phase == "RESULT":

            if not self.applied_result:

                if self.choice == "TAKE":
                    game_state.subtract_money(800)
                    game_state.recover_stress(35)
                    self.result_text = "You take the medication and feel calmer."

                elif self.choice == "SKIP":
                    game_state.add_stress(20)
                    self.result_text = "You skip the medication. Stress rises."

                # Determine outcome
                stress = game_state.stress

                if stress >= game_state.max_stress:
                    self.outcome = "DEATH"

                elif stress >= 60:
                    self.outcome = "NIGHTMARE"
                    self.result_text += " You feel awful tonight..."

                else:
                    self.outcome = "PEACEFUL"

                self.applied_result = True

        # FADE
        elif self.phase == "FADE":
            self.fade_alpha += self.fade_speed * dt

            if self.fade_alpha >= 255:
                self.ui.state = None # ensure HUD updates
                self.entered = False  

                if self.outcome == "DEATH":
                    self.ui.change_screen("GAME_OVER")
                elif self.outcome == "NIGHTMARE":
                    self.ui.change_screen("NIGHTMARE")
                else:
                    game_state.advance_day()
                    self.ui.change_screen("TRADING_FLOOR")

    # ----------------------------------------
    # Draw
    # ----------------------------------------
    def draw(self, surface):
        font = pygame.font.SysFont("Arial", 24)

        # Background art
        if self.phase in ("ENTER", "CHOICE"):
            surface.blit(self.doctor_open, (0, 0))
        else:
            surface.blit(self.doctor_closed, (0, 0))

        # Textbox background
        textbox = pygame.Surface((GAME_WIDTH, 80))
        textbox.set_alpha(140)
        textbox.fill((0, 0, 0))
        surface.blit(textbox, (0, GAME_HEIGHT - 80))

        # Text
        if self.phase == "CHOICE":
            t1 = font.render("1) Take medication (-$800, -35 stress)", True, (255, 255, 255))
            t2 = font.render("2) Skip medication (+20 stress)", True, (255, 255, 255))
            surface.blit(t1, (20, GAME_HEIGHT - 70))
            surface.blit(t2, (20, GAME_HEIGHT - 40))

        elif self.phase == "RESULT":
            txt = font.render(self.result_text, True, (255, 255, 255))
            txt2 = font.render("Press SPACE to continue", True, (255, 255, 255))
            surface.blit(txt, (20, GAME_HEIGHT - 70))
            surface.blit(txt2, (20, GAME_HEIGHT - 40))

        # Fade overlay
        if self.phase == "FADE":
            fade = pygame.Surface(surface.get_size())
            fade.fill((0, 0, 0))
            fade.set_alpha(int(self.fade_alpha))
            surface.blit(fade, (0, 0))
