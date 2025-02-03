import pygame
from pygame.examples.grid import WINDOW_WIDTH

from sprites import *
from config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth, screenHeight))
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_level = 0
        self.total_levels = len(tilemaps)
        self.level_keys = list(tilemaps.keys())


        self.level_timer_duration = 30
        self.level_timer_start = None
        self.spawn_interval = 2000
        self.last_spawn_time = 0


        self.charachterSpritesheet = SpriteSheet('assets/img/walk.png')
        self.terrainSpritesheet = SpriteSheet('assets/img/terrain.png')
        self.enemySpritesheet = SpriteSheet('assets/img/enemy.png')


        self.volume = 0.1
        pygame.mixer.init()
        pygame.mixer.music.load("assets/sound/gameMusic.mp3")
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

    def createTilemap(self):
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()
        self.portals = pygame.sprite.LayeredUpdates()

        level_key = self.level_keys[self.current_level]
        current_tilemap = tilemaps[level_key]

        for i, row in enumerate(current_tilemap):
            for j, column in enumerate(row):
                if self.current_level == 3:
                    StoneGround(self, j, i)
                    if column == "D":
                        Dragon(self, j, i)
                else:
                    Ground(self, j, i)

                if column == "B":
                    Block(self, j, i)
                elif column == "P":
                    self.player = Player(self, j, i)
                elif column == "H":
                    Pillar(self, j, i)
                elif column == "E":
                    Enemy(self, j, i)

    def start_level_timer(self):
        self.level_timer_start = pygame.time.get_ticks()

    def get_remaining_time(self):
        if self.level_timer_start is None:
            return self.level_timer_duration
        elapsed_time = (pygame.time.get_ticks() - self.level_timer_start) / 1000
        remaining_time = max(0, self.level_timer_duration - elapsed_time)
        return remaining_time

    def spawn_enemy_at_edge(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.randint(0, screenWidth // tileSize - 1)
            y = 0
        elif side == 'bottom':
            x = random.randint(0, screenWidth // tileSize - 1)
            y = screenHeight // tileSize - 1
        elif side == 'left':

            x = 0
            y = random.randint(0, screenHeight // tileSize - 1)
        elif side == 'right':
            x = screenWidth // tileSize - 1
            y = random.randint(0, screenHeight // tileSize - 1)

        if random.random() < 0.5 and self.current_level < 3:
            Bat(self, x, y)
        elif random.random() > 0.5 and self.current_level < 3:
            Enemy(self, x, y)

    def update_timer_and_spawning(self):
        remaining_time = self.get_remaining_time()

        now = pygame.time.get_ticks() *2
        if remaining_time > 0 and now - self.last_spawn_time >= self.spawn_interval:
            self.spawn_enemy_at_edge()
            self.last_spawn_time = now

        if remaining_time <= 0 and len(self.enemies) == 0 and not hasattr(self, "portal"):
            if hasattr(self, "last_enemy_position"):
                portal_x, portal_y = self.last_enemy_position
            else:
                portal_x, portal_y = screenWidth // 2, screenHeight // 2

            self.portal = Portal(self, portal_x, portal_y)


    def check_level_completion(self):
        if not self.enemies and not hasattr(self, "portal") and self.get_remaining_time() == 0:

            if hasattr(self, "last_enemy_position"):
                x, y = self.last_enemy_position

            self.portal = Portal(self, x, y)


    #newgame
    def new(self):

        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()



        if self.current_level == 3:
            pygame.mixer.music.stop()
            pygame.mixer.music.load("assets/sound/bossMusic.mp3")
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1)


        self.start_level_timer()
        self.createTilemap()



    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.player.gun.switch_to_hand(0)
                elif event.key == pygame.K_2:
                    self.player.gun.switch_to_hand(1)
                elif event.key == pygame.K_3:
                    self.player.gun.switch_to_hand(2)
                elif event.key == pygame.K_4:
                    self.player.gun.switch_to_hand(3)


    def update(self):
        self.all_sprites.update()
        self.check_level_completion()
        self.update_timer_and_spawning()

    def draw(self):
        self.screen.fill(BLUE)
        self.all_sprites.draw(self.screen)

        font = pygame.font.Font(None, 60)
        timer_text = font.render(f"{int(self.get_remaining_time())}s", True, WHITE)
        timer_rect = timer_text.get_rect(center=(screenWidth // 2, 20))
        self.screen.blit(timer_text, timer_rect)

        self.clock.tick(fps)
        pygame.display.update()  #screen update

        for sprite in self.all_sprites:
            if isinstance(sprite, Player):
                sprite.draw(self.screen)


    def next_level(self):
        self.current_level += 1
        if self.current_level < self.total_levels:
            if hasattr(self, "portal"):
                self.portal.kill()
                del self.portal

            self.new()
        else:
            print("Game Completed!")
            self.winner_screen()
            self.running = False

    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False

    def game_over_screen(self):

        pygame.mixer.music.stop()
        pygame.mixer.music.load("assets/sound/gameOver.mp3")
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

        gameover_background = pygame.image.load("assets/img/gameoverScreen.png").convert()
        font = pygame.font.Font('assets/fonts/upheavtt.ttf', 80)
        game_over_text = font.render("Game Over", True, RED)
        game_over_rect = game_over_text.get_rect(center=(screenWidth // 2, screenHeight // 3))

        exit_font = pygame.font.Font('assets/fonts/upheavtt.ttf', 50)
        exit_text = exit_font.render("Exit", True, WHITE)
        exit_rect = exit_text.get_rect(center=(screenWidth // 2, screenHeight // 2 + 70))

        while True:
            self.screen.blit(gameover_background, (0, 0))
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(exit_text, exit_rect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if exit_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

    def intro_screen(self):

        intro_background = pygame.image.load("assets/img/introScreen.png").convert()
        font = pygame.font.Font('assets/fonts/upheavtt.ttf', 80)  # Large font for the title
        title_text = font.render("Elemental Survival", True, WHITE)
        title_rect = title_text.get_rect(center=(screenWidth // 2, screenHeight // 3))

        play_font = pygame.font.Font('assets/fonts/upheavtt.ttf', 50)  # Smaller font for buttons
        play_text = play_font.render("Play", True, WHITE)
        play_rect = play_text.get_rect(center=(screenWidth // 2, screenHeight // 2))

        exit_text = play_font.render("Exit", True, WHITE)
        exit_rect = exit_text.get_rect(center=(screenWidth // 2, screenHeight // 2 + 70))

        while True:
            self.screen.blit(intro_background, (0, 0))
            self.screen.blit(title_text, title_rect)
            self.screen.blit(play_text, play_rect)
            self.screen.blit(exit_text, exit_rect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if play_rect.collidepoint(mouse_pos):
                        return
                    if exit_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

    def winner_screen(self):

        pygame.mixer.music.stop()

        pygame.mixer.music.load("assets/sound/completed.mp3")
        pygame.mixer.music.set_volume(self.volume)
        pygame.mixer.music.play(-1)

        winner_background = pygame.image.load("assets/img/gameoverScreen.png").convert()

        font = pygame.font.Font('assets/fonts/upheavtt.ttf', 80)
        winner_text = font.render("WINNER", True, GREEN)
        winner_rect = winner_text.get_rect(center=(screenWidth // 2, screenHeight // 3))

        exit_font = pygame.font.Font('assets/fonts/upheavtt.ttf', 50)
        exit_text = exit_font.render("Exit", True, WHITE)
        exit_rect = exit_text.get_rect(center=(screenWidth // 2, screenHeight // 2 + 70))

        while True:
            self.screen.blit(winner_background, (0, 0))
            self.screen.blit(winner_text, winner_rect)
            self.screen.blit(exit_text, exit_rect)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if exit_rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

game = Game()
game.intro_screen()
game.new()
while game.running:

    game.main()
    game.game_over_screen()

pygame.quit()
sys.exit()
