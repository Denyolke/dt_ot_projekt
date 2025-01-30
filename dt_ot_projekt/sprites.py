import pygame
from config import *
import math
import random

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = playerLayer #setting which layer to appear on
        self.groups = self.game.all_sprites #adding player to allsprites group
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x*tileSize
        self.y = y*tileSize
        self.width = tileSize
        self.height = tileSize

        self.xChange = 0
        self.yChange = 0
        self.facing = "down"

        #image
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(RED)
        #hitbox/pos
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def update(self):
        self.movement()

        self.rect.x += self.xChange
        self.rect.y += self.yChange

        #temp variables to counter player drifting
        self.xChange = 0
        self.yChange = 0


    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.xChange -= playerSpeed
            self.facing = "left"
        if keys[pygame.K_RIGHT]:
            self.xChange += playerSpeed
            self.facing = "right"
        if keys[pygame.K_UP]:
            self.yChange -= playerSpeed
            self.facing = "up"
        if keys[pygame.K_DOWN]:
            self.yChange += playerSpeed
            self.facing = "down"


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = blockLayer
        self.groups = self.game.all_sprites, self.game.blocks
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x*tileSize
        self.y = y*tileSize
        self.width = tileSize
        self.height = tileSize

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(BLUE)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
