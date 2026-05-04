import pygame
from settings import *
from player import Player
from sprites import *
from pytmx.util_pygame import load_pygame
from groups import AllSprites
from live_data import LiveData
from nodes import MomentumNode, LiquidityNode, RiskNode, DarkPoolNode
from terminal import Terminal
from signal_engine import SignalEngine
from results_screen import ResultsScreen
from os.path import join
from os import walk


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Survivor")
        self.clock = pygame.time.Clock()
        self.running = True

        self.state = "RUNNING"
        self.run_time = 60
        self.run_end_reason = None
        self.trade_committed = False

        # SEC Heat
        self.heat = 0
        self.heat_max = 100
        self.heat_decay_rate = 4
        self.heat_gain_node = 12
        self.heat_gain_trade = 20
        self.heat_gain_hold = 4

        # Groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.node_sprites = pygame.sprite.Group()

        # Systems
        self.terminal = Terminal()
        self.signal_engine = SignalEngine()
        self.live_data = LiveData(["NVDA", "TSLA", "AAPL", "GME"], update_interval=15000)
        self.signal_engine.set_live_data(self.live_data)
        self.results_screen = ResultsScreen()

        # Player money
        self.capital = 1000

        # Gun
        self.can_shoot = True
        self.shoot_time = 100
        self.gun_cooldown = 100

        # Map data
        self.nasdaq_rect = None
        self.nearby_node = None

        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(
            join("images", "Player", "bullet.png")
        ).convert_alpha()

        enemy_folder = join("images", "enemies", "blob")
        self.enemy_frames = []
        for _, _, files in walk(enemy_folder):
            for file in sorted(files, key=lambda n: int(n.split(".")[0])):
                surf = pygame.image.load(join(enemy_folder, file)).convert_alpha()
                self.enemy_frames.append(surf)
            break

    def setup(self):
        tmx_map = load_pygame(join("data", "maps", "my_city.tmx"))

        # Ground
        for x, y, image in tmx_map.get_layer_by_name("Ground").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites, ground=True)

        # Objects
        for obj in tmx_map.get_layer_by_name("Objects"):
            image = tmx_map.get_tile_image_by_gid(obj.gid)
            if image:
                Sprite((obj.x, obj.y - 64), image, self.all_sprites)

        # Collisions
        for obj in tmx_map.get_layer_by_name("Collisions"):
            self.image = pygame.image.load(join("images", "Player", "regularpisto.png")).convert_alpha()
            self.original_image = self.image


        entities = tmx_map.get_layer_by_name("Entities")

        # PASS 1 — create player first
        for obj in entities:
            if obj.name == "Player":
                self.player = Player((obj.x, obj.y), self.all_sprites, self.collision_sprites)
                self.gun = Gun(self.player, self.all_sprites)
                break

        # PASS 2 — everything else
        for obj in entities:

            if obj.name == "Player":
                continue

            if obj.name == "Nasdaqnode":
                self.nasdaq_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                continue

            if obj.name == "Enemy":
                Enemy((obj.x, obj.y), self.enemy_frames,
                      (self.all_sprites, self.enemy_sprites),
                      self.player, self.collision_sprites)
                continue

            node_type = obj.properties.get("node_type")
            symbol = obj.properties.get("symbol")

            if node_type == "momentum":
                MomentumNode((obj.x, obj.y), symbol, (self.all_sprites, self.node_sprites))
            elif node_type == "liquidity":
                LiquidityNode((obj.x, obj.y), symbol, (self.all_sprites, self.node_sprites))
            elif node_type == "risk":
                RiskNode((obj.x, obj.y), symbol, (self.all_sprites, self.node_sprites))
            elif node_type == "darkpool":
                DarkPoolNode((obj.x, obj.y), symbol, (self.all_sprites, self.node_sprites))

    # Shooting
    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(self.bullet_surf, pos, self.gun.player_direction, (self.all_sprites, self.bullet_sprites))
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot =True

    # Collisions
    def bullet_collision(self):
        for bullet in self.bullet_sprites:
            hits = pygame.sprite.spritecollide(
                bullet, self.enemy_sprites, False, pygame.sprite.collide_mask
            )
            if hits:
                for enemy in hits:
                    enemy.destroy()
                bullet.kill()

    def player_collision(self):
        hits = pygame.sprite.spritecollide(
            self.player, self.enemy_sprites, False, pygame.sprite.collide_mask
        )
        if hits:
            if self.trade_committed:
                self.capital -= 500
            self.run_end_reason = "CAUGHT_BY_POLICE"
            self.end_run()

    # SEC Heat
    def update_heat(self, dt):
        if self.heat > 0:
            self.heat -= self.heat_decay_rate * dt
            self.heat = max(self.heat, 0)

        if self.trade_committed:
            self.heat += self.heat_gain_hold * dt
            self.heat = min(self.heat, self.heat_max)

        if self.heat >= self.heat_max:
            self.run_end_reason = "SEC_ALERT"
            self.end_run()

    def end_run(self):
        self.state = "RESULTS"
        self.results_screen.collect(
            capital=self.capital,
            pl=self.signal_engine.get_display_data().get("pl", 0),
            intel=self.signal_engine.captured_label,
            nodes=self.signal_engine.nodes_accessed,
            enemies=self.signal_engine.enemies_defeated,
            reason=self.run_end_reason,
        )

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and self.terminal.visible:
                        self.signal_engine.tap_in()
                        self.trade_committed = True

                        self.heat += self.heat_gain_node
                        self.heat += self.heat_gain_trade

                        for e in self.enemy_sprites:
                            e.set_mode("aggressive")

                        self.terminal.close()

            if self.state == "RESULTS":
                self.display_surface.fill("black")
                self.results_screen.draw(self.display_surface)
                pygame.display.update()
                continue

            self.run_time -= dt
            if self.run_time <= 0:
                self.run_end_reason = "TIME_UP"
                self.end_run()
                continue

            self.live_data.update()
            self.signal_engine.update(dt)
            self.update_heat(dt)

            if self.terminal.visible:
                for e in self.enemy_sprites:
                    if e.mode == "npc" and e.has_line_of_sight(self.player, self.collision_sprites):
                        e.set_mode("aggressive")
                        self.heat += 8

            self.terminal.near_node = False
            self.nearby_node = None

            for node in self.node_sprites:
                dx = node.rect.centerx - self.player.rect.centerx
                dy = node.rect.centery - self.player.rect.centery
                dist = (dx * dx + dy * dy) ** 0.5

                if dist < TERMINAL_RADIUS:
                    self.terminal.near_node = True
                    self.nearby_node = node
                    break

            if self.terminal.near_node:
                if not self.terminal.visible:
                    self.signal_engine.set_active_node(self.nearby_node)
                    self.terminal.open(self.nearby_node)
            else:
                if self.terminal.visible:
                    self.terminal.close()

            if self.nasdaq_rect and self.player.rect.colliderect(self.nasdaq_rect):

                if self.trade_committed and self.signal_engine.captured_label:
                    payout = self.signal_engine.cash_out()
                    self.capital += payout
                    self.run_end_reason = "REACHED_NASDAQ"
                else:
                    self.run_end_reason = "NO_ACTIVE_TRADE"

                self.end_run()
                continue

            self.gun_timer()
            self.input()
            self.all_sprites.update(dt)
            self.bullet_collision()
            self.player_collision()

            self.display_surface.fill("black")
            self.all_sprites.draw(self.player.rect.center)

            bar_width = 200
            heat_ratio = self.heat / self.heat_max
            pygame.draw.rect(self.display_surface, "red", (20, 20, bar_width * heat_ratio, 20))
            pygame.draw.rect(self.display_surface, "white", (20, 20, bar_width, 20), 2)

            data = self.signal_engine.get_display_data()
            data["capital"] = self.capital
            data["pl_display"] = f"${data.get('pl', 0):.2f}"
            data["insider_hint"] = self.terminal.get_hint()
            data["run_time"] = self.run_time

            self.terminal.data = data
            self.terminal.draw(self.display_surface)

            pygame.display.update()

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
