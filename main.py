import math
import time
import sys
import pygame
import random
from consts import *
from start import *


class Square:
    def __init__(self, speed, oth_squares_coords) -> None:
        self.square = {
            'position': self.gen_spawn_points(oth_squares_coords), 
            'state': 'normal', 
            'start_time': 0, 
            'fade': 0, 
            'alpha': 0
        }
        self.speed = speed

    def gen_spawn_points(self, oth_squares_coords):
        center_x = screen_width // 2
        center_y = screen_height // 2
        a = screen_width / 2.8  # Полуось по ширине (полуширина эллипса)
        b = screen_height / 2.8  # Полуось по высоте (полувысота эллипса)
        
        while True:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            distance_to_ellipse = ((x - center_x) ** 2) / (a ** 2) + ((y - center_y) ** 2) / (b ** 2)

            if distance_to_ellipse > 1:  # Если точка находится за пределами эллипса
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
                    square_color = (89, 118, 179, alpha)
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
                square_color = (137, 154, 197, alpha)
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
                squares.remove(square)
                return True
        return False


class Circle:
    def __init__(self, x, y, dx, dy):
        self.circle = (x, y, dx, dy)

    @staticmethod
    def from_center_to_mouse(screen_width, screen_height, bullet_speed, offset_angle=0):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        center_x = screen_width // 2
        center_y = screen_height // 2

        dx = mouse_x - center_x
        dy = mouse_y - center_y

        length = math.sqrt(dx ** 2 + dy ** 2)
        if length != 0:
            dx /= length
            dy /= length

        # Применяем смещение угла, если оно есть
        if offset_angle != 0:
            angle = math.atan2(dy, dx)
            angle += math.radians(offset_angle)
            dx = math.cos(angle)
            dy = math.sin(angle)

        return Circle(center_x, center_y, dx * bullet_speed, dy * bullet_speed)

    @staticmethod
    def offset_circle(circle, offset_distance):
        circle_x, circle_y, dx, dy = circle.circle
        # Перпендикулярный вектор для смещения
        perp_dx = -dy
        perp_dy = dx
        
        # Нормализуем перпендикулярный вектор и умножаем на расстояние смещения
        length = math.sqrt(perp_dx ** 2 + perp_dy ** 2)
        if length > 0:
            perp_dx = (perp_dx / length) * offset_distance
            perp_dy = (perp_dy / length) * offset_distance
        
        # Создаем новый круг, смещенный на определенное расстояние
        return Circle(circle_x + perp_dx, circle_y + perp_dy, dx, dy)

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
    def render_info(self, points, level, remaining_enemies, coins):

        text_to_blit = { # [value, offset]
            'SCORE': [points, 425],
            'LEVEL': [level, 125], 
            'ENEMIES REMAIN':  [remaining_enemies, -290],
            'COINS': [coins, -850],
        }
        
        for key in text_to_blit:
            if key == 'COINS':
                coins_text = font_s.render(f"{text_to_blit[key][0]}", True, (255, 255, 255))
                coins_rect = coins_text.get_rect(center=(screen_width // 2 - text_to_blit[key][1], 40))
                screen.blit(coins_text, coins_rect.topleft)

                circle_center = (coins_rect.right + 25, coins_rect.centery)
                circle_radius = coins_rect.height // 2
                circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, YELLOW, (circle_radius, circle_radius), circle_radius)
                screen.blit(circle_surface, (circle_center[0] - circle_radius + 3, circle_center[1] - circle_radius - 5))

                c_text = font_xs.render("C", True, (0, 0, 0))
                c_rect = c_text.get_rect(center=(coins_rect.right + 25, coins_rect.centery - 3))
                screen.blit(c_text, c_rect.topleft)
            else:
                points_text = font_s.render(f"{key}:  {text_to_blit[key][0]}", True, (255, 255, 255))
                text_rect = points_text.get_rect(center=(screen_width // 2 - text_to_blit[key][1], 40))
                transparent_rect = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
                transparent_rect.fill((0, 0, 0, 0))
                screen.blit(transparent_rect, text_rect.topleft)
                screen.blit(points_text, text_rect.topleft)

    def endscreen(self, result, curr_level, score):
        victory_screen = pygame.Surface((screen_width, screen_height))
        victory_screen.fill((0, 0, 0))

        text = font_for_the_biggest_nigga.render(result, True, (255, 255, 255))     
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 4 - 100))

        if result == 'YOU LOST' or result == 'KRAKEN REACHED YOU':
            lost = True
        else:
            lost = False
        
        offset = 0
        if lost:
            offset = 150
            level_text = font_xl.render('LEVELS COMPLETED: ' + str(curr_level-1), True, (255, 255, 255))
        else:
            level_text = font_xl.render('NEXT LEVEL: ' + str(curr_level+1), True, (255, 255, 255))
            next_level_button = pygame.Rect(screen_width // 2 - 175, screen_height // 2, 350, 100)
            next_level_text = font_m.render("NEXT LEVEL", True, (0, 0, 0))
            next_level_text_rect = next_level_text.get_rect(center=next_level_button.center)

        level_rect = level_text.get_rect(center=(screen_width // 2, screen_height // 4 + 100))

        score_text = font_l.render('SCORE: ' + str(score), True, (255, 255, 255))     
        score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 4 + 200))   

        replay_button = pygame.Rect(screen_width // 2 - 175, screen_height // 2 + 150 - offset, 350, 100)
        replay_text = font_m.render("RESTART", True, (0, 0, 0))
        replay_text_rect = replay_text.get_rect(center=replay_button.center)

        quit_button = pygame.Rect(screen_width // 2 - 175, screen_height // 2 + 300 - offset, 350, 100)
        quit_text = font_m.render("QUIT", True, (0, 0, 0))
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

        logo = font_for_the_biggest_nigga.render('LIGHTHOUSE', True, (255, 255, 255))     
        logo_rect = logo.get_rect(center=(screen_width // 2, screen_height // 4))      

        play_button = pygame.Rect(screen_width // 2 - 200, screen_height // 2 - 50, 400, 100)
        play_text = font_m.render("PLAY", True, (0, 0, 0))
        play_text_rect = play_text.get_rect(center=play_button.center)

        shop_button = pygame.Rect(screen_width // 2 - 200, screen_height // 2 + 100, 400, 100)
        shop_text = font_m.render("SHOP", True, (0, 0, 0))
        shop_text_rect = shop_text.get_rect(center=shop_button.center)

        quit_button = pygame.Rect(screen_width // 2 - 200, screen_height // 2 + 250, 400, 100)
        quit_text = font_m.render("QUIT", True, (0, 0, 0))
        quit_text_rect = quit_text.get_rect(center=quit_button.center)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.collidepoint(event.pos):
                        game(level=1, points=0)
                    if shop_button.collidepoint(event.pos):
                        self.shop()
                    if quit_button.collidepoint(event.pos):
                        sys.exit()
                        
            start_screen.fill((0, 0, 0))

            start_screen.blit(logo, logo_rect)

            pygame.draw.rect(start_screen, (255, 255, 255), play_button)
            start_screen.blit(play_text, play_text_rect)

            pygame.draw.rect(start_screen, (255, 255, 255), shop_button)
            start_screen.blit(shop_text, shop_text_rect)

            pygame.draw.rect(start_screen, (255, 255, 255), quit_button)
            start_screen.blit(quit_text, quit_text_rect)

            screen.blit(start_screen, (0, 0))
            pygame.display.flip()
    
    def debug_info(tentacles, stage):
        stage_text = font_xs.render(f"STAGE: {stage}", True, (255, 255, 255))
        stage_rect = stage_text.get_rect(topright=(screen_width - 10, 20))
        tr_rect = pygame.Surface((stage_rect.width, stage_rect.height), pygame.SRCALPHA)
        tr_rect.fill((0, 0, 0, 0))
        screen.blit(tr_rect, stage_rect.topleft)
        screen.blit(stage_text, stage_rect.topleft)
        positions = ['LT', 'LM', 'LB', 'RT', 'RM', 'RB']  # Позиции меток
        for i, t in enumerate(tentacles):
            if 'hp' in t:
                label = positions[i % len(positions)]  # Определение метки
                points_text = font_xs.render(f"{label}: {t['hp']}, {t['sprite']['rect'].x}, {t['sprite']['rect'].y}", True, (255, 255, 255))
                text_rect = points_text.get_rect(topright=(screen_width - 10, 40 + i * 30))
                transparent_rect = pygame.Surface((text_rect.width, text_rect.height), pygame.SRCALPHA)
                transparent_rect.fill((0, 0, 0, 0))
                screen.blit(transparent_rect, text_rect.topleft)
                screen.blit(points_text, text_rect.topleft)

    def shop(self):
        shop_screen = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        stats_to_display = [
            ("BULLET DAMAGE", "_progression_bullet_damage"),
            ("BULLET FREQUENCY", "_progression_bullet_frequency"),
            ("BULLET SPEED", "_progression_bullet_speed"),
            ("TURRET LEVEL", "_progression_turret_level"),
            ("BEAM WIDTH", "_progression_beam_width"),
            ("LIGHTHOUSE HP", "_progression_lighthouse_hp"),
        ]

        start_x_left_col = 200
        start_x_right_col = start_x_left_col + 800 + 100
        start_y = 230
        y_offset = 300
        upgrade_x_offset = 10
        progress_x_offset = -20
        cell_size = 70
        cell_margin = 10
        button_positions = {}
        
        shop_text = font_xl.render(f"SHOP", True, WHITE)
        shop_rect = shop_text.get_rect(center=(screen_width // 2, 90))
    
        reset_button_rect = pygame.Rect(1450, 80, 270, 100)
        reset_button_text = font_s.render("reset", True, WHITE)
        coins_color_transition = None
        while True:
            upgrade_button_rects = []  
            shop_screen.blit(objs['bg_shop']['sf'], objs['bg_shop']['rect'])
            shop_screen.blit(shop_text, shop_rect)
            shop_screen.blit(objs['shop_return']['sf'], objs['shop_return']['rect'])
            shop_screen.blit(reset_button_text, reset_button_rect)

            coins_color = (255, 255, 255)
            if coins_color_transition:
                coins_color = coins_color_transition.update_color()

            coins_text = font_m.render(f"{STATS['coins']}", True, coins_color)
            coins_rect = coins_text.get_rect(center=(screen_width // 2 + 800, 100))
            shop_screen.blit(coins_text, coins_rect.topleft)

            circle_center = (coins_rect.right + 30, coins_rect.centery)
            circle_radius = coins_rect.height // 2
            circle_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (230, 188, 76), (circle_radius, circle_radius), circle_radius)
            shop_screen.blit(circle_surface, (circle_center[0] - circle_radius + 3, circle_center[1] - circle_radius - 5))

            c_text = font_s.render("C", True, (0, 0, 0))
            c_rect = c_text.get_rect(center=(coins_rect.right + 31, coins_rect.centery - 1))
            shop_screen.blit(c_text, c_rect.topleft)

            for i, (stat_name, prog_name) in enumerate(stats_to_display):
                col = i % 2
                row = i // 2

                current_stat = STATS[stat_name]

                stat_x = start_x_left_col if col == 0 else start_x_right_col
                stat_y = start_y + row * y_offset

                text = font_m.render(f"{stat_name}: {current_stat}", True, WHITE)
                text_rect = text.get_rect(topleft=(stat_x, stat_y))
                transparent_rect = pygame.Surface((680, 100), pygame.SRCALPHA)
                transparent_rect.fill((42, 101, 161, 127))
                shop_screen.blit(transparent_rect, (text_rect.x - 20, text_rect.y - 30))
                shop_screen.blit(text, text_rect)

                if prog_name:
                    progression = list(map(int, STATS[prog_name].split(', ')))
                    
                    cell_x_start = stat_x + progress_x_offset
                    cell_y = text_rect.bottom + 40
                    
                    cell_color = WHITE if STATS[stat_name] != max(progression) else YELLOW

                    for j, value in enumerate(progression):
                        cell_x = cell_x_start + j * (cell_size + cell_margin)
                        cell_rect = pygame.Rect(cell_x, cell_y, cell_size, cell_size)
                        
                        pygame.draw.rect(shop_screen, cell_color, cell_rect)

                        if current_stat >= value:
                            inner_rect = cell_rect.inflate(-10, -10)
                            pygame.draw.rect(shop_screen, (0, 0, 0), inner_rect)
                        elif current_stat < value and j == progression.index(min([v for v in progression if v > current_stat])):
                            cell_value_text = font_s.render(str(value), True, (0, 0, 0))
                            cell_value_text_rect = cell_value_text.get_rect(center=cell_rect.center)
                            shop_screen.blit(cell_value_text, cell_value_text_rect)

                    if STATS[stat_name] != max(progression):
                        upgrade_button_rect = pygame.Rect(cell_x_start + (len(progression) * (cell_size + cell_margin)) + upgrade_x_offset, cell_y, 270, 100)
                        upgrade_button_text = font_m.render("UP", True, YELLOW)
                        upgrade_button_text_rect = upgrade_button_text.get_rect(topleft=(upgrade_button_rect.x + 35 , upgrade_button_rect.centery - 20))

                        button_positions[stat_name] = (upgrade_button_rect, upgrade_button_text, upgrade_button_text_rect)
                        tr_rect = pygame.Surface((upgrade_button_rect.width, upgrade_button_rect.height), pygame.SRCALPHA)
                        tr_rect.fill((42, 101, 161, 127))
                        shop_screen.blit(tr_rect, (upgrade_button_rect.x, upgrade_button_rect.y))
                        shop_screen.blit(upgrade_button_text, upgrade_button_text_rect)

                        next_stat = self.get_next_value(current_stat, progression)
                        next_index = progression.index(next_stat)
                        upgrade_cost = int(5 * (next_index ** 2) + 10)
                        
                        cost_text = font_s.render(f"{upgrade_cost}", True, WHITE)
                        cost_text_rect = cost_text.get_rect(topleft=(upgrade_button_rect.x + 135 , upgrade_button_rect.centery - 15))
                        shop_screen.blit(cost_text, cost_text_rect)

                        circle_c = (cost_text_rect.right + 30, cost_text_rect.centery)
                        circle_r = cost_text_rect.height // 2.5
                        circle_sf = pygame.Surface((circle_r * 2, circle_r * 2), pygame.SRCALPHA)
                        pygame.draw.circle(circle_sf, (230, 188, 76), (circle_r, circle_r), circle_r)
                        shop_screen.blit(circle_sf, (circle_c[0] - circle_r + 3, circle_c[1] - circle_r - 5))

                        upgrade_button_rects.append((upgrade_button_rect, stat_name, progression, upgrade_cost))
                    else:
                        if stat_name in button_positions:
                            upgrade_button_rect, _, _ = button_positions[stat_name]
                            shop_screen.blit(objs['bg_shop']['sf'], upgrade_button_rect, area=upgrade_button_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or event.type == pygame.MOUSEBUTTONDOWN and objs['shop_return']['rect'].collidepoint(event.pos):
                    self.startscreen()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for upgrade_button_rect, stat_name, progression, upgrade_cost in upgrade_button_rects:
                        if upgrade_button_rect.collidepoint(event.pos):
                            current_stat = STATS[stat_name]
                            next_stat = self.get_next_value(current_stat, progression)
                            if next_stat is not None:
                                next_index = progression.index(next_stat)
                                if STATS['coins'] >= upgrade_cost:
                                    STATS['coins'] -= upgrade_cost
                                    STATS[stat_name] = next_stat
                                    text = font_s.render(f"{stat_name}: {STATS[stat_name]}", True, WHITE)
                                else:
                                    # Подсвечиваем количество монет красным цветом
                                    coins_color_transition = ColorTransition((255, 0, 0), (255, 255, 255), duration=30)
                    if reset_button_rect.collidepoint(event.pos):
                        STATS["BULLET DAMAGE"] = 1
                        STATS["BULLET FREQUENCY"] = 10
                        STATS['BULLET SPEED'] = 7
                        STATS["TURRET LEVEL"] = 1
                        STATS["BEAM WIDTH"] = 15
                        STATS["LIGHTHOUSE HP"] = 2
                        STATS["coins"] = 9999

            save_stats(STATS)

            screen.blit(shop_screen, (0, 0))
            pygame.display.flip()

    def get_next_value(self, current_value, progression):
        for value in progression:
            if value > current_value:
                return value
        return None


class ColorTransition:
    def __init__(self, start_color, end_color, duration=30):
        self.start_color = pygame.Color(*start_color)
        self.end_color = pygame.Color(*end_color)
        self.duration = duration
        self.current_frame = 0

    def update_color(self):
        t = self.current_frame / self.duration
        self.current_frame = min(self.current_frame + 1, self.duration)
        return self.start_color.lerp(self.end_color, t)

    def reset(self):
        self.current_frame = 0
    

class Raindrop:
    def __init__(self):
        self.size = random.choices(RAINDROP_SIZES, RAINDROP_PROBABILITIES)[0]
        self.color = random.choices(RAINDROP_COLORS, RAINDROP_PROBABILITIES)[0]
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
        s.fill((*self.color, self.alpha))
        surface.blit(s, (self.x, self.y))


class Boss:
    def __init__(self) -> None:
        # Инициализация свойств для всех элементов tentacles
        tentacle_props = []
        for key in ["lt", "lm", "lb", "rt", "rm", "rb"]:
            tentacle_props.append(objs[key])

        self.tentacles = []
        self.t_hp = 3 # max hp for each tentacle
        for tentacle_sf in tentacle_props:
            self.tentacles.append({
                'hp': self.t_hp,
                'sprite': tentacle_sf,
                'appear_start_time': 0,
                'death_start_time': 0,
            })
        
        stage1_order = random.sample(range(6), 6)
        self.pair_lt_rb = [stage1_order[0], stage1_order[1]]
        self.pair_lm_rm = [stage1_order[2], stage1_order[3]]
        self.pair_lb_rt = [stage1_order[4], stage1_order[5]]

        self.stage2 = False
        self.stage2_order = random.sample(range(6), 6)
        self.curr_t_n = self.stage2_order[0]

        self.prev_alpha = 255
        self.started = None
        self.end_time = None
        self.show_hb = True
        self.show_text = False
        
    def bossfight(self, stage, moved_x, circles, level, score):
        if not moved_x:
            for i in range(6):
                if i < 3:
                    self.tentacles[i]['sprite']['rect'].x -= self.tentacles[i]['sprite']['rect'].width
                else:
                    self.tentacles[i]['sprite']['rect'].x += screen_width
        else:
            if stage == 1:
                if sum(self.tentacles[t_n]['hp'] for t_n in self.pair_lt_rb) != 0 or sum(self.tentacles[t_n]['sprite']['sf'].get_alpha() for t_n in self.pair_lt_rb) != 0:
                    pair_to_blit = self.pair_lt_rb
                elif sum(self.tentacles[t_n]['hp'] for t_n in self.pair_lm_rm) != 0 or sum(self.tentacles[t_n]['sprite']['sf'].get_alpha() for t_n in self.pair_lm_rm) != 0:
                    pair_to_blit = self.pair_lm_rm
                else:
                    pair_to_blit = self.pair_lb_rt
                
                for t_n in pair_to_blit:
                    for circle in circles:
                        circle_x, circle_y, dx, dy = circle

                        collision_lt = check_collision_circle_surface((circle_x, circle_y), CIRCLE_RAD, self.tentacles[t_n]['sprite'])
                        if collision_lt and self.tentacles[t_n]['hp'] > 0:
                            circles.remove(circle)
                            self.tentacles[t_n]['hp'] -= STATS['BULLET DAMAGE']
                            if self.tentacles[t_n]['hp'] < 0:
                                self.tentacles[t_n]['hp'] = 0
                    if self.tentacles[t_n]['hp'] > 0:
                        if t_n < 3:
                            if self.tentacles[t_n]['sprite']['rect'].x != 0:
                                self.tentacles[t_n]['sprite']['rect'].x += 2
                            else:
                                Screen.endscreen('KRAKEN REACHED YOU', level, score)
                        elif t_n > 2:
                            if self.tentacles[t_n]['sprite']['rect'].x != screen_width - self.tentacles[t_n]['sprite']['rect'].width:
                                self.tentacles[t_n]['sprite']['rect'].x -= 2
                            else:
                                Screen().endscreen('KRAKEN REACHED YOU', level, score)
                    elif self.tentacles[t_n]['sprite']['sf'].get_alpha() > 0: 
                        #change_sf_color(self.tentacles[t_n]['sprite']['sf'], (36, 42, 55, 255))
                        if self.tentacles[t_n]['sprite']['sf'].get_alpha() - 5 > 0:
                            self.tentacles[t_n]['sprite']['sf'].set_alpha(self.tentacles[t_n]['sprite']['sf'].get_alpha() - 5)
                        else: 
                            self.tentacles[t_n]['sprite']['sf'].set_alpha(0)

                    if self.tentacles[t_n]['sprite']['sf'].get_alpha() > 0:
                        screen.blit(self.tentacles[t_n]['sprite']['sf'], self.tentacles[t_n]['sprite']['rect'])
            elif stage == 2:
                self.t_hp = 2
                if not self.stage2:
                    for t_n in range(len(self.tentacles)):
                        if self.tentacles[t_n]['hp'] <= 2:
                            self.tentacles[t_n]['hp']+=0.01
                            
                        # adjust x coord to start pos
                        self.tentacles[t_n]['sprite']['rect'].x = 0 - self.tentacles[t_n]['sprite']['rect'].width if t_n < 3 else screen_width

                        self.moved_y(t_n)
                        
                        self.tentacles[t_n]['sprite']['sf'].set_alpha(254)        
                    
                    if sum(t['hp'] for t in self.tentacles) > len(self.tentacles) * self.t_hp:
                        '''
                        почему-то в цикле до этого хп каждой щупальцы возрастало до 2,00...013 несмотря на условие ифа
                        поэтому беру ток целую часть
                        '''
                        for i in self.stage2_order:
                            self.tentacles[i]['hp'] = int(self.tentacles[i]['hp'])
                    if sum(t['hp'] for t in self.tentacles) == len(self.tentacles) * self.t_hp:
                        self.stage2 = True
                else:
                    for t_n in self.stage2_order:
                        if self.tentacles[t_n]['hp'] > 0:
                            self.curr_t_n = t_n
                            break

                    for circle in circles:
                        circle_x, circle_y, dx, dy = circle

                        collision_lt = check_collision_circle_surface((circle_x, circle_y), CIRCLE_RAD, self.tentacles[self.curr_t_n]['sprite'])
                        if collision_lt and self.tentacles[self.curr_t_n]['hp'] > 0:
                            circles.remove(circle)
                            self.tentacles[self.curr_t_n]['hp'] -= STATS['BULLET DAMAGE']
                            if self.tentacles[t_n]['hp'] < 0:
                                self.tentacles[t_n]['hp'] = 0
                            self.tentacles[self.curr_t_n]['sprite']['sf'].set_alpha(self.tentacles[self.curr_t_n]['sprite']['sf'].get_alpha() - int(255 / (self.t_hp / STATS['BULLET DAMAGE'])))
                            if self.curr_t_n < 3: # left tentacles are knokbacked to the left, reversed for the right ones
                                self.tentacles[self.curr_t_n]['sprite']['rect'].x -= STATS['BULLET KNOCKBACK']
                            else:
                                self.tentacles[self.curr_t_n]['sprite']['rect'].x += STATS['BULLET KNOCKBACK']
                    if self.tentacles[self.curr_t_n]['hp'] > 0:
                        if self.curr_t_n < 3:
                            if self.tentacles[self.curr_t_n]['sprite']['rect'].x != 0:
                                self.tentacles[self.curr_t_n]['sprite']['rect'].x += 4
                            else:
                                Screen.endscreen('KRAKEN REACHED YOU', level, score)
                        else:
                            if self.tentacles[self.curr_t_n]['sprite']['rect'].x != screen_width - self.tentacles[self.curr_t_n]['sprite']['rect'].width:
                                self.tentacles[self.curr_t_n]['sprite']['rect'].x -= 4
                            else:
                                Screen().endscreen('KRAKEN REACHED YOU', level, score)

                    screen.blit(self.tentacles[self.curr_t_n]['sprite']['sf'], self.tentacles[self.curr_t_n]['sprite']['rect'])
            elif stage == 3:
                self.t_hp = 4
                for t_n in range(len(self.tentacles)):
                    if self.tentacles[t_n]['hp'] <= 4 and self.started == None:
                        self.tentacles[t_n]['hp']+=0.01
                        if self.tentacles[t_n]['hp'] > 2:
                            self.show_text = True
                    
                    self.tentacles[t_n]['sprite']['rect'].x = 0 if t_n < 3 else screen_width - self.tentacles[t_n]['sprite']['rect'].width
                    
                    self.moved_y(t_n)
                    
                if self.started:
                    objs['fin']['sf'].set_alpha(max(0, objs['fin']['sf'].get_alpha() - 2))

                    for t in self.tentacles:
                        t['hp'] = max(0, t['hp'] - 0.1)
                    if objs['fin']['sf'].get_alpha() == 0:
                        if self.end_time == None:
                            self.end_time = pygame.time.get_ticks()
                        if pygame.time.get_ticks() - self.end_time > 3000:
                            self.started = False
            if self.show_hb:
                self.healthbar(self.t_hp)
    
    def moved_y(self, t_n):
        if t_n == 0: # top left
            self.tentacles[t_n]['sprite']['rect'].y = screen_height * 0.0644
        elif t_n == 1 or t_n == 4: # middle left or right
            self.tentacles[t_n]['sprite']['rect'].y = screen_height * 0.268
        elif t_n == 2: # bottom left
            self.tentacles[t_n]['sprite']['rect'].y = screen_height - self.tentacles[t_n]['sprite']['rect'].height
        elif t_n == 3: # top right
            self.tentacles[t_n]['sprite']['rect'].y = 0
        elif t_n == 5: # bottom right
            self.tentacles[t_n]['sprite']['rect'].y = screen_height * 0.6287

    def healthbar(self, t_hp):
        total_hp = sum(t['hp'] for t in self.tentacles)
        max_hp = len(self.tentacles) * t_hp

        bar_width = screen_width / 2
        bar_height = screen_width / 128
        offset_y = screen_height / 20
        bar_center_y = screen_height - offset_y - bar_height / 2
        bar_x = (screen_width - bar_width) / 2
        bar_y = screen_height - offset_y - bar_height
        
        current_bar_width = (total_hp / max_hp) * bar_width

        top_left_x = bar_width - current_bar_width / 2
        top_left_y = bar_center_y - bar_height / 2

        text = font_m.render("KRAKEN", True, (255, 255, 255))
        text_rect = text.get_rect(center=(screen_width / 2, bar_center_y - screen_height / 40))
        screen.blit(text, text_rect)

        text_surface = font_s.render("PRESS SPACE", True, (255, 255, 255))  # Белый цвет текста
        text1_rect = text_surface.get_rect()

        screen_rect = screen.get_rect()
        text1_rect.centerx = screen_rect.centerx
        text1_rect.bottom = screen_rect.bottom - 150

        if self.show_text:
            screen.blit(text_surface, text1_rect)

        pygame.draw.rect(screen, HEALTHBAR_COLOR, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, HEALTH_COLOR, (top_left_x, top_left_y, current_bar_width, bar_height))
   

def lh_healthbar(curr_hp):
    max_hp = STATS['LIGHTHOUSE HP']
    
    text = font_xs.render("HP", True, LH_CURR_HP_COLOR)

    text_rect = text.get_rect()
    text_rect.centery = 37
    text_rect.right = LH_HEALTHBAR_POS[0] - 15
    screen.blit(text, text_rect)

    lh_healthbar_width = LH_1HP_WIDTH * STATS['LIGHTHOUSE HP']
    current_health_width = lh_healthbar_width * (curr_hp / max_hp)

    pygame.draw.rect(screen, LH_FULL_HP_COLOR, (LH_HEALTHBAR_POS[0], LH_HEALTHBAR_POS[1], lh_healthbar_width, LH_HEALTHBAR_HEIGHT))
    pygame.draw.rect(screen, LH_CURR_HP_COLOR, (LH_HEALTHBAR_POS[0], LH_HEALTHBAR_POS[1], current_health_width, LH_HEALTHBAR_HEIGHT))
      
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
    # вычисляем координаты левого края
    perpendicular_dx_left = -dy
    perpendicular_dy_left = dx

    perpendicular_length = math.sqrt(perpendicular_dx_left ** 2 + perpendicular_dy_left ** 2)
    if perpendicular_length > 0:
        perpendicular_dx_left /= perpendicular_length
        perpendicular_dy_left /= perpendicular_length

    perpendicular_dx_left *= STATS['BEAM WIDTH'] * 10
    perpendicular_dy_left *= STATS['BEAM WIDTH'] * 10

    left_vertex_x = end_x + perpendicular_dx_left
    left_vertex_y = end_y + perpendicular_dy_left

    # вычисляем координаты правого края
    perpendicular_dx_right = dy
    perpendicular_dy_right = -dx

    perpendicular_length_right = math.sqrt(perpendicular_dx_right ** 2 + perpendicular_dy_right ** 2)
    if (perpendicular_length_right > 0):
        perpendicular_dx_right /= perpendicular_length_right
        perpendicular_dy_right /= perpendicular_length_right

    perpendicular_dx_right *= STATS['BEAM WIDTH'] * 10
    perpendicular_dy_right *= STATS['BEAM WIDTH'] * 10

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
                stats['coins'] += 1
                save_stats(stats)
                square.trigger_death_anim(pygame.time.get_ticks())
                fading_squares.append(square)
                squares.remove(square) 
                circles.remove(circle)

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

    return collision_point is not None

def game(level, points):
    if (level == 0):
        sys.exit()
    
    lh_hp = STATS['LIGHTHOUSE HP']

    circles = []
    last_circle_spawn_time = 0
    spawn_delay = 1200 - STATS['BULLET FREQUENCY'] * 10
    circle_drawer = Circle(0, 0, 0, 0)
    offsets = [20, -20]

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
    max_odd = 100
    
    raindrops = []
    last_rain_time = 0

    boss = Boss()
    boss_preview = None
    scr_alpha = 255
    start_time = 0
    objs['preview']['sf'].set_alpha(0)
    objs['fin']['sf'].set_alpha(0)
    boss_killed = False
    stage = 1
    moved_x = False

    running = True
    clock = pygame.time.Clock()

    squares.append(Square(speed, oth_sqs_coords))
    oth_sqs_coords.append(squares[0].square['position'])

    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or running == False):
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if current_time - last_circle_spawn_time >= spawn_delay:
                    new_circles = []
                    main_circle = Circle.from_center_to_mouse(screen_width, screen_height, STATS['BULLET SPEED'])

                    if STATS['TURRET LEVEL'] == 1:
                        # один круг по центру
                        new_circles.append(main_circle)

                    if STATS['TURRET LEVEL'] == 2:
                        # два круга со смещением 10 пикс
                        [new_circles.append(Circle.offset_circle(main_circle, o)) for o in offsets]

                    if STATS['TURRET LEVEL'] == 3:
                        # круг по центру + два круга под углом 5 град
                        degrees = [0, 5, -5]
                        [new_circles.append(Circle.from_center_to_mouse(screen_width, screen_height, STATS['BULLET SPEED'], d)) for d in degrees]
                    
                    if STATS['TURRET LEVEL'] == 4:
                        # два круга со смещением + 2 круга под углом
                        degrees = [5, -5]
                        [new_circles.append(Circle.offset_circle(main_circle, o)) for o in offsets]
                        [new_circles.append(Circle.from_center_to_mouse(screen_width, screen_height, STATS['BULLET SPEED'], d)) for d in degrees]

                    if STATS['TURRET LEVEL'] == 5:
                        # круг по центру + два круга 5 град + 2 круга 10 град
                        degrees = [0, 5, -5, 10, -10]
                        [new_circles.append(Circle.from_center_to_mouse(screen_width, screen_height, STATS['BULLET SPEED'], d)) for d in degrees]

                    for c in new_circles:
                        circles.append(c.circle)

                    last_circle_spawn_time = pygame.time.get_ticks()
            elif event.type == SPAWN_ENEMY_EVENT and enemies_spawned < n_enemies - 1:
                squares.append(Square(speed, oth_sqs_coords))
                oth_sqs_coords.append(squares[len(squares) - 1].square['position'])
                enemies_spawned += 1
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and boss.started == None and stage == 3:
                boss.started = True
                boss.show_hb = False
                objs['fin']['sf'].set_alpha(255)
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
                    max_odd = max(max_odd-5, 0)
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
            'bg_isl',
            'preview',
            'isl',
            'lh',
            'lh_top'
        ]

        for key in objs_to_blit:
            obj = objs[key]
            blit_x = (screen_width - obj['rect'].width) // 2
            blit_y = (screen_height - obj['rect'].height) // 2
            if key == 'isl' and objs['fin']['sf'].get_alpha() != 0:
                screen.blit(objs['fin']['sf'], (0, 0))
            if key == 'lh_top':
                screen.blit(beam_surface, (0,0))
            if (key == 'bg_isl' and obj['sf'].get_alpha() == 0) or (key == 'preview' and boss_preview == None) or obj['sf'].get_alpha() == 0:
                continue
            screen.blit(obj['sf'], (blit_x, blit_y))
        
        island_center = (objs['isl']['rect'].centerx, objs['isl']['rect'].centery)
        island_radius = min(objs['isl']['rect'].width, objs['isl']['rect'].height) // 2 - SQ_SIZE
        island_circle = (island_center, island_radius)

        if Square(speed, oth_sqs_coords).check_loss(squares, island_circle):
            lh_hp -= 1    
        
        if lh_hp == 0:
            Screen().endscreen("YOU LOST", level, points)

        [sq.draw_square(current_time) for sq in squares]

        Square(speed, oth_sqs_coords).update_fading_squares(fading_squares)

        n_sq = len(squares)

        check_collision(circles=circles, squares=squares, fading_squares=fading_squares, stats=STATS)

        # если круг сбил квадрат то квадрат удаляется из массива => добавляем поинт если после проверки на столкновение квадратов оказалось меньше чем до проверки
        if len(squares) < n_sq:
            points+=1

        circles = circle_drawer.draw_circles(circles)

        if boss_preview and objs['bg_isl']['sf'].get_alpha() > 0:
            objs['bg_isl']['sf'].set_alpha(objs['bg_isl']['sf'].get_alpha() - 1.5)        
        
        '''if objs['bg_isl']['sf'].get_alpha() > 0:
            screen.blit(objs['bg_isl']['sf'], (0, 0))'''

        # капли
        t_current_time = time.time()
        if t_current_time - last_rain_time >= 0.02:
            raindrops.append(Raindrop())
            last_rain_time = t_current_time

        raindrops = [drop for drop in raindrops if drop.update()]
        [drop.draw(screen) for drop in raindrops]          
    
        Screen().render_info(points, level, len(squares), STATS['coins'])
        lh_healthbar(lh_hp)

        # проверка len(f_s) нужна для того, чтобы экран победы запускался после последней анимации смерти врага, а не сразу же при его убийстве
        if (len(squares)==0 and points != 0 and len(fading_squares) == 0): 
            if level == 9 and not boss_killed:
                if boss_preview != False:
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
                                max_odd = 100
                elif not boss_killed:
                    Screen.debug_info(boss.tentacles, stage)
                    boss.bossfight(stage, moved_x, circles, level, points)
                    moved_x = True
                    if stage != 3 and sum(t['hp'] for t in boss.tentacles) == 0 and sum(t['sprite']['sf'].get_alpha() for t in boss.tentacles) == 0:
                        stage += 1
                    elif stage == 3 and sum(t['hp'] for t in boss.tentacles) == 0 and boss.started == False:
                        boss_killed = True
            else:
                Screen().endscreen("LEVEL COMPLETED", level, points)
                save_stats(STATS)
        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    Screen().startscreen()