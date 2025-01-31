import pygame
from config import *
import math
import random

class SpriteSheet():
    def __init__(self,file):
        self.sheet = pygame.image.load(file).convert()

    def get_sprite(self,x,y,width,height):
        sprite = pygame.Surface([width,height])
        sprite.blit(self.sheet,(0,0),(x,y,width,height))
        sprite.set_colorkey(BLACK)
        return sprite


class CollisionBox(pygame.sprite.Sprite):
    def __init__(self, game, player):
        self._layer = 4
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.player = player
        self.image = pygame.Surface([player.width, player.height], pygame.SRCALPHA)
        self.rect = self.image.get_rect()

    def update(self):
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, RED, (0, 0, self.player.width, self.player.height), 2)

        # Calculate the offset to center the collision box on the scaled sprite
        x_offset = (self.player.scaled_width - self.player.width) // 2
        y_offset = (self.player.scaled_height - self.player.height) // 2

        # Update position with offset
        self.rect.x = self.player.rect.x + x_offset
        self.rect.y = self.player.rect.y + y_offset


class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x,y):
        self.game = game
        self._layer = enemyLayer
        self.groups = game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x*tileSize
        self.y = y*tileSize

        self.width = tileSize
        self.height = tileSize

        self.x_change = 0
        self.y_change = 0

        self.image = self.game.enemySpritesheet.get_sprite(3,2,self.width,self.height)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.facing = random.choice(["left","right"])
        self.animationLoop = 1
        self.movementLoop = 0
        self.max_travel = random.randint(7, 30)

    def movement(self):
        if self.facing == 'left':
            self.x_change -= enemySpeed
            self.movementLoop -= 1
            if self.movementLoop <= -self.max_travel:
                self.facing = 'right'

        if self.facing == 'right':
            self.x_change += enemySpeed
            self.movementLoop += 1
            if self.movementLoop >= self.max_travel:
                self.facing = 'left'

    def update(self):
        self.movement()
        self.rect.x += self.x_change
        self.rect.y += self.y_change


        self.x_change = 0
        self.y_change = 0


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = playerLayer  # Setting which layer to appear on
        self.groups = self.game.all_sprites  # Adding player to allsprites group
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * tileSize
        self.y = y * tileSize
        self.width = 32  # Scaled sprite size
        self.height = 64

        self.xChange = 0
        self.yChange = 0
        self.facing = "down"
        self.animation_loop = 0

        # Animations for all directions
        self.animations = {
            "down": [
                self.extract_sprite(0, 0),
                self.extract_sprite(48, 0),
                self.extract_sprite(96, 0)
            ],
            "left": [
                self.extract_sprite(0, 64),
                self.extract_sprite(48, 64),
                self.extract_sprite(96, 64)
            ],
            "up": [
                self.extract_sprite(0, 192),
                self.extract_sprite(48, 192),
                self.extract_sprite(96, 192)
            ],
            "right": [
                self.extract_sprite(0, 320),
                self.extract_sprite(48, 320),
                self.extract_sprite(96, 320)
            ],
        }

        # Set initial image
        self.image = self.animations["down"][0]

        # Adjusted hitbox/position (now matches scaled size)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def extract_sprite(self, x, y):
        # Extract the 48x64 frame
        full_sprite = self.game.charachterSpritesheet.get_sprite(x, y, 48, 64).convert_alpha()

        # Crop the sprite to 16x32 centered in the 48x64 frame
        cropped_sprite = pygame.Surface((16, 32), pygame.SRCALPHA)  # Keep transparency
        cropped_sprite.blit(full_sprite, (0, 0), (16, 16, 16, 32))  # Crop (16px from left, 16px from top)

        # Ensure no unintentional transparency by preserving original pixel data
        cropped_sprite.set_colorkey((255, 0, 255))  # Assuming magenta (255, 0, 255) is unused in the sprite

        # Scale up to 32x64 for better visibility
        scaled_sprite = pygame.transform.scale(cropped_sprite, (32, 64))

        return scaled_sprite

    def update(self):
        self.movement()
        self.animate()

        self.rect.x += self.xChange
        self.collide_blocks("x")
        self.rect.y += self.yChange
        self.collide_blocks("y")
        # Reset movement after each frame
        self.xChange = 0
        self.yChange = 0

    def draw(self, surface):
        # Draw the player sprite
        surface.blit(self.image, (self.rect.x, self.rect.y))

        # Draw the hitbox (collision rectangle) in red for visualization
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)  # Red rectangle, 2-pixel thickness

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            for sprite in self.game.all_sprites:
                sprite.rect.x += playerSpeed
            self.xChange -= playerSpeed
            self.facing = "left"
        if keys[pygame.K_RIGHT]:
            for sprite in self.game.all_sprites:
                sprite.rect.x -= playerSpeed
            self.xChange += playerSpeed
            self.facing = "right"
        if keys[pygame.K_UP]:
            for sprite in self.game.all_sprites:
                sprite.rect.y += playerSpeed
            self.yChange -= playerSpeed
            self.facing = "up"
        if keys[pygame.K_DOWN]:
            for sprite in self.game.all_sprites:
                sprite.rect.y -= playerSpeed
            self.yChange += playerSpeed
            self.facing = "down"

    def collide_blocks(self, direction):
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.xChange > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                    for sprite in self.game.all_sprites:
                        sprite.rect.x += playerSpeed
                if self.xChange < 0:
                    self.rect.x = hits[0].rect.right
                    for sprite in self.game.all_sprites:
                        sprite.rect.x -= playerSpeed

        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.yChange > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                    for sprite in self.game.all_sprites:
                        sprite.rect.y += playerSpeed
                if self.yChange < 0:
                    self.rect.y = hits[0].rect.bottom
                    for sprite in self.game.all_sprites:
                        sprite.rect.y -= playerSpeed



    def animate(self):
        # Change frame every few updates for smooth animation
        if self.xChange != 0 or self.yChange != 0:
            self.animation_loop += 0.1
            if self.animation_loop >= len(self.animations[self.facing]):
                self.animation_loop = 0
            self.image = self.animations[self.facing][int(self.animation_loop)]
        else:
            # Reset to standing frame when not moving
            self.image = self.animations[self.facing][0]


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

        self.image = self.game.terrainSpritesheet.get_sprite(960,480,self.width,self.height)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Ground(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = groundLayer
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.x = x*tileSize
        self.y = y*tileSize
        self.width = tileSize
        self.height = tileSize


        self.image = self.game.terrainSpritesheet.get_sprite(64,352,self.width,self.height)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y