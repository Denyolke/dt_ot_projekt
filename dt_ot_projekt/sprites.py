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


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, game, player):
        self.game = game
        self._layer = playerLayer
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.player = player

        scale_factor = 0.5
        self.health_images = []
        original_images = [
            pygame.image.load('assets/img/0Heart.png').convert_alpha(),
            pygame.image.load('assets/img/1Heart.png').convert_alpha(),
            pygame.image.load('assets/img/2Heart.png').convert_alpha(),
            pygame.image.load('assets/img/3Heart.png').convert_alpha(),
            pygame.image.load('assets/img/4Heart.png').convert_alpha(),
        ]


        for img in original_images:
            original_size = img.get_size()
            scaled_size = (int(original_size[0] * scale_factor), int(original_size[1] * scale_factor))
            scaled_img = pygame.transform.scale(img, scaled_size)
            self.health_images.append(scaled_img)

        self.max_health = len(self.health_images) - 1
        self.current_health = self.max_health

        self.image = self.health_images[self.current_health]
        self.rect = self.image.get_rect()
        self.rect.x = 20
        self.rect.y = 20

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0
            print("Game Over!")

        self.image = self.health_images[self.current_health]

    def update(self):
        self.rect.x = 20
        self.rect.y = 20


class Gun(pygame.sprite.Sprite):
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self._layer = playerLayer
        self.groups = game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.hands = [
            pygame.image.load('assets/img/earthHand.png').convert_alpha(),
            pygame.image.load('assets/img/fireHand.png').convert_alpha(),
            pygame.image.load('assets/img/waterHand.png').convert_alpha(),
            pygame.image.load('assets/img/windHand.png').convert_alpha()
        ]
        self.current_hand = 0  # Start with Earth hand
        self.image_original = self.hands[self.current_hand]
        self.image = self.image_original
        self.radius = 40
        self.rect = self.image.get_rect(center=self.player.rect.center)
        self.last_shot = pygame.time.get_ticks()

    def switch_to_hand(self, hand_index):
        if 0 <= hand_index < len(self.hands):
            self.current_hand = hand_index
            self.image_original = self.hands[self.current_hand]
            print("Switch detected (",self.current_hand,")")
    def shoot(self):
        now = pygame.time.get_ticks()
        if self.current_hand == 3 and now - self.last_shot > airAttackSpeed:  # Air hand
            self.last_shot = now
            print("Shooting air projectile!")
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_x, player_y = self.player.rect.center
            angle = math.degrees(math.atan2(mouse_y - player_y, mouse_x - player_x))
            AirProjectile(self.game, self.rect.centerx, self.rect.centery, angle)

        elif self.current_hand == 2 and now - self.last_shot > waterAttackSpeed:  # Water hand
            self.last_shot = now
            print("Creating water attack!")
            WaterAttack(self.game, self.game.player)

        elif self.current_hand == 1 and now - self.last_shot > fireAttackSpeed:  # Fire hand
            self.last_shot = now
            print("Shooting fire boomerang!")
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_x, player_y = self.rect.center  # Gun position
            angle = math.degrees(math.atan2(mouse_y - player_y, mouse_x - player_x))
            FireProjectile(self.game, player_x, player_y, angle)

        elif self.current_hand == 0 and now - self.last_shot > earthAttackSpeed:  # Earth hand
            self.last_shot = now
            print("Shooting earth projectile!")
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_x, player_y = self.rect.center  # Gun position
            angle = math.degrees(math.atan2(mouse_y - player_y, mouse_x - player_x))
            EarthProjectile(self.game, player_x, player_y, angle)

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

        keys = pygame.mouse.get_pressed()
        if keys[0]:  # Left mouse button
            self.shoot()


class AirProjectile(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle):
        self.game = game
        self.groups = game.all_sprites, game.attacks
        self._layer = skillLayer
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.speed = 8
        self.damage = 1
        self.attack_speed = airAttackSpeed
        self.knockback_strength = 10

        self.image_original = pygame.image.load('assets/img/airShot.png').convert_alpha()


        self.image = pygame.transform.rotate(self.image_original, -angle)
        self.rect = self.image.get_rect(center=(x, y))

        self.angle = math.radians(angle)
        self.dx = self.speed * math.cos(self.angle)
        self.dy = self.speed * math.sin(self.angle)

        self.rect.x -= self.game.player.xChange
        self.rect.y -= self.game.player.yChange

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        self.rect.x += self.game.player.xChange
        self.rect.y += self.game.player.yChange

        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            for enemy in hits:
                enemy.take_damage(self.damage)  # Apply damage to the enemy
                enemy.apply_knockback(
                    self.knockback_strength * self.dx, self.knockback_strength * self.dy
                )  # Apply knockback

            self.kill()

        if (self.rect.right < 0 or self.rect.left > screenWidth or
            self.rect.bottom < 0 or self.rect.top > screenHeight):
            self.kill()


class WaterAttack(pygame.sprite.Sprite):
    def __init__(self, game, player):
        self.game = game
        self.player = player
        self.groups = game.all_sprites, game.attacks
        self._layer = skillLayer
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.damage = waterPuddleDamage
        self.duration = waterPuddleDuration
        self.tick_rate = waterPuddleTickRate
        self.knockback_strength = waterPuddleKnockback
        self.spawn_time = pygame.time.get_ticks()
        self.last_tick = pygame.time.get_ticks()
        self.attack_speed = waterAttackSpeed

        self.radius = 60
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (0, 0, 255, 100), (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=self.player.rect.center)

    def damage_enemies(self):
        for enemy in self.game.enemies:
            # Check if the enemy is inside the circle
            distance = math.sqrt(
                (enemy.rect.centerx - self.rect.centerx) ** 2 +
                (enemy.rect.centery - self.rect.centery) ** 2
            )
            if distance <= self.radius:
                now = pygame.time.get_ticks()
                if now - self.last_tick >= self.tick_rate:
                    self.last_tick = now
                    enemy.take_damage(self.damage)

                angle = math.atan2(
                    enemy.rect.centery - self.rect.center[1],
                    enemy.rect.centerx - self.rect.center[0]
                )
                knockback_x = math.cos(angle) * self.knockback_strength
                knockback_y = math.sin(angle) * self.knockback_strength
                enemy.rect.x += knockback_x
                enemy.rect.y += knockback_y

    def update(self):
        self.rect.center = self.player.rect.center

        self.damage_enemies()

        if pygame.time.get_ticks() - self.spawn_time > self.duration:
            self.kill()


class FireProjectile(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle):
        self.game = game
        self.groups = game.all_sprites, game.attacks
        self._layer = skillLayer
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.speed = fireProjectileSpeed
        self.damage = fireProjectileDamage
        self.max_distance = fireProjectileMaxDistance
        self.spawn_time = pygame.time.get_ticks()

        self.frames = [
            pygame.image.load('assets/img/FireShot1.png').convert_alpha(),
            pygame.image.load('assets/img/FireShot2.png').convert_alpha(),
            pygame.image.load('assets/img/FireShot3.png').convert_alpha(),
            pygame.image.load('assets/img/FireShot4.png').convert_alpha()
        ]
        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(center=(x, y))

        # Travel calculations
        self.angle = math.radians(angle)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

        # Position tracking
        self.start_x = x
        self.start_y = y
        self.travelled_distance = 0
        self.returning = False

    def animate(self):
        self.animation_index += 0.2
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animate()

        if self.returning:
            player_x, player_y = self.game.player.rect.center
            angle_to_player = math.atan2(player_y - self.rect.centery, player_x - self.rect.centerx)
            self.dx = math.cos(angle_to_player) * self.speed
            self.dy = math.sin(angle_to_player) * self.speed

        self.rect.x += self.dx
        self.rect.y += self.dy

        self.travelled_distance += self.speed

        if self.travelled_distance >= self.max_distance and not self.returning:
            self.returning = True

        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            for enemy in hits:
                enemy.take_damage(self.damage)
            self.returning = True

        block_hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
        if block_hits:
            self.returning = True

        if self.returning and self.rect.colliderect(self.game.player.rect):
            self.kill()

class EarthProjectile(pygame.sprite.Sprite):
    def __init__(self, game, x, y, angle):
        self.game = game
        self.groups = game.all_sprites, game.attacks
        self._layer = skillLayer
        pygame.sprite.Sprite.__init__(self, self.groups)

        # Attributes
        self.damage = earthProjectileDamage  # Damage dealt by the projectile
        self.speed = earthProjectileSpeed  # Speed of the projectile

        self.image_original = pygame.image.load('assets/img/EarthShot.png').convert_alpha()


        self.image = pygame.transform.rotate(self.image_original, -angle)
        self.rect = self.image.get_rect(center=(x, y))

        self.angle = math.radians(angle)
        self.dx = math.cos(self.angle) * self.speed
        self.dy = math.sin(self.angle) * self.speed

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy

        # Adjust position for camera shifts (if applicable)
        self.rect.x += self.game.player.xChange
        self.rect.y += self.game.player.yChange

        # Check for collision with enemies
        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            for enemy in hits:
                enemy.take_damage(self.damage)
            self.kill()

        if (self.rect.right < 0 or self.rect.left > screenWidth or
            self.rect.bottom < 0 or self.rect.top > screenHeight):
            self.kill()

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

        self.image_original = self.game.enemySpritesheet.get_sprite(3, 2, self.width, self.height)
        self.image_original.set_colorkey(BLACK)
        self.image = self.image_original.copy()
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.facing = random.choice(["left", "right"])
        self.animationLoop = 1
        self.movementLoop = 0
        self.max_travel = random.randint(7, 30)

        self.detection_radius = 150
        self.speed = enemySpeed

        self.health = enemyHealth
        self.damaged = False
        self.damage_timer = 0

    def take_damage(self, amount):
        self.health -= amount
        print(f"Enemy hit remaining health: {self.health}")

        self.damaged = True
        self.damage_timer = pygame.time.get_ticks()
        self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        if self.health <= 0:
            self.kill()
            print("Enemy dead")

    def apply_knockback(self, knockback_x, knockback_y):
        self.rect.x += knockback_x
        self.rect.y += knockback_y

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
        if not self.chase_player():
            self.movement()

        if self.damaged:
            if pygame.time.get_ticks() - self.damage_timer > 200:
                self.damaged = False
                self.image = self.image_original.copy()

        if self.rect.colliderect(self.game.player.rect):
            self.game.player.take_damage(1)
            print("Player hit by enemy!")

        self.rect.x += self.x_change
        self.rect.y += self.y_change


        self.x_change = 0
        self.y_change = 0


class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self._layer = skillLayer
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)


        self.x = x * tileSize
        self.y = y * tileSize
        self.width = 32
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


        self.image = self.animations["down"][0]

        # Adjusted hitbox/position (now matches scaled size)
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

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
        cropped_sprite.blit(full_sprite, (0, 0), (16, 16, 16, 32))

        cropped_sprite.set_colorkey((255, 0, 255))

        scaled_sprite = pygame.transform.scale(cropped_sprite, (32, 64))

        return scaled_sprite

    def update(self):
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
            for sprite in self.game.all_sprites:
                sprite.rect.x += playerSpeed
            self.xChange = -playerSpeed
            self.facing = "left"
        if keys[pygame.K_d]:
            for sprite in self.game.all_sprites:
                sprite.rect.x -= playerSpeed
            self.xChange = playerSpeed
            self.facing = "right"
        if keys[pygame.K_w]:
            for sprite in self.game.all_sprites:
                sprite.rect.y += playerSpeed
            self.yChange = -playerSpeed
            self.facing = "up"
        if keys[pygame.K_s]:
            for sprite in self.game.all_sprites:
                sprite.rect.y -= playerSpeed
            self.yChange = playerSpeed
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
        if self.xChange != 0 or self.yChange != 0:
            self.animation_loop += 0.1
            if self.animation_loop >= len(self.animations[self.facing]):
                self.animation_loop = 0
            self.image = self.animations[self.facing][int(self.animation_loop)]
        else:
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