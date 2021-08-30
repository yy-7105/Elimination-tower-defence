import pygame
# import cProfile
import pygame.gfxdraw
from config import *
from tower_defence import *
from pygame.locals import (MOUSEBUTTONUP,
                           MOUSEBUTTONDOWN,
                           KEYDOWN,
                           K_r,
                           QUIT)
from typing import List, Tuple, Optional
import random

# don't change, haven't updated yet
DEVELOPER_MODE = 0  # if developer_mode is 1, all towers spawns are snipers


def gen_text_window(text, font_size, centered_pos, font_color, bg_color):
    font = pygame.font.SysFont('calibri', font_size)
    text = font.render(text, True, font_color, bg_color)
    textrect = text.get_rect()
    textrect.center = centered_pos
    screen.blit(text, textrect)


def gen_text_window_left_align(text, font_size, topleft, font_color, bg_color,
                               textrect_info_only=False):
    font = pygame.font.SysFont('calibri', font_size)
    text = font.render(text, True, font_color, bg_color)
    textrect = text.get_rect()
    if textrect_info_only:
        return textrect.width, textrect.height
    textrect.topleft = topleft
    screen.blit(text, textrect)


def tower_options(lst, num_tower=AVAIL_SLOTS_NUM) -> List[Tower]:
    if DEVELOPER_MODE == 1:
        s1 = Sniper()
        s2 = Sniper()
        s3 = Sniper()
        s2.upgrade_tower()
        s3.upgrade_tower()
        s3.upgrade_tower()
        return [s1, s2, s3][:num_tower]

    r_lst = []  # return lst
    lst_copy = lst[:]
    len_ = len(lst) - 1
    for t in range(num_tower):
        index_ = random.randint(0, len_)
        tower = lst_copy.pop(index_)()  # Tower obj
        r_lst.append(tower)
        len_ -= 1

    return r_lst


def render_board(lst: List[List[Optional[Tower]]],
                 pos: Tuple[int, int]):
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            bg_color = get_tower_color(lst[y][x])
            pygame.draw.rect(screen, bg_color,
                             pygame.Rect(margin + grid_size * x,
                                         margin + grid_size * y,
                                         grid_size - margin,
                                         grid_size - margin))
            if lst[y][x] is not None:
                center = (margin + grid_size * x + (grid_size - margin) // 2,
                          margin + grid_size * y + (grid_size - margin) // 2)
                gen_text_window(str(lst[y][x]), tower_font_size,
                                center, black, bg_color)

    if pos is not None:
        x, y = pos[1], pos[0]
        bg_color = get_tower_color(lst[y][x])
        pygame.draw.rect(screen, lighter_green,
                         pygame.Rect(grid_size * x,
                                     grid_size * y,
                                     grid_size + margin,
                                     grid_size + margin))
        pygame.draw.rect(screen, bg_color,
                         pygame.Rect(margin + grid_size * x,
                                     margin + grid_size * y,
                                     grid_size - margin,
                                     grid_size - margin))

        if lst[y][x] is not None:
            center = (margin + grid_size * x + (grid_size - margin) // 2,
                      margin + grid_size * y + (grid_size - margin) // 2)
            tower = lst[y][x]
            gen_text_window(str(tower), tower_font_size,
                            center, black, bg_color)
            pygame.gfxdraw.aacircle(screen, center[0], center[1],
                                    tower.atk_range, ATK_RANGE_COLOR)
            # pygame.gfxdraw.aacircle(screen, center[0], center[1],
            #                         tower.atk_range - 1, ATK_RANGE_COLOR)


def get_grid(pos):
    """Get pos on lst from mouse position.
    """
    x, y = pos[0], pos[1]
    row, col = y // grid_size, x // grid_size  # row and col in lst
    # print(row, col)

    return row, col


def within_square(pos: Tuple[int, int], pos_rect: Tuple[int, int],
                  width: int, height: int) -> bool:
    x, y = pos[0], pos[1]
    rect_x, rect_y = pos_rect[0], pos_rect[1]
    return (rect_x <= x <= rect_x + width) and (rect_y <= y <= rect_y + height)


slots_sep = 20
slots_distance = int((WIDTH - HEIGHT - slots_sep) // 3)
slot_width = slots_distance - slots_sep
slot_height = slot_width
slots_init_x = HEIGHT + slots_sep
slots_y = HEIGHT - slots_sep - 5 - slot_height

slot1_pos = (slots_init_x, slots_y)
slot2_pos = (slots_init_x + slots_distance, slots_y)
slot3_pos = (slots_init_x + slots_distance * 2, slots_y)
slots_lst = [slot1_pos, slot2_pos, slot3_pos]


def display_slots(tower_slot_lst):
    for i in range(AVAIL_SLOTS_NUM):
        curr_slot = slots_lst[i]
        tower = tower_slot_lst[i]
        bg_color = get_tower_color(tower)
        pygame.draw.rect(screen, bg_color,
                         pygame.Rect(curr_slot[0],
                                     curr_slot[1],
                                     slot_width,
                                     slot_height))
        center = (curr_slot[0] + slot_width // 2,
                  curr_slot[1] + slot_height // 2)
        gen_text_window(str(tower), slot_font_size,
                        center, black, bg_color)


def display_enemy_path(path_lst: List[Tuple[int, int]]):
    for pos in path_lst:
        x, y = pos[1], pos[0]
        center = (margin + grid_size * x + (grid_size - margin) // 2,
                  margin + grid_size * y + (grid_size - margin) // 2)
        gen_text_window('.', path_dot_size,
                        center, light_grey, white)


def select_slot(tower_lst: List[Tower], pos_on_lst, pos) -> Optional[Tower]:
    if pos_on_lst is None:
        return None
    # pos_on_lst is not None
    for i in range(AVAIL_SLOTS_NUM):
        if within_square(pos, slots_lst[i], slot_width, slot_height):
            return tower_lst[i]


def display_game_text(g: Game):
    wave_loc = (HEIGHT + 10, 10)
    score_loc = (HEIGHT + 10, 70)
    multiplier_loc = (HEIGHT + 10, 100)
    hp_loc = (HEIGHT + 10, 130)

    remaining_tower_num_loc = (HEIGHT + 10, slots_y - 35)

    gen_text_window_left_align(f'Wave {g.enemy_wave}', 30, wave_loc,
                               white, (0, 75, 100))
    gen_text_window_left_align(f'Score: {round(g.score)}', 30, score_loc,
                               white, (0, 75, 100))
    gen_text_window_left_align(f'Multiplier: {round(g.score_multiplier, 2)}',
                               18, multiplier_loc, white, (0, 75, 100))
    gen_text_window_left_align(f'HP: {g.port_hp}', 30, hp_loc,
                               lighter_green, (0, 75, 100))
    gen_text_window_left_align(f'{g.remaining_tower_to_place} '
                               f'towers can be placed', 22,
                               remaining_tower_num_loc,
                               white, (0, 75, 100))

    wave_info_x, wave_info_y = HEIGHT + 10, 310
    gen_text_window_left_align(f'Next wave:', 30, (wave_info_x, wave_info_y),
                               white, (0, 75, 100))
    wave_info_y += 30
    for i in g.wave_info:
        if g.wave_info[i] != 0:
            gen_text_window_left_align(f'{str(i)}: {g.wave_info[i]}', 20,
                                       (wave_info_x, wave_info_y),
                                       white, (0, 75, 100))
            wave_info_y += 20


def display_tower_info(t: Tower):
    name_loc = (HEIGHT + 10, 175)
    gen_text_window_left_align(f'{str(t)}', 30, name_loc,
                               white, (0, 75, 100))

    tw_atk_loc = (HEIGHT + 10, 210)
    tw_range_loc = (HEIGHT + 10, 232)
    tw_int_loc = (HEIGHT + 10, 254)
    gen_text_window_left_align(f'ATK: {t.atk}', 20, tw_atk_loc,
                               white, (0, 75, 100))
    gen_text_window_left_align(f'range: {t.atk_range}', 20, tw_range_loc,
                               white, (0, 75, 100))
    gen_text_window_left_align(f'interval: {t.atk_interval}s', 20, tw_int_loc,
                               white, (0, 75, 100))


def display_game_over():
    gen_text_window(f'You Lose', 120, (HEIGHT // 2, HEIGHT // 2),
                    white, black)


def check_click_go_next_wave(pos, topleft, size, count: int) -> int:
    if count > 0:
        width = size[0]
        height = size[1]
        left = topleft[0]
        top = topleft[1]
        x = pos[0]
        y = pos[1]
        if left <= x <= left + width and top < y < top + height:
            return 0

    return count


g = Game()
g.gen_random_enemies()  # generate for the first wave
# text, position
pygame.init()

skip_font_size = 25
skip_waiting_topleft = (HEIGHT + 120, 35)
skip_waiting_size = gen_text_window_left_align('Go!', skip_font_size,
                                               skip_waiting_topleft,
                                               white, green,
                                               textrect_info_only=True)

screen.fill((0, 75, 100))
tower_in_slot = tower_options(AVAIL_TOWER_LST)

running = True
pos_selected = None
wave_wait_time = 1000
spawn = False
game_over = False
next_level = 1
counter = WAVE_DELAY // 1000

SPAWN_ENEMY = pygame.USEREVENT + 1
NEXT_WAVE = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_ENEMY, ENEMY_SPAWN_INTERVAL)
pygame.time.set_timer(NEXT_WAVE, wave_wait_time)

while running:
    screen.fill((0, 75, 100))
    render_board(g.board, pos_selected)  # render the game board
    display_slots(tower_in_slot)  # display towers on the slots on the right
    display_enemy_path(g.path)  # display enemy path

    g.update_enemy_pygame()
    g.update_all_towers()
    g.display_aim_line_pygame()
    display_game_text(g)

    for event in pygame.event.get():

        if event.type == NEXT_WAVE:
            print(f'count_down: {counter}')
            if counter == 0:
                wave_wait_time = 0
                spawn = True
                next_level += 1
            else:
                counter -= 1
                spawn = False

        if event.type == SPAWN_ENEMY:
            if spawn:
                # print(1)
                if not g.spawn_time_based():
                    spawn = False
                next_level = g.enemy_wave + 1

        if event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            counter = check_click_go_next_wave(pos,
                                               skip_waiting_topleft,
                                               skip_waiting_size,
                                               counter)
            if pos[0] < HEIGHT - margin:  # guarantee x in g.board
                # x <= BOARD_SIZE * grid_size - margin - 1
                temp = get_grid(pos)
                # select twice ==> deselect
                if pos_selected == temp:
                    pos_selected = None
                # otherwise select
                else:
                    pos_selected = temp

            # select tower on slots, if none, return None
            # if no grid selected on the board, return None
            tower = select_slot(tower_in_slot, pos_selected, pos)
            if tower:
                if g.place_tower(tower, pos_selected):
                    g.game_update_enemy_path()
                    tower_in_slot = tower_options(AVAIL_TOWER_LST)
            print(pos_selected)

        if event.type == QUIT:
            running = False
    # show tower info if tower on the grid
    if pos_selected is not None:
        tw = g.board[pos_selected[0]][pos_selected[1]]
        if isinstance(tw, Tower):
            display_tower_info(tw)

    if g.port_hp <= 0:
        game_over = True
        running = False

    if len(g.enemy_list) == 0 and not spawn:
        if next_level != g.enemy_wave:
            wave_wait_time = 1000
            counter = WAVE_DELAY // 1000
            g.next_wave()

    # Wave text
    if counter > 0:
        gen_text_window_left_align(f'Next in: {counter}s', 20,
                                   (HEIGHT + 10, 40),
                                   white, (0, 75, 100))
        gen_text_window_left_align('Go!', skip_font_size,
                                   skip_waiting_topleft,
                                   white, indigo)

    fps = round(1000 / fpsClock.tick(FPS))
    gen_text_window_left_align(f'fps: {fps}', 30, (HEIGHT + 185, 10),
                               white, (0, 75, 100))
    pygame.display.update()


while game_over:
    display_game_over()
    fpsClock.tick(5)
    pygame.display.update()

pygame.quit()
