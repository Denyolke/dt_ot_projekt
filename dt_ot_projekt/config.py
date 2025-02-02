screenWidth = 1280
screenHeight = 736
tileSize = 32
fps = 60
print("The tilemaps size should be: ", screenWidth / 32, "x",  screenHeight/ 32, "y")

playerSpeed = 3
enemySpeed = 1
enemyHealth = 3

playerLayer = 5
skillLayer = 4
enemyLayer = 3
blockLayer = 2
groundLayer = 1

current_hand = 0

airAttackSpeed = 400

fireProjectileSpeed = 5
fireProjectileDamage = 2
fireAttackSpeed = 700
fireProjectileMaxDistance = 300


waterPuddleDuration = 5000
waterPuddleDamage = 1
waterPuddleTickRate = 1000
waterPuddleKnockback = 5
waterAttackSpeed = 5000

earthProjectileDamage = 3
earthAttackSpeed = 800
earthProjectileSpeed = 7


RED = (255,0,0)
BLACK = (0,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)

tilemap =  [
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',#40
    'B......................................B',
    'B......................................B',
    'B......................................B',
    'B......................................B',
    'B...........BBB........................B',
    'B.............B........................B',
    'B.............B........................B',
    'B..............................E.......B',
    'B.....BBB..............................B',
    'B..................P...................B',
    'B......................................B',
    'B......................................B',
    'B......................................B',
    'B.................E....................B',
    'B......................................B',
    'B......................................B',
    'B......................................B',
    'B......................................B',
    'B......................................B',
    'B......................................B',
    'B......................................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
                                            #23
]


