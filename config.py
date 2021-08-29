import pygame

margin = 2
WIDTH = 1000
HEIGHT = 720 + margin
screen = pygame.display.set_mode([WIDTH, HEIGHT])

BOARD_SIZE = 12
grid_size = int(round((HEIGHT - margin) / BOARD_SIZE))

FPS = 30
fpsClock = pygame.time.Clock()


BULLET_SIZE = 10
ENEMY_IMG_SIZE = grid_size // 2

HP_BAR_THICKNESS = 4
HP_BAR_ABOVE_ENEMY_CENTER = ENEMY_IMG_SIZE // 2 + 8
HP_BAR_BORDER = 1

tower_font_size = 14
slot_font_size = 14
path_dot_size = 28


ENEMY_SPAWN_INTERVAL = 800  # ms
WAVE_DELAY = 10000


DEFEAT_ENEMY_SCORE = 10
INIT_PORT_HP = 20

SHOW_AIM_LINE = 1  # if 1, show aim line

TOWER_MAX_LVL = 4
# (atk, atk_range)
TOWER_ATTR_DICT = {
    'Cannon1': (20, round(grid_size * 3.1)),
    'Cannon2': (50, round(grid_size * 3.1)),
    'Cannon3': (130, round(grid_size * 3.6)),
    'Cannon4': (360, round(grid_size * 3.6)),

    'Sniper1': (40, round(grid_size * 5.1)),
    'Sniper2': (105, round(grid_size * 5.1)),
    'Sniper3': (280, round(grid_size * 6.1)),
    'Sniper4': (750, round(grid_size * 6.1)),

    'Crusher1': (15, round(grid_size * 2.1)),
    'Crusher2': (40, round(grid_size * 2.1)),
    'Crusher3': (100, round(grid_size * 2.6)),
    'Crusher4': (260, round(grid_size * 2.6))
}

# (hp, ms)
ENEMY_ATTR_DICT = {
    'Circle': (30, 2.5),
    'Square': (100, 1.5)
}

CANNON_ATK_INT = 0.8
SNIPER_ATK_INT = 2
CRUSHER_ATK_INT = 1.5
# Bullet Speed
CANNON_BS = FPS * 0.8
SNIPER_BS = FPS * 1.5


white = (255, 255, 255)
green = (0, 255, 0)
lighter_green = (0, 200, 0)
blue = (0, 0, 128)
azure = (170, 240, 250)
black = (0, 0, 0)
red = (255, 0, 0)
dark_grey = (43, 45, 47)
light_grey = (180, 180, 180)
ATK_RANGE_COLOR = (160, 220, 235)
