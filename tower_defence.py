from config import *
from typing import Tuple, List, Union, Optional, Dict
import pygame
from pygame.math import Vector2
import pygame.gfxdraw
import random


def get_grid(pos) -> Tuple[int, int]:
    """Get pos on lst from mouse position.
    """
    x, y = pos[0], pos[1]
    row, col = y // grid_size, x // grid_size  # row and col in lst

    return row, col


def get_coord(path: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Get coord of center of a square on pygame from a nested list.
    """
    lst = []
    for pos in path:
        x, y = pos[1] + 1, pos[0] + 1
        coord_x = grid_size * x - (grid_size - margin) // 2
        coord_y = grid_size * y - (grid_size + margin) // 2
        lst.append((coord_x, coord_y))

    return lst


class Enemy(pygame.sprite.Sprite):
    """
    Enemy class

    === Public Attributes ===
    hp: hp of an enemy
    ms: Movement speed of an enemy
    defence: percentage of damage taken from an attack (normally)
    pos: position
    travelled: distance travelled by the enemy object
    """
    max_hp: int
    hp: int
    ms: int
    defence: float
    pos: Vector2
    path: List[Tuple[int, int]]
    path_index: int

    def __init__(self, hp, ms, board):
        """Enemy_attr: attributes of enemy."""
        super().__init__()
        # self.image = pygame.Surface((24, 24))
        # self.image.fill(pygame.Color(green))
        # self.rect = self.image.get_rect(center=(0, (grid_size + margin) // 2))
        self.pos = Vector2(0, (grid_size + margin) // 2)
        pos = round(self.pos.x), round(self.pos.y)
        (row, col) = get_grid(pos)
        e_path = enemy_path(board, (row, col))
        self.path = get_coord(e_path)
        self.path_index = 0
        self.target = self.path[self.path_index]
        self.max_hp = hp
        self.hp = hp
        self.ms = ms
        self.remove = False
        self.defeated = False

    def __str__(self):
        raise NotImplementedError

    def update_path(self, board):
        pos = round(self.pos.x), round(self.pos.y)
        (row, col) = get_grid(pos)
        e_path = enemy_path(board, (row, col))
        self.path = get_coord(e_path)

    def update(self):
        # A vector pointing from self to the target.
        heading = self.target - self.pos
        distance = heading.length()  # Distance to the target.
        try:
            heading.normalize_ip()  # length 1 vec
        except ValueError:
            pass
        if distance < self.ms:
            if self.path_index < len(self.path):
                # print(self.path_index, len(self.path))
                self.target = self.path[self.path_index]
                self.path_index += 1
            # otherwise enemy reach dest
            else:
                self.remove = True

        self.pos += heading * self.ms
        # self.pos.x, self.pos.y = round(self.pos.x), round(self.pos.y)
        self.rect.center = self.pos

    def lose_hp(self, i: int):
        self.hp -= i
        if self.hp <= 0:
            self.defeated = True

    def flag_defeat(self):
        self.defeated = True

    def distance_to_port(self):
        i = self.path_index
        d = (self.pos - self.target).length()
        while i < len(self.path) - 1:
            d += (Vector2(self.path[i]) - Vector2(self.path[i + 1])).length()
            i += 1
        return d


class Circle(Enemy):

    def __init__(self, hp, ms, board):
        super().__init__(hp, ms, board)
        self.image = pygame.Surface((ENEMY_IMG_SIZE, ENEMY_IMG_SIZE),
                                    pygame.SRCALPHA)
        pygame.gfxdraw.aacircle(self.image,
                                ENEMY_IMG_SIZE // 2,
                                ENEMY_IMG_SIZE // 2,
                                ENEMY_IMG_SIZE // 2 - 1, (0, 255, 0))
        pygame.gfxdraw.filled_circle(self.image,
                                     ENEMY_IMG_SIZE // 2,
                                     ENEMY_IMG_SIZE // 2,
                                     ENEMY_IMG_SIZE // 2 - 1, (0, 255, 0))
        self.rect = self.image.get_rect(center=(0, (grid_size + margin) // 2))

    def __str__(self):
        return 'Circle'


class Square(Enemy):

    def __init__(self, hp, ms, board):
        super().__init__(hp, ms, board)
        self.image = pygame.Surface((ENEMY_IMG_SIZE, ENEMY_IMG_SIZE))
        self.image.fill(pygame.Color(green))
        self.rect = self.image.get_rect(center=(0, (grid_size + margin) // 2))

    def __str__(self):
        return 'Square'


class Bullet(pygame.sprite.Sprite):
    """
    Bullet class

    === Public Attributes ===
    pos: position of the bullet
    bs: bullet speed
    target: target the bullet is targeting on
    """
    pos: Vector2
    dmg: int
    bs: int
    color: Tuple[int, int, int]
    target: Enemy
    remove: bool

    def __init__(self, pos, dmg, bs, color, target):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE),
                                    pygame.SRCALPHA)
        pygame.gfxdraw.aacircle(self.image,
                                BULLET_SIZE // 2,
                                BULLET_SIZE // 2,
                                BULLET_SIZE // 2 - 1, color)
        pygame.gfxdraw.filled_circle(self.image,
                                     BULLET_SIZE // 2,
                                     BULLET_SIZE // 2,
                                     BULLET_SIZE // 2 - 2, color)
        self.rect = self.image.get_rect(center=pos)
        self.pos = Vector2(pos)
        self.dmg = dmg
        self.bs = bs
        self.target = target
        self.remove = False

    def update(self):
        if self.target.remove:
            self.remove = True
            return

        heading = self.target.pos - self.pos
        distance = heading.length()  # Distance to the target.
        if distance < self.bs:
            self.target.lose_hp(self.dmg)
            self.remove = True
        else:
            heading.normalize_ip()
            self.pos += heading * self.bs
            self.rect.center = self.pos


class Tower:
    """
    Tower class

    === Public Attributes ===
    atk: attack of the tower
    atk_range: attack range of the tower
    atk_interval: the time period between towers two attacks
    level: level of the tower
    pos: position
    """
    atk: int
    atk_range: int
    atk_interval: float
    pos: Tuple[int, int]
    level: int
    cool_down: int
    target: Union[Optional[Enemy], bool]
    bullets: pygame.sprite.Group

    def __init__(self):
        """Tower_attr: attributes of tower."""
        self.pos = (0, 0)
        self.level = 1
        self.cool_down = 0
        self.target = None
        self.bullets = pygame.sprite.Group()

    def __str__(self):
        raise NotImplementedError

    def upgrade_tower(self):
        if self.level < TOWER_MAX_LVL:
            self.level += 1
        self.atk, self.atk_range = TOWER_ATTR_DICT[str(self)]

    def set_target(self, e_list: pygame.sprite.Group) -> bool:
        enemy_in_range = []
        for e in e_list:
            heading = e.pos - self.pos
            distance = heading.length()
            if distance <= self.atk_range:
                enemy_in_range.append(e)

        if not enemy_in_range:
            return False

        shortest = None
        enemy_ = None
        for i in enemy_in_range:
            dist = i.distance_to_port()
            if shortest is None:
                shortest = dist
                enemy_ = i
            elif dist < shortest:  # new find
                shortest = dist
                enemy_ = i

        self.target = enemy_
        return True

    def update_bullets(self):
        raise NotImplementedError

    def attack_enemy(self, e_list: pygame.sprite.Group):
        raise NotImplementedError

    def draw_aim_line(self):
        raise NotImplementedError

    def on_cool_down(self):
        if self.cool_down > 0:
            self.cool_down -= 1


class Cannon(Tower):

    def __init__(self):
        super().__init__()
        self.atk, self.atk_range = TOWER_ATTR_DICT[str(self)]
        self.atk_interval = CANNON_ATK_INT

    def __str__(self):
        return f'Cannon{self.level}'

    def update_bullets(self):
        self.bullets.update()
        for b in self.bullets:
            if b.remove:
                self.bullets.remove(b)
        self.bullets.draw(screen)

    def attack_enemy(self, e_list: pygame.sprite.Group):
        if self.cool_down > 0:
            if SHOW_AIM_LINE:
                self.set_target(e_list)
            return

        if not self.target:  # self target is None
            if not self.set_target(e_list):  # not new target
                return
        # has a target
        if self.target.remove or self.target.defeated:
            # self.bullets.remove(self.target)
            self.target = None
            if not self.set_target(e_list):
                return

        bullet = Bullet(self.pos, self.atk, CANNON_BS,
                        get_tower_color(self), self.target)
        self.bullets.add(bullet)
        self.cool_down = CANNON_ATK_INT

    def draw_aim_line(self):
        if self.target:
            if self.target.remove or self.target.defeated:
                return
            pygame.gfxdraw.line(screen, self.pos[0], self.pos[1],
                                round(self.target.pos[0]),
                                round(self.target.pos[1]), red)


class Sniper(Tower):

    def __init__(self):
        super().__init__()
        self.atk, self.atk_range = TOWER_ATTR_DICT[str(self)]
        self.atk_interval = SNIPER_ATK_INT

    def __str__(self):
        return f'Sniper{self.level}'

    def update_bullets(self):
        self.bullets.update()
        for b in self.bullets:
            if b.remove:
                self.bullets.remove(b)
        self.bullets.draw(screen)

    def attack_enemy(self, e_list: pygame.sprite.Group):
        if self.cool_down > 0:
            if SHOW_AIM_LINE:
                self.set_target(e_list)
            return

        if not self.target:  # self target is None
            if not self.set_target(e_list):  # not new target
                return
        # has a target
        if self.target.remove or self.target.defeated:
            # self.bullets.remove(self.target)
            self.target = None
            if not self.set_target(e_list):
                return

        atk = self.atk
        if isinstance(self.target, Square):
            atk = self.atk * 1.5
        bullet = Bullet(self.pos, atk, CANNON_BS,
                        get_tower_color(self), self.target)
        self.bullets.add(bullet)
        self.cool_down = SNIPER_ATK_INT

    def draw_aim_line(self):
        if self.target:
            if self.target.remove or self.target.defeated:
                return
            pygame.gfxdraw.line(screen, self.pos[0], self.pos[1],
                                round(self.target.pos[0]),
                                round(self.target.pos[1]), red)


class Crusher(Tower):

    def __init__(self):
        super().__init__()
        self.atk, self.atk_range = TOWER_ATTR_DICT[str(self)]
        self.atk_interval = CRUSHER_ATK_INT

    def __str__(self):
        return f'Crusher{self.level}'

    def set_target(self, e_list: pygame.sprite.Group):
        pass

    def update_bullets(self):
        pass

    def attack_enemy(self, e_list: pygame.sprite.Group):
        attacked = False
        if self.cool_down == 0:
            for e in e_list:
                heading = e.pos - self.pos
                distance = heading.length()
                if distance <= self.atk_range:
                    attacked = True
                    e.hp -= self.atk
                    if e.hp <= 0:
                        e.defeated = True

        if attacked:
            pygame.gfxdraw.aacircle(screen, self.pos[0], self.pos[1],
                                    self.atk_range, get_tower_color(self))
            self.cool_down = CRUSHER_ATK_INT

    def draw_aim_line(self):
        pass


AVAIL_TOWER_LST = [Cannon, Sniper, Crusher]
AVAIL_SLOTS_NUM = 2
AVAIL_ENEMY_LST = [Circle, Square]
ENEMY_STR_DICT = {
    Circle: 'Circle',
    Square: 'Square'
}


class Game:
    """
    === Public Attributes ===
    board: board in list form, show positions of towers
    path: path of enemy
    enemy_list: list of enemies, sorted in the order of distance travelled
    score: score gained in this game
    """
    board: List[List[Union[Tower, None]]]
    path: List[Tuple[int, int]]
    enemy_list: pygame.sprite.Group()
    new_enemy_list: List[str]
    port_hp: int
    score: int
    score_multiplier: float
    enemy_wave: int
    enemy_types: int
    enemy_num: int
    wave_info: Dict[str, int]

    def __init__(self):
        self.board = list_deep_copy()
        self.path = enemy_path(self.board)
        self.enemy_list = pygame.sprite.Group()
        self.new_enemy_list = []
        self.port_hp = INIT_PORT_HP
        self.score = 0
        self.score_multiplier = 1.00
        self.enemy_wave = 1
        self.enemy_types = 1
        self.enemy_num = 10
        self.wave_info = {}
        for e in ENEMY_STR_DICT.values():
            self.wave_info[e] = 0

    def __str__(self):
        s = ''
        for row in self.board:
            row_str = ''
            for col in row:
                if isinstance(col, Tower):
                    row_str += f'{col.level} '
                else:
                    row_str += '  '
            s += row_str + '\n'
        return s

    def update_all_towers(self):
        """Enemy list will be updated first"""
        for row in self.board:
            for tw in row:
                if isinstance(tw, Tower):
                    tw.attack_enemy(self.enemy_list)
                    tw.update_bullets()
                    tw.on_cool_down()

    def display_aim_line_pygame(self, show_aim_line=SHOW_AIM_LINE):
        if show_aim_line:
            for row in self.board:
                for tw in row:
                    if isinstance(tw, Tower):
                        tw.draw_aim_line()

    def gen_random_enemies(self):
        if self.enemy_wave < 5:
            self.wave_info['Circle'] = self.enemy_num
            self.new_enemy_list = \
                ['Circle' for _ in range(self.enemy_num)]

        # elif self.enemy_wave < 16:
        else:
            square_num = self.enemy_num // 2
            self.wave_info['Square'] = square_num
            rest = self.enemy_num - square_num
            temp = ['Square' for _ in range(square_num)]
            lst_no_square = AVAIL_ENEMY_LST[:]
            lst_no_square.remove(Square)
            random_type = random.choice(lst_no_square)
            type_str = ENEMY_STR_DICT[random_type]
            self.wave_info[type_str] = rest
            self.new_enemy_list = \
                temp + [type_str for _ in range(rest)]

    def spawn_time_based(self) -> bool:
        try:
            type_str = self.new_enemy_list.pop()
            hp = round(ENEMY_ATTR_DICT[type_str][0] * self.score_multiplier, 1)
            ms = ENEMY_ATTR_DICT[type_str][1]
            if type_str == 'Circle':
                new_enemy = Circle(hp, ms, self.board)
                self.add_enemy(new_enemy)
            if type_str == 'Square':
                new_enemy = Square(hp, ms, self.board)
                self.add_enemy(new_enemy)
            return True
        except IndexError:
            return False

    def add_enemy(self, e: Enemy):
        self.enemy_list.add(e)

    def remove_enemy(self):
        for e in self.enemy_list:
            if e.defeated:
                self.score += DEFEAT_ENEMY_SCORE * self.score_multiplier
                self.enemy_list.remove(e)
            elif e.remove:
                self.port_hp -= 1
                self.enemy_list.remove(e)

    def draw_enemy_hp_bar(self):
        for e in self.enemy_list:
            ex, ey = e.pos.x, e.pos.y
            ex -= ENEMY_IMG_SIZE // 2
            ey -= HP_BAR_ABOVE_ENEMY_CENTER
            pygame.draw.rect(screen, red,
                             pygame.Rect(ex, ey, ENEMY_IMG_SIZE,
                                         HP_BAR_THICKNESS))

            # display losed hp bar
            if e.max_hp != e.hp:
                hp_bar_deducted_percentage = (e.max_hp - e.hp) / e.max_hp
                hp_bar_deducted_length = \
                    round(hp_bar_deducted_percentage * ENEMY_IMG_SIZE)

                ex += HP_BAR_BORDER + ENEMY_IMG_SIZE - hp_bar_deducted_length
                ey += HP_BAR_BORDER
                width = hp_bar_deducted_length - HP_BAR_BORDER * 2
                height = HP_BAR_THICKNESS - HP_BAR_BORDER * 2
                pygame.draw.rect(screen, white,
                                 pygame.Rect(ex, ey, width, height))

    def update_enemy_pygame(self):
        self.enemy_list.update()
        self.remove_enemy()
        self.draw_enemy_hp_bar()
        self.enemy_list.draw(screen)

    def next_wave(self):
        self.enemy_wave += 1
        self.score_multiplier = self.score_multiplier + 0.1
        self.score += 100
        self.enemy_types = min(2, 1 + self.enemy_wave // 5)
        self.enemy_num = min(40, 10 + self.enemy_wave // 5 * 2)
        self.wave_info = {}
        self.gen_random_enemies()

    def game_update_enemy_path(self):
        for e in self.enemy_list:
            e.path_index = 1
            e.update_path(self.board)

    def add_score(self, s: int):
        self.score += s

    def _remove_tower(self, pos: Tuple[int, int]) -> bool:
        """Return True if a tower is removed at position, replaced with None
        if tower does not exist on pos, return False.
        """
        if self.board[pos[0]][pos[1]] is None:
            return False
        if isinstance(self.board[pos[0]][pos[1]], Tower):
            self.board[pos[0]][pos[1]] = None
            return True

    def place_tower(self, tower: Tower, pos: Tuple[int, int]) -> bool:
        """Place a tower at pos.
        Return False if:
        - pos is not valid
        - a tower is already placed on pos
        - cannot find the path if the tower was placed (check if towers
        merge first)
        - (an enemy is on the curr pos, NEED TO IMPLEMENT FOR PYGAME)

        Upon returning True, update self.path if the tower is placed on current
        path
        -
        """
        if pos == (0, 0) or pos == (BOARD_SIZE - 1, BOARD_SIZE - 1):
            return False
        if isinstance(self.board[pos[0]][pos[1]], Tower):
            # a tower already placed here
            return False

        # need to find another path
        # create a deep copy of self.board
        board_copy = list_deep_copy(self.board)
        can_be_merged = check_merge_tower(board_copy, tower, pos)
        # print(can_be_merged)
        if can_be_merged:
            path = enemy_path(board_copy)
            if path:  # path available after merge
                self.path = path
                # Mutate self.board
                self.board = board_copy
                tower.pos = get_coord([pos])[0]
                return True

        # can not be merged
        # do not change path if tower isn't placed on current path,
        # return immediately
        if pos not in self.path:
            self.board[pos[0]][pos[1]] = tower
            tower.pos = get_coord([pos])[0]
            return True

        # need a new copy in case mutated
        board_copy1 = list_deep_copy(self.board)
        board_copy1[pos[0]][pos[1]] = tower
        path = enemy_path(board_copy1)
        if path:  # return value is not an empty list
            self.path = path
            self.board[pos[0]][pos[1]] = tower
            tower.pos = get_coord([pos])[0]
            return True
        else:
            return False

    def print_path(self) -> str:
        lst = list_deep_copy(self.board)
        for p in self.path:
            lst[p[0]][p[1]] = '.'

        s = ''
        for row in lst:
            row_str = ''
            for col in row:
                if isinstance(col, Tower):
                    row_str += f'{col.level} '
                elif col == '.':
                    row_str += '. '
                else:
                    row_str += '  '
            s += row_str + '\n'
        return s


def get_tower_color(tower: Optional[Tower]) -> Tuple[int, int, int]:
    if tower is None:
        return 255, 255, 255
    elif isinstance(tower, Cannon):
        return 45, 179, 98
    elif isinstance(tower, Sniper):
        return 210, 240, 79
    elif isinstance(tower, Crusher):
        return 168, 101, 201


def enemy_path(board, pos=(0, 0), visited=None) -> List[Tuple[int, int]]:
    """Find an enemy path using DFS method
    """
    if visited is None:
        visited = set()
    if pos in visited:
        return []
    if pos == (BOARD_SIZE - 1, BOARD_SIZE - 1):
        return [pos]

    visited.add(pos)
    extensions = next_move_extensions(pos, board)
    # print(pos, extensions, visited)
    for ext in extensions:  # ext is a position
        if ext not in visited:
            temp = enemy_path(board, ext, visited)
            if temp:
                return [pos] + temp
            visited.add(ext)

    return []


def next_move_extensions(pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
    """ Return a list containing all possible move extensions
    """
    row = pos[0]
    col = pos[1]
    assert 0 <= row < BOARD_SIZE
    assert 0 <= col < BOARD_SIZE

    lst = []
    # priority: right, down, left, up;
    # if the extension is a tower, do not append
    if col < BOARD_SIZE - 1 and not isinstance(board[row][col + 1], Tower):
        lst.append((row, col + 1))
    if row < BOARD_SIZE - 1 and not isinstance(board[row + 1][col], Tower):
        lst.append((row + 1, col))
    if col > 0 and not isinstance(board[row][col - 1], Tower):
        lst.append((row, col - 1))
    if row > 0 and not isinstance(board[row - 1][col], Tower):
        lst.append((row - 1, col))

    return lst


def check_merge_tower(board: List[list], tower: Tower,
                      pos: Tuple[int, int], merged=False) -> bool:
    """Return True if tower can be merged to given location.
    Done recursively to upgrade the tower as high as possible
    """
    if tower.level == TOWER_MAX_LVL:
        return True
    row, col = pos[0], pos[1]
    left_most = max(0, col - 2)
    right_most = min(BOARD_SIZE - 1, col + 2)
    upper_most = max(0, row - 2)
    lower_most = min(BOARD_SIZE - 1, row + 2)

    tower_type = type(tower)
    tower_lvl = tower.level
    count = 0
    for tower_same_row in range(left_most, right_most + 1):
        curr_tower = board[row][tower_same_row]
        if tower_same_row == col:  # pass for pos
            count += 1
        elif type(curr_tower) == tower_type and \
                curr_tower.level == tower_lvl:
            count += 1
        else:
            count = 0
        if count == 3:
            merged = True
            board[row][tower_same_row] = None
            board[row][tower_same_row - 1] = None
            board[row][tower_same_row - 2] = None
            tower.upgrade_tower()
            board[row][col] = tower
            return check_merge_tower(board, tower, pos, merged)

    for tower_same_col in range(upper_most, lower_most + 1):
        curr_tower = board[tower_same_col][col]
        if tower_same_col == row:  # pass for pos
            count += 1
        elif type(curr_tower) == tower_type and \
                curr_tower.level == tower_lvl:
            count += 1
        else:
            count = 0
        if count == 3:
            merged = True
            board[tower_same_col][col] = None
            board[tower_same_col - 1][col] = None
            board[tower_same_col - 2][col] = None
            tower.upgrade_tower()
            board[row][col] = tower
            return check_merge_tower(board, tower, pos, merged)

    return merged


def list_deep_copy(lst=None) -> List[List]:
    """If no arg passed in, create a empty list of size BOARD_SIZE"""
    board = []
    if not lst:
        for row in range(BOARD_SIZE):
            board.append([None for col in range(BOARD_SIZE)])
    else:
        for row in lst:
            board.append([col for col in row])

    return board


# if __name__ == '__main__':
#     print(1)
#     BOARD_SIZE = 6
#     g = Game()
#     print(g.print_path())
#
#     g.place_tower(Sniper(), (0, 5))
#     g.place_tower(Sniper(), (1, 3))
#     g.place_tower(Sniper(), (1, 4))
#     g.place_tower(Sniper(), (1, 5))
#     print(g.print_path())
#
#     pygame.init()
#
#     c1 = Circle(g.board)
#     enemy_group = pygame.sprite.Group()
#     enemy_group.add(c1)
#
#     screen = pygame.display.set_mode([WIDTH, HEIGHT])
#     screen.fill((0, 75, 100))
#
#     running = True
#     while running:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#
#         screen.fill((0, 75, 100))
#         enemy_group.update()
#         enemy_group.draw(screen)
#         print(c1.pos)
#
#         pygame.display.update()
#         fpsClock.tick(FPS)
#
#     pygame.quit()



