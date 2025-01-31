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


class Gun(pygame.sprite.Sprite):
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self._layer = playerLayer
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.hands = [
            pygame.image.load('assets/img/earthHand.png').convert_alpha(),  # Earth hand
            pygame.image.load('assets/img/fireHand.png').convert_alpha(),   # Fire hand
            pygame.image.load('assets/img/waterHand.png').convert_alpha(),  # Water hand
            pygame.image.load('assets/img/windHand.png').convert_alpha()    # Wind hand
        ]
        self.current_hand = 0  # Start with Earth hand
        self.image_original = self.hands[self.current_hand]
        self.image = self.image_original
        self.radius = 40
        self.rect = self.image.get_rect(center=self.player.rect.center)

    def switch_to_hand(self, hand_index):
        if 0 <= hand_index < len(self.hands):
            self.current_hand = hand_index
            self.image_original = self.hands[self.current_hand]
            self.update_position()  # Ensure it updates immediately

    def update_position(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        player_x, player_y = self.player.rect.center

        angle = math.degrees(math.atan2(mouse_y - player_y, mouse_x - player_x))

        self.image = pygame.transform.rotate(self.image_original, -angle)

        offset_x = self.radius * math.cos(math.radians(angle))
        offset_y = self.radius * math.sin(math.radians(angle))
        self.rect = self.image.get_rect(center=(player_x + offset_x, player_y + offset_y))

    def update(self):
        self.update_position()

class HealthBar(pygame.sprite.Sprite):
    def __init__(self, game, player):
        self.game = game
        self._layer = playerLayer
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.player = player

        # Load and scale heart images
        scale_factor = 0.5  # Adjust this value to make hearts smaller (0.5 = half size) or larger
        self.health_images = []
        original_images = [
            pygame.image.load('assets/img/0Heart.png').convert_alpha(),
            pygame.image.load('assets/img/1Heart.png').convert_alpha(),
            pygame.image.load('assets/img/2Heart.png').convert_alpha(),
            pygame.image.load('assets/img/3Heart.png').convert_alpha(),
            pygame.image.load('assets/img/4Heart.png').convert_alpha(),
        ]

        # Scale all images
        for img in original_images:
            original_size = img.get_size()
            scaled_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
            scaled_img = pygame.transform.scale(img, scaled_size)
            self.health_images.append(scaled_img)

        self.max_health = len(self.health_images) - 1  # Subtract 1 because 0Heart is at index 0
        self.current_health = self.max_health  # Start at full health

        self.image = self.health_images[self.current_health]
        self.rect = self.image.get_rect()
        self.rect.x = 20
        self.rect.y = 20

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0
            print("Game Over!")  # Placeholder for game-over logic

        # Update the displayed image
        self.image = self.health_images[self.current_health]

    def update(self):
        self.rect.x = 20
        self.rect.y = 20

class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = enemyLayer
        self.groups = game.all_sprites, self.game.enemies
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * tileSize
        self.y = y * tileSize

        self.width = tileSize
        self.height = tileSize

        self.x_change = 0
        self.y_change = 0

        self.image = self.game.enemySpritesheet.get_sprite(3, 2, self.width, self.height)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.facing = random.choice(["left", "right"])
        self.animationLoop = 1
        self.movementLoop = 0
        self.max_travel = random.randint(7, 30)

        self.detection_radius = 150  # Detection radius in pixels
        self.speed = enemySpeed  # Speed of the enemy

    def movement(self):
        if self.facing == 'left':
            self.x_change -= self.speed
            self.movementLoop -= 1
            if self.movementLoop <= -self.max_travel:
                self.facing = 'right'

        elif self.facing == 'right':
            self.x_change += self.speed
            self.movementLoop += 1
            if self.movementLoop >= self.max_travel:
                self.facing = 'left'

    def chase_player(self):
        if not hasattr(self.game, 'player') or self.game.player is None:
            return False

        player = self.game.player
        player_center = player.rect.center
        enemy_center = self.rect.center

        distance_to_player = math.sqrt(
            (player_center[0] - enemy_center[0]) ** 2 +
            (player_center[1] - enemy_center[1]) ** 2
        )

        # If the player is within the detection radius, move toward them
        if distance_to_player <= self.detection_radius:
            if player.rect.centerx > self.rect.centerx:
                self.x_change += self.speed
            elif player.rect.centerx < self.rect.centerx:
                self.x_change -= self.speed

            if player.rect.centery > self.rect.centery:
                self.y_change += self.speed
            elif player.rect.centery < self.rect.centery:
                self.y_change -= self.speed
            return True

        return False

    def update(self):
        if not self.chase_player():  # If not chasing the player, patrol
            self.movement()

        # Check for collision with the player
        if self.rect.colliderect(self.game.player.rect):
            self.game.player.take_damage(1)  # Reduce player health
            print("Player hit by enemy!")  # Debugging message

        # Update the enemy's position
        self.rect.x += self.x_change
        self.rect.y += self.y_change

        # Reset movement changes for the next frame
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

        #adding healthbar
        self.health_bar = HealthBar(self.game, self)
        self.gun = Gun(self.game, self)
        self.invulnerable = False
        self.invulnerable_timer = 0

    def take_damage(self, amount):
        if not self.invulnerable:
            self.health_bar.take_damage(amount)
            self.invulnerable = True
            self.invulnerable_timer = pygame.time.get_ticks()  # Set timer
            if self.health_bar.current_health == 0:
                print("Game Over!")

    def extract_sprite(self, x, y):
        full_sprite = self.game.charachterSpritesheet.get_sprite(x, y, 48, 64).convert_alpha()

        cropped_sprite = pygame.Surface((16, 32), pygame.SRCALPHA)  # Keep transparency
        cropped_sprite.blit(full_sprite, (0, 0), (16, 16, 16, 32))  # Crop (16px from left, 16px from top)

        cropped_sprite.set_colorkey((255, 0, 255))  # Assuming magenta (255, 0, 255) is unused in the sprite

        scaled_sprite = pygame.transform.scale(cropped_sprite, (32, 64))

        return scaled_sprite

    def update(self):
        """Update player movement, animations, and gun."""
        self.movement()
        self.animate()

        self.rect.x += self.xChange
        self.collide_blocks("x")
        self.rect.y += self.yChange
        self.collide_blocks("y")

        self.xChange = 0
        self.yChange = 0

        self.gun.update()

        if self.invulnerable:
            if pygame.time.get_ticks() - self.invulnerable_timer > 1000:
                self.invulnerable = False

    def draw(self, surface):
        surface.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 2)  # Red rectangle for debugging

    def movement(self):
        keys = pygame.key.get_pressed()

        self.xChange = 0
        self.yChange = 0

        if keys[pygame.K_a]:
            self.xChange = -playerSpeed
            self.facing = "left"
        if keys[pygame.K_d]:
            self.xChange = playerSpeed
            self.facing = "right"
        if keys[pygame.K_w]:
            self.yChange = -playerSpeed
            self.facing = "up"
        if keys[pygame.K_s]:
            self.yChange = playerSpeed
            self.facing = "down"

    def collide_blocks(self, direction):
        if direction == "x":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.xChange > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                if self.xChange < 0:
                    self.rect.x = hits[0].rect.right

        if direction == "y":
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                if self.yChange > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                if self.yChange < 0:
                    self.rect.y = hits[0].rect.bottom



    def animate(self):
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