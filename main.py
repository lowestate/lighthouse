import math
import time
import sys
import pygame
import random
import json
import numpy as np
from consts import *
from start import *


class Square:
    def __init__(self, speed, oth_squares_coords) -> None:
        self.square = {
            'position': self.gen_spawn_points(oth_squares_coords), 
            'state': 'normal', 
            'start_time': 0, 
            'fade': 0, 
            'alpha': 0}
        self.speed = speed

    def gen_spawn_points(self, oth_squares_coords):
        center_x = screen_width // 2
        center_y = screen_height // 2
        radius = 800
        
        while True:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            distance_to_center = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)

            if distance_to_center > radius:
                if len(oth_squares_coords) == 0:
                    return (x, y)
                else:
                    if all(math.sqrt((x - coord[0]) ** 2 + (y - coord[1]) ** 2) >= 150 for coord in oth_squares_coords):
                        return (x, y)
             
    def upd_sq_pos(self):
        square_x, square_y = self.square['position']

        direction_x = (screen_width // 2) - square_x
        direction_y = (screen_height // 2) - square_y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

        if distance > 0:
            direction_x /= distance
            direction_y /= distance

        square_x += direction_x * self.speed
        square_y += direction_y * self.speed

        self.square['position'] = (square_x, square_y)

    def draw_square(self, current_time):
        square_x, square_y = self.square['position']
        distance_to_center = math.sqrt((square_x + SQ_SIZE // 2 - screen_width // 2) ** 2 + (square_y + SQ_SIZE // 2 - screen_height // 2) ** 2)  

        pygame.draw.rect(screen, BLUE, pygame.Rect(square_x, square_y, SQ_SIZE, SQ_SIZE))

        if distance_to_center < 400:
            if self.square['state'] == 'normal':
                self.square['state'] = 'hit'
                self.square['start_time'] = current_time
            if self.square['state'] == 'hit':
                elapsed_time = (current_time - self.square['start_time']) / 1000
                if elapsed_time < 1:
                    alpha = max(0, int(255 * (1 - elapsed_time)))
                    square_color = (255, 0, 0, alpha)
                    s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
                    s.fill(square_color)
                    screen.blit(s, (square_x, square_y))
                else:
                    self.square['state'] = 'normal'
            elif self.square['state'] == 'normal':
                pygame.draw.rect(screen, BLUE, pygame.Rect(square_x, square_y, SQ_SIZE, SQ_SIZE))

    def trigger_death_anim(self, current_time):
        self.square['state'] = 'death_anim'
        self.square['fade'] = current_time

    def update_fading_squares(self, fading_squares):
        current_time = pygame.time.get_ticks()

        for square in fading_squares:
            elapsed_time = (current_time - square.square['fade']) / 1000
            square_x, square_y = square.square['position']
            if elapsed_time < 1:
                alpha = max(0, int(255 * (1 - elapsed_time / 1)))
                square_color = (255, 255, 255, alpha)
                s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
                s.fill(square_color)
                screen.blit(s, (square_x, square_y))
            else:
                fading_squares.remove(square)   

    def check_loss(self, squares, island_circle):
        island_center, island_radius = island_circle
        for square in squares:
            square_x, square_y = square.square['position']
            square_center_x = square_x + SQ_SIZE / 2
            square_center_y = square_y + SQ_SIZE / 2

            distance = math.sqrt((square_center_x - island_center[0]) ** 2 + (square_center_y - island_center[1]) ** 2)
            if distance < island_radius + SQ_SIZE / 2:
                return True
        return False


class Circle:
    def __init__(self) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (screen_width // 2)
        dy = mouse_y - (screen_height // 2)
            
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length > 0:
            dx /= length
            dy /= length
                
        circle_x = screen_width // 2
        circle_y = screen_height // 2

        self.circle = (circle_x, circle_y, dx * CIRCLE_SPEED, dy * CIRCLE_SPEED)
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

    def draw_circles(self, circles):
        new_circles = []
        for circle in circles:

            circle_x, circle_y, dx, dy = circle

            circle_x += dx
            circle_y += dy

            if circle_x + CIRCLE_RAD > screen_width or circle_x - CIRCLE_RAD < 0 or circle_y + CIRCLE_RAD > screen_height or circle_y - CIRCLE_RAD < 0:
                continue    
            
            pygame.draw.circle(screen, CIRCLE_OUTLINES_COLOR, (int(circle_x), int(circle_y)), CIRCLE_RAD+3)
            pygame.draw.circle(screen, CIRCLE_COLOR, (int(circle_x), int(circle_y)), CIRCLE_RAD)

            new_circles.append((circle_x, circle_y, dx, dy))

        return new_circles


class Screen:
    def render_info(self, points, level, remaining_enemies):

        text_to_blit = { # [value, offset]
            'SCORE:  ': [points, 400],
            'LEVEL:  ': [level, 150], 
            'ENEMIES REMAIN:  ':  [remaining_enemies, -200]
        }
        
        for key in text_to_blit: 
            points_text = font.render(f"{key}{text_to_blit[key][0]}", True, (255, 255, 255))
            text_rect = points_text.get_rect(center=(screen_width // 2 - text_to_blit[key][1], 30))
            transparent_rect = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
            transparent_rect.fill((0, 0, 0, 0))
            screen.blit(transparent_rect, text_rect.topleft)
            screen.blit(points_text, text_rect.topleft)

    def endscreen(self, result, curr_level, score):
        victory_screen = pygame.Surface((screen_width, screen_height))
        victory_screen.fill((0, 0, 0))

        font = pygame.font.Font(None, 90)
        button_font = pygame.font.Font(None, 60)

        text = font.render(result, True, (255, 255, 255))     
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 4))

        if result == 'YOU LOST' or result == 'KRAKEN REACHED YOU':
            lost = True
        else:
            lost = False
        
        offset = 0
        if lost:
            offset = 150
            level_text = font.render('LEVELS COMPLETED: ' + str(curr_level-1), True, (255, 255, 255))
        else:
            level_text = font.render('NEXT LEVEL: ' + str(curr_level+1), True, (255, 255, 255))
            next_level_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2, 300, 100)
            next_level_text = button_font.render("NEXT LEVEL", True, (0, 0, 0))
            next_level_text_rect = next_level_text.get_rect(center=next_level_button.center)

        level_rect = level_text.get_rect(center=(screen_width // 2, screen_height // 4 + 100))

        score_text = font.render('SCORE: ' + str(score), True, (255, 255, 255))     
        score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 4 + 200))
          

        replay_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 150 - offset, 300, 100)
        replay_text = button_font.render("RESTART", True, (0, 0, 0))
        replay_text_rect = replay_text.get_rect(center=replay_button.center)

        quit_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 300 - offset, 300, 100)
        quit_text = button_font.render("QUIT", True, (0, 0, 0))
        quit_text_rect = quit_text.get_rect(center=quit_button.center)

        alpha = 0
        fade_duration = 1500  # in milliseconds
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()

        while True:
            elapsed_time = pygame.time.get_ticks() - start_time
            if elapsed_time < fade_duration:
                alpha = int((elapsed_time / fade_duration) * 255)
            else:
                alpha = 255

            l = [victory_screen, text, level_text, score_text, replay_text, quit_text]
            [elem.set_alpha(alpha) for elem in l]

            if not lost:
                next_level_text.set_alpha(alpha)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not lost and next_level_button.collidepoint(event.pos):
                        game(level=curr_level + 1, points=score)
                    if replay_button.collidepoint(event.pos):
                        game(level=1, points=0)
                    elif quit_button.collidepoint(event.pos):
                        game(level=0, points=0)

            victory_screen.fill((0, 0, 0))

            to_blit = [
                [text,text_rect], 
                [level_text, level_rect], 
                [score_text, score_rect]
            ]
            [victory_screen.blit(o[0], o[1]) for o in to_blit]
            
            if not lost:
                pygame.draw.rect(victory_screen, (255, 255, 255), next_level_button)
                victory_screen.blit(next_level_text, next_level_text_rect)

            pygame.draw.rect(victory_screen, (255, 255, 255), replay_button)
            victory_screen.blit(replay_text, replay_text_rect)

            pygame.draw.rect(victory_screen, (255, 255, 255), quit_button)
            victory_screen.blit(quit_text, quit_text_rect)

            screen.blit(victory_screen, (0, 0))
            pygame.display.flip()
            clock.tick(60)

    def level_screen(self):
        isl_img = objs['isl']['img']
        lh_img = objs['lh']['img']
        new_island_image = pygame.transform.scale(isl_img, (isl_img.get_width() * 1.3, isl_img.get_height() * 1.3))
        new_island_image_rect = new_island_image.get_rect()
        new_island_image_rect.center = (screen_width // 2, screen_height // 2)

        new_lh_image = pygame.transform.scale(lh_img, (lh_img.get_width() * 1.3, lh_img.get_height() * 1.3))
        new_lh_image_rect = new_lh_image.get_rect()
        new_lh_image_rect.center = (screen_width // 2, screen_height // 2)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or running == False):
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if new_island_image_rect.collidepoint(event.pos):
                        game(level=1, points=0)
                        
            screen.fill(BLUE)

            screen.blit(isl_img, objs['isl']['rect'])
            screen.blit(new_lh_image, new_lh_image_rect)
              
            screen.blit(beam_surface, (0, 0))
            
            pygame.display.flip()

    def startscreen(self):
        start_screen = pygame.Surface((screen_width, screen_height))
        start_screen.fill((0, 0, 0))

        logo_font = pygame.font.Font(None, 200)
        button_font = pygame.font.Font(None, 60)

        logo = logo_font.render('LIGHTHOUSE', True, (255, 255, 255))     
        logo_rect = logo.get_rect(center=(screen_width // 2, screen_height // 4))      

        play_button = pygame.Rect(screen_width // 2 - 200, screen_height // 2, 400, 100)
        play_text = button_font.render("ENDLESS MODE", True, (0, 0, 0))
        play_text_rect = play_text.get_rect(center=play_button.center)

        quit_button = pygame.Rect(screen_width // 2 - 200, screen_height // 2 + 150, 400, 100)
        quit_text = button_font.render("QUIT", True, (0, 0, 0))
        quit_text_rect = quit_text.get_rect(center=quit_button.center)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.collidepoint(event.pos):
                        game(level=1, points=0)
                    if quit_button.collidepoint(event.pos):
                        sys.exit()
                        
            start_screen.fill((0, 0, 0))

            start_screen.blit(logo, logo_rect)

            pygame.draw.rect(start_screen, (255, 255, 255), play_button)
            start_screen.blit(play_text, play_text_rect)

            pygame.draw.rect(start_screen, (255, 255, 255), quit_button)
            start_screen.blit(quit_text, quit_text_rect)

            screen.blit(start_screen, (0, 0))
            pygame.display.flip()
    
    def debug_info(tentacles):
        positions = ['LT', 'LM', 'LB', 'RT', 'RM', 'RB']  # Позиции меток
        for i, t in enumerate(tentacles):
            if 'hp' in t:
                label = positions[i % len(positions)]  # Определение метки
                points_text = font.render(f"{label}: {t['hp']}, {t['sprite']['rect'].x}, {t['sprite']['rect'].y}", True, (255, 255, 255))
                text_rect = points_text.get_rect(topright=(screen_width - 10, 20 + i * 30))
                transparent_rect = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
                transparent_rect.fill((0, 0, 0, 0))
                screen.blit(transparent_rect, text_rect.topleft)
                screen.blit(points_text, text_rect.topleft)


class Raindrop:
    def __init__(self):
        self.size = random.choices(RAINDROP_SIZES, RAINDROP_PROBABILITIES)[0]
        self.x = random.randint(0, screen_width)
        self.y = random.randint(0, screen_height)
        self.start_time = time.time()
        self.alpha = 255

    def update(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0.5:
            self.alpha = max(0, 255 - int((elapsed_time - 0.5) * 510))
        if self.alpha == 0:
            return False
        return True

    def draw(self, surface):
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        s.fill((*RAIN_COLOR, self.alpha))
        surface.blit(s, (self.x, self.y))


class Boss:
    def __init__(self) -> None:
        # Инициализация свойств для всех элементов tentacles
        tentacle_props = []
        for key in ["lt", "lm", "lb", "rt", "rm", "rb"]:
            tentacle_props.append(objs[key])

        self.tentacles = []
        for tentacle_sf in tentacle_props:
            self.tentacles.append({
                'hp': 4,
                'sprite': tentacle_sf,
                'appear_start_time': 0,
                'death_start_time': 0,
                'last_hit_time': 0,
            })
        
        self.pair_lt_rb = [0, 5]
        self.pair_lm_rm = [1, 4]
        self.pair_lb_rt = [2, 3]

    def bossfight(self, stage, moved_l, moved_r, circles, level, score):
        if not moved_l:
            for i in range(3):
                self.tentacles[i]['sprite']['rect'].x -= self.tentacles[i]['sprite']['rect'].width
        if not moved_r:
            for i in range(3, 6):
                self.tentacles[i]['sprite']['rect'].x += screen_width

        if stage == 1 and moved_r and moved_l:
            if self.tentacles[0]['hp'] != 0 or self.tentacles[5]['hp'] != 0 or self.tentacles[0]['sprite']['sf'].get_alpha() != 0 or self.tentacles[5]['sprite']['sf'].get_alpha() != 0:
                pair_to_blit = self.pair_lt_rb
            elif self.tentacles[1]['hp'] != 0 or self.tentacles[4]['hp'] != 0 or self.tentacles[1]['sprite']['sf'].get_alpha() != 0 or self.tentacles[4]['sprite']['sf'].get_alpha() != 0:
                pair_to_blit = self.pair_lm_rm
            else:
                pair_to_blit = self.pair_lb_rt
            
            for t_n in pair_to_blit:
                for circle in circles:
                    circle_x, circle_y, dx, dy = circle

                    if pygame.time.get_ticks() - self.tentacles[t_n]['last_hit_time'] > 1000:
                        collision_lt, self.tentacles[t_n]['last_hit_time'] = check_collision_circle_surface((circle_x, circle_y), CIRCLE_RAD, self.tentacles[t_n]['sprite'])
                        if collision_lt  and self.tentacles[t_n]['hp'] > 0:
                            self.tentacles[t_n]['hp'] -= 1
                
                if self.tentacles[t_n]['hp'] > 0:
                    if t_n < 3:
                        if self.tentacles[t_n]['sprite']['rect'].x != 0:
                            self.tentacles[t_n]['sprite']['rect'].x += 1
                        else:
                            Screen.endscreen('KRAKEN REACHED YOU', level, score)
                    elif t_n > 2:
                        if self.tentacles[t_n]['sprite']['rect'].x != screen_width - self.tentacles[t_n]['sprite']['rect'].width:
                            self.tentacles[t_n]['sprite']['rect'].x -= 1
                        else:
                            Screen().endscreen('KRAKEN REACHED YOU', level, score)
                elif self.tentacles[t_n]['sprite']['sf'].get_alpha() > 0: 
                    change_sf_color(self.tentacles[t_n]['sprite']['sf'], (255, 255, 255, 255))
                    if self.tentacles[t_n]['sprite']['sf'].get_alpha() - 15 > 0:
                        self.tentacles[t_n]['sprite']['sf'].set_alpha(self.tentacles[t_n]['sprite']['sf'].get_alpha() - 15)
                    else: 
                        self.tentacles[t_n]['sprite']['sf'].set_alpha(0)

                if self.tentacles[t_n]['sprite']['sf'].get_alpha() > 0:
                    screen.blit(self.tentacles[t_n]['sprite']['sf'], self.tentacles[t_n]['sprite']['rect'])


def change_sf_color(surface, color):
    # Создание маски для непрозрачных частей
    mask = pygame.mask.from_surface(surface)

    # Создание нового слоя для покраски
    color_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    color_surface.fill(color)

    # Накладываем цвет только на непрозрачные пиксели
    for y in range(surface.get_height()):
        for x in range(surface.get_width()):
            if mask.get_at((x, y)) != 0:  # Проверка на непрозрачность
                surface.set_at((x, y), color_surface.get_at((x, y)))

def beam_corners(dx, dy, end_x, end_y):
    perpendicular_dx = -dy
    perpendicular_dy = dx

    # Нормализуем вектор
    perpendicular_length = math.sqrt(perpendicular_dx ** 2 + perpendicular_dy ** 2)
    if perpendicular_length > 0:
        perpendicular_dx /= perpendicular_length
        perpendicular_dy /= perpendicular_length

    # Умножаем нормализованный вектор на 100 пикселей
    perpendicular_dx *= 150 # 150 200 250
    perpendicular_dy *= 150

    # Вычисляем координаты вершины слева
    left_vertex_x = end_x + perpendicular_dx
    left_vertex_y = end_y + perpendicular_dy

    # Находим вектор, перпендикулярный лучу в его конце справа
    perpendicular_dx_right = dy
    perpendicular_dy_right = -dx

    # Нормализуем вектор
    perpendicular_length_right = math.sqrt(perpendicular_dx_right ** 2 + perpendicular_dy_right ** 2)
    if (perpendicular_length_right > 0):
        perpendicular_dx_right /= perpendicular_length_right
        perpendicular_dy_right /= perpendicular_length_right

    # Умножаем нормализованный вектор на 100 пикселей
    perpendicular_dx_right *= 150
    perpendicular_dy_right *= 150

    # Вычисляем координаты вершины справа
    right_vertex_x = end_x + perpendicular_dx_right
    right_vertex_y = end_y + perpendicular_dy_right

    return left_vertex_x, left_vertex_y, right_vertex_x, right_vertex_y

def point_inside_triangle(x, y, triangle):
    x1, y1 = triangle[0]
    x2, y2 = triangle[1]
    x3, y3 = triangle[2]

    # Вычисление площади треугольников ABC, ABD, ACD
    main_triangle_area = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
    triangle1_area = abs((x1 - x) * (y2 - y) - (x2 - x) * (y1 - y))
    triangle2_area = abs((x1 - x) * (y3 - y) - (x3 - x) * (y1 - y))
    triangle3_area = abs((x2 - x) * (y3 - y) - (x3 - x) * (y2 - y))

    # Если сумма площадей треугольников равна площади основного треугольника,
    # то точка находится внутри треугольника
    return main_triangle_area == triangle1_area + triangle2_area + triangle3_area

def check_collision(circles, squares, fading_squares, stats):
    for circle in circles:
        circle_x, circle_y, dx, dy = circle
        for square in squares:
            square_x, square_y = square.square['position']
            if (square_x <= circle_x <= square_x + 40) and (square_y <= circle_y <= square_y + 40):     
                stats['total_sqs_killed'] += 1
                save_stats(stats)
                square.trigger_death_anim(pygame.time.get_ticks())
                fading_squares.append(square)
                squares.remove(square) 

def check_collision_circle_surface(circle_pos, circle_radius, sprite):
    surface = sprite['sf']
    surface_rect = sprite['rect']
    collision_time = 0

    # Создание маски для поверхности
    mask = pygame.mask.from_surface(surface)

    # Создание маски для круга
    circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(circle_surface, (255, 255, 255), (circle_radius, circle_radius), circle_radius)
    circle_mask = pygame.mask.from_surface(circle_surface)

    # Позиция круга относительно поверхности
    offset = (circle_pos[0] - surface_rect.left - circle_radius, circle_pos[1] - surface_rect.top - circle_radius)

    # Проверка коллизии масок
    collision_point = mask.overlap(circle_mask, offset)

    if collision_point is not None:
        collision_time = pygame.time.get_ticks()

    return collision_point is not None, collision_time

def load_stats(filename='stats.json'):
    try:
        with open(filename, 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        stats = {'total_sqs_killed': 0}
    return stats

def save_stats(stats, filename='stats.json'):
    with open(filename, 'w') as f:
        json.dump(stats, f, indent=4)  

def game(level, points):
    if (level == 0):
        sys.exit()

    circles = []
    last_circle_spawn_time = 0
    spawn_delay = 1200 # 1.2 сек

    squares = []
    oth_sqs_coords = []
    SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, 1000)
    enemies_spawned = 0
    fading_squares = []
    n_enemies = level * 2
    speed = math.sqrt(level) / 2

    beam_state = 'normal'
    transparent_start = None
    min_alpha = 10
    max_alpha = 80
    max_odd = 120
    
    raindrops = []
    last_rain_time = 0

    boss = Boss()
    boss_preview = None
    scr_alpha = 255
    start_time = 0
    objs['preview']['sf'].set_alpha(0)
    boss_killed = False
    stage = 1
    moved_l = False
    moved_r = False

    running = True
    clock = pygame.time.Clock()

    squares.append(Square(speed, oth_sqs_coords))
    oth_sqs_coords.append(squares[0].square['position'])

    stats = load_stats()

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or running == False):
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_time - last_circle_spawn_time >= spawn_delay:
                    new_c = Circle()
                    circles.append(new_c.circle)
                    last_circle_spawn_time = current_time
            elif event.type == SPAWN_ENEMY_EVENT and enemies_spawned < n_enemies - 1:
                squares.append(Square(speed, oth_sqs_coords))
                oth_sqs_coords.append(squares[len(squares) - 1].square['position'])
                enemies_spawned += 1

        mouse_x, mouse_y = pygame.mouse.get_pos()

        dx = mouse_x - (screen_width // 2)
        dy = mouse_y - (screen_height // 2)
            
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length > 0:
            dx /= length
            dy /= length

        end_x = (screen_width // 2) + dx * BEAM_LENGTH
        end_y = (screen_height // 2) + dy * BEAM_LENGTH

        beam_surface.fill((0, 0, 0, 0))
            
        left_x, left_y, right_x, right_y = beam_corners(dx, dy, end_x, end_y)

        beam_triangle = [
            (left_x, left_y),    # вершина слева
            (right_x, right_y),  # вершина справа
            (screen_width // 2, screen_height // 2)  # вершина в центре
        ]

        if random.randint(0, max_odd) == 0 and beam_state == 'normal':
            beam_state = 'transparent'
            transparent_start = current_time

        if boss_preview:
            min_alpha = 0
        
        if beam_state == 'transparent':
            elapsed_time = (current_time - transparent_start) / 1000
            if elapsed_time < 0.2:
                beam_color = (245, 238, 119, min_alpha)
                if boss_preview:
                    if max_alpha - 1.5 > 0: 
                        max_alpha -= 1.5 
                    else: 
                        max_alpha = 0
                    max_odd = 30
            else:
                beam_state = 'normal'
                beam_color = (245, 238, 119, max_alpha)    
        else:
            beam_color = (245, 238, 119, max_alpha)

        if max_alpha != 0:
            pygame.draw.polygon(beam_surface, beam_color, beam_triangle)
            pygame.draw.line(beam_surface, beam_color, (screen_width // 2, screen_height // 2), (end_x, end_y), 5)
                    
            screen.blit(beam_surface, (0, 0))

        [sq.upd_sq_pos() for sq in squares]

        screen.fill(BLUE)

        objs_to_blit = [
            'preview',
            'isl',
            'lh',
            'lh_top'
        ]

        for key in objs_to_blit:
            obj = objs[key]
            blit_x = (screen_width - obj['rect'].width) // 2
            blit_y = (screen_height - obj['rect'].height) // 2
            if key == 'lh_top':
                screen.blit(beam_surface, (0,0))
            if (key == 'bg_isl' and obj['sf'].get_alpha() == 0) or (key == 'preview' and boss_preview == None):
                continue
            screen.blit(obj['sf'], (blit_x, blit_y))
        
        island_center = (objs['isl']['rect'].centerx, objs['isl']['rect'].centery)
        island_radius = min(objs['isl']['rect'].width, objs['isl']['rect'].height) // 4 - SQ_SIZE
        island_circle = (island_center, island_radius)

        if Square(speed, oth_sqs_coords).check_loss(squares, island_circle):
            Screen().endscreen("YOU LOST", level, points)

        [sq.draw_square(current_time) for sq in squares]

        Square(speed, oth_sqs_coords).update_fading_squares(fading_squares)

        n_sq = len(squares)

        check_collision(circles=circles, squares=squares, fading_squares=fading_squares, stats=stats)

        # если круг сбил квадрат то квадрат удаляется из массива => добавляем поинт если после проверки на столкновение квадратов оказалось меньше чем до проверки
        if len(squares) < n_sq:
            points+=1

        circles = Circle().draw_circles(circles)

        if boss_preview and objs['bg_isl']['sf'].get_alpha() > 0:
            objs['bg_isl']['sf'].set_alpha(objs['bg_isl']['sf'].get_alpha() - 1.5)        
        
        if objs['bg_isl']['sf'].get_alpha() > 0:
            screen.blit(objs['bg_isl']['sf'], (0, 0))

        # капли
        t_current_time = time.time()
        if t_current_time - last_rain_time >= 0.02:
            raindrops.append(Raindrop())
            last_rain_time = t_current_time

        raindrops = [drop for drop in raindrops if drop.update()]
        [drop.draw(screen) for drop in raindrops]          
    
        Screen().render_info(points, level, len(squares))

        # проверка len(f_s) нужна для того, чтобы экран победы запускался после последней анимации смерти врага, а не сразу же при его убийстве
        if (len(squares)==0 and points != 0 and len(fading_squares) == 0): 
            if (level==1 and boss_preview != False):
                boss_preview = True
                if max_alpha == 0:    
                    if start_time == 0:
                        start_time = pygame.time.get_ticks() 
                    elif pygame.time.get_ticks() - start_time > 2000:
                        scr_alpha = max(scr_alpha - 3, 0)
                        objs['preview']['sf'].set_alpha(scr_alpha)
                        if scr_alpha == 0:
                            boss_preview = False
                            objs['bg_isl']['sf'].set_alpha(255)
                            max_alpha = 80
                            min_alpha = 20
            elif not boss_killed:
                Screen.debug_info(boss.tentacles)
                boss.bossfight(stage, moved_l, moved_r, circles, level, points)
                moved_r = True
                moved_l = True
            else:
                Screen().endscreen("LEVEL COMPLETED", level, points)
                save_stats(stats)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    Screen().startscreen()