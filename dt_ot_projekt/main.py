import pygame
from pygame.examples.grid import WINDOW_WIDTH

from sprites import *
from config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((screenWidth,screenHeight))
        self.clock = pygame.time.Clock()
        self.running = True


    def createTilemap(self):
        for i, row in enumerate(tilemap):
             for j, column in enumerate(row):
                 if column == "B":
                     Block(self,j,i)
                 if column == "P":
                     Player(self,j,i)

    #newgame
    def new(self):

        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates() #enables update all sprites at once
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.createTilemap()

    def events(self):
        #gameloop events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.playing = False
    def update(self):
        self.all_sprites.update() #method update from layeredUpdates updates every sprite

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(fps)
        pygame.display.update() #screen update

    def main(self):
        #gameloop
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False

    def game_over(self):
        pass

    def intro_screen(self):
        pass

game = Game()
game.intro_screen()
game.new()
while game.running:
    game.main()
    game.game_over()

pygame.quit()
sys.exit()