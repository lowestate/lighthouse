import math
import time
import pygame
import random
from consts import *
from start import *


class Square():
    def __init__(self, sprite, speed) -> None:
        self.square = {
            'position': self.gen_spawn_points(), 
            'state': 'normal', 
            'start_time': 0, 
            'fade': 0, 
            'alpha': 0}
        self.sprite = sprite
        self.resized_sprite = pygame.transform.scale(sprite, (sprite.get_width() // 4, sprite.get_height() // 4))
        self.speed = speed

    def gen_spawn_points(self):
        center_x = screen_width // 2
        center_y = screen_height // 2
        radius = 400
        
        while True:
            x = random.randint(0, screen_width)
            y = random.randint(0, screen_height)
            distance_to_center = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            
            if distance_to_center > radius:
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

    def draw_square(self, current_time, beam_triangle):
        square_x, square_y = self.square['position']
        distance_to_center = math.sqrt((square_x + 20 - screen_width // 2) ** 2 + (square_y + 20 - screen_height // 2) ** 2)

        resized_sprite_width = self.resized_sprite.get_width()
        resized_sprite_height = self.resized_sprite.get_height()
        sprite_x = square_x + (square_size - resized_sprite_width) // 2
        sprite_y = square_y + (square_size - resized_sprite_height) // 2
        sprite_with_alpha = self.resized_sprite.copy()\
        
        center_x, center_y = screen_width // 2, screen_height // 2
        angle = 180 - math.degrees(math.atan2(center_y - (square_y + 20), center_x - (square_x + 20)))  

        if distance_to_center < 300 or any(point_inside_triangle(square_x, square_y, beam_triangle) for square_x, square_y in [(square_x, square_y), (square_x + square_size, square_y), (square_x, square_y + square_size), (square_x + square_size, square_y + square_size)]):
            self.square['state'] = 'hit'
            self.square['start_time'] = current_time
            self.square['alpha'] = 255 

        if self.square['state'] == 'hit':
            elapsed_time = (current_time - self.square['start_time']) / 1000
            if elapsed_time < 1:
                alpha = max(0, int(255 * (1 - elapsed_time)))
                sprite_with_alpha.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                rotated_sprite = pygame.transform.rotate(sprite_with_alpha, angle)
                screen.blit(rotated_sprite, rotated_sprite.get_rect(center=(sprite_x + resized_sprite_width // 2, sprite_y + resized_sprite_height // 2)))
            else:
                self.square['state'] = 'normal'
                self.square['alpha'] = 0

        elif self.square['state'] == 'normal':
            if 'alpha' not in self.square:
                self.square['alpha'] = 0

            sprite_with_alpha.fill((255, 255, 255, self.square['alpha']), special_flags=pygame.BLEND_RGBA_MULT)
            rotated_sprite = pygame.transform.rotate(sprite_with_alpha, angle)
            screen.blit(rotated_sprite, rotated_sprite.get_rect(center=(sprite_x + resized_sprite_width // 2, sprite_y + resized_sprite_height // 2)))

    def trigger_death_anim(self, current_time):
        self.square['state'] = 'death_anim'
        self.square['fade'] = current_time
        self.square['alpha'] = 255

    def update_fading_squares(self, fading_squares):
        current_time = pygame.time.get_ticks()
        center_x, center_y = screen_width // 2, screen_height // 2

        for square in fading_squares:
            elapsed_time = (current_time - square.square['fade']) / 1000
            square_x, square_y = square.square['position']
            angle = 180 - math.degrees(math.atan2(center_y - (square_y + 20), center_x - (square_x + 20)))
            if elapsed_time < 1:
                alpha = max(0, int(255 * (1 - elapsed_time / 1)))
                
                sprite_x = square_x + (square_size - self.resized_sprite.get_width()) // 2
                sprite_y = square_y + (square_size - self.resized_sprite.get_height()) // 2       
                self.resized_sprite.fill((255, 0, 0, alpha), special_flags=pygame.BLEND_RGBA_MULT)
                rotated_sprite = pygame.transform.rotate(self.resized_sprite, angle)
                screen.blit(rotated_sprite, rotated_sprite.get_rect(center=(sprite_x + self.resized_sprite.copy().get_width() // 2, sprite_y + self.resized_sprite.copy().get_height() // 2)))
            else:
                fading_squares.remove(square)   

    def check_loss(self, squares, island_circle):
        island_center, island_radius = island_circle
        for square in squares:
            square_x, square_y = square.square['position']
            square_center_x = square_x + square_size / 2
            square_center_y = square_y + square_size / 2

            distance = math.sqrt((square_center_x - island_center[0]) ** 2 + (square_center_y - island_center[1]) ** 2)
            if distance < island_radius + square_size / 2:
                return True
        return False


class Circle():
    def __init__(self, sprite) -> None:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - (screen_width // 2)
        dy = mouse_y - (screen_height // 2)
            
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length > 0:
            dx /= length
            dy /= length
                
        circle_x = screen_width // 2
        circle_y = screen_height // 2

        self.circle = (circle_x, circle_y, dx * speed, dy * speed)
        self.sprite = pygame.transform.scale(sprite, (sprite.get_width() // 5, sprite.get_height() // 5))
        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

    def draw_circles(self, circles):
        new_circles = []
        for circle in circles:
            # Извлечение координат и скорости круга
            circle_x, circle_y, dx, dy = circle
            # Обновление позиции круга
            circle_x += dx
            circle_y += dy
            # Проверка, выходит ли круг за границы экрана
            if circle_x + circle_radius > screen_width or circle_x - circle_radius < 0 or circle_y + circle_radius > screen_height or circle_y - circle_radius < 0:
                continue  # Пропускаем этот круг
            
            # Вычисление угла поворота в сторону курсора
            
            angle = math.degrees(math.atan2(self.mouse_y - circle_y, self.mouse_x - circle_x)) - 90  # Вычитание 90, чтобы спрайт смотрел вверх
            
            # Поворот спрайта
            rotated_sprite = pygame.transform.rotate(self.sprite, angle)
            rotated_rect = rotated_sprite.get_rect(center=(int(circle_x), int(circle_y)))
            
            # Отрисовка спрайта
            screen.blit(rotated_sprite, rotated_rect.topleft)
            
            # Добавляем круг в новый список
            new_circles.append((circle_x, circle_y, dx, dy))
        # Заменяем старый список новым
        return new_circles

class Screen():
    def render_points(self, points):
        points_text = font.render(f'SCORE:  {points} ', True, (255, 255, 255))
        text_rect = points_text.get_rect(center=(screen_width // 2 + 130, 30))
        screen.blit(points_text, text_rect)

    def render_level(self, level):
        level_text = font.render(f'LEVEL:  {level} ', True, (255, 255, 255))
        text_rect = level_text.get_rect(center=(screen_width // 2 - 130, 30))
        screen.blit(level_text, text_rect)

    def endscreen(self, result, curr_level, score):
        victory_screen = pygame.Surface((screen_width, screen_height))
        victory_screen.fill((0, 0, 0))

        font = pygame.font.Font(None, 90)
        button_font = pygame.font.Font(None, 60)

        text = font.render(result, True, (255, 255, 255))     
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 4))

        if (result == "YOU LOST"):
            level_text = font.render('LEVELS COMPLETED: ' + str(curr_level-1), True, (255, 255, 255))
        else:
            level_text = font.render('NEXT LEVEL: ' + str(curr_level+1), True, (255, 255, 255))

        level_rect = level_text.get_rect(center=(screen_width // 2, screen_height // 4 + 100))

        score_text = font.render('SCORE: ' + str(score), True, (255, 255, 255))     
        score_rect = score_text.get_rect(center=(screen_width // 2, screen_height // 4 + 200))

        next_level_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2, 300, 100)
        next_level_text = button_font.render("NEXT LEVEL", True, (0, 0, 0))
        next_level_text_rect = next_level_text.get_rect(center=next_level_button.center)

        replay_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 150, 300, 100)
        replay_text = button_font.render("RESTART", True, (0, 0, 0))
        replay_text_rect = replay_text.get_rect(center=replay_button.center)

        quit_button = pygame.Rect(screen_width // 2 - 150, screen_height // 2 + 300, 300, 100)
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

            victory_screen.set_alpha(alpha)
            text.set_alpha(alpha)
            level_text.set_alpha(alpha)
            score_text.set_alpha(alpha)
            next_level_text.set_alpha(alpha)
            replay_text.set_alpha(alpha)
            quit_text.set_alpha(alpha)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if next_level_button.collidepoint(event.pos):
                        game(level=curr_level + 1, points=score)
                    if replay_button.collidepoint(event.pos):
                        game(level=1, points=0)
                    elif quit_button.collidepoint(event.pos):
                        game(level=0, points=0)

            victory_screen.fill((0, 0, 0))
            victory_screen.blit(text, text_rect)
            victory_screen.blit(level_text, level_rect)
            victory_screen.blit(score_text, score_rect)

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
        new_island_image = pygame.transform.scale(island_image, (island_image.get_width() * 1.3, island_image.get_height() * 1.3))
        new_island_image_rect = new_island_image.get_rect()
        new_island_image_rect.center = (screen_width // 2, screen_height // 2)

        new_lh_image = pygame.transform.scale(lighthouse_image, (lighthouse_image.get_width() * 1.3, lighthouse_image.get_height() * 1.3))
        new_lh_image_rect = new_lh_image.get_rect()
        new_lh_image_rect.center = (screen_width // 2, screen_height // 2)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or running == False):
                    pygame.quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if new_island_image_rect.collidepoint(event.pos):
                        game(level=1, points=0)
                    if r_arrow_image.collidepoint(event.pos):
                        pass
                    if l_arrow_image.collidepoint(event.pos):
                        pass
                        
            screen.fill(blue_color)

            screen.blit(island_image, island_rect)
            screen.blit(new_lh_image, new_lh_image_rect)
            screen.blit(r_arrow_image, r_arrow_rect)
            screen.blit(l_arrow_image, l_arrow_rect)
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

        level_button = pygame.Rect(screen_width // 2 - 200, screen_height // 2 + 150, 400, 100)
        level_text = button_font.render("CHOOSE A LEVEL", True, (0, 0, 0))
        level_text_rect = level_text.get_rect(center=level_button.center)

        quit_button = pygame.Rect(screen_width // 2 - 200, screen_height // 2 + 300, 400, 100)
        quit_text = button_font.render("QUIT", True, (0, 0, 0))
        quit_text_rect = quit_text.get_rect(center=quit_button.center)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button.collidepoint(event.pos):
                        game(level=1, points=0)
                    if level_button.collidepoint(event.pos):
                        self.level_screen()
                    if quit_button.collidepoint(event.pos):
                        pygame.quit()

            start_screen.fill((0, 0, 0))

            start_screen.blit(logo, logo_rect)

            pygame.draw.rect(start_screen, (255, 255, 255), play_button)
            start_screen.blit(play_text, play_text_rect)

            pygame.draw.rect(start_screen, (255, 255, 255), level_button)
            start_screen.blit(level_text, level_text_rect)

            pygame.draw.rect(start_screen, (255, 255, 255), quit_button)
            start_screen.blit(quit_text, quit_text_rect)

            screen.blit(start_screen, (0, 0))
            pygame.display.flip()


def get_points(dx, dy, end_x, end_y):
    perpendicular_dx = -dy
    perpendicular_dy = dx

    # Нормализуем вектор
    perpendicular_length = math.sqrt(perpendicular_dx ** 2 + perpendicular_dy ** 2)
    if perpendicular_length > 0:
        perpendicular_dx /= perpendicular_length
        perpendicular_dy /= perpendicular_length

    # Умножаем нормализованный вектор на 100 пикселей
    perpendicular_dx *= 100
    perpendicular_dy *= 100

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
    perpendicular_dx_right *= 100
    perpendicular_dy_right *= 100

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

def check_collision(circles, squares, fading_squares):
    for circle in circles:
        circle_x, circle_y, dx, dy = circle
        for square in squares:
            square_x, square_y = square.square['position']
            if (square_x <= circle_x <= square_x + 40) and (square_y <= circle_y <= square_y + 40):        
                square.trigger_death_anim(pygame.time.get_ticks())
                fading_squares.append(square)
                squares.remove(square) 

def game(level, points):

    if (level == 0):
        pygame.quit() # дописать хендлер выхода из игры - щас ошибка какая-то выползает при выходе: pygame.error: video system not initialized

    circles = []
    squares = []
    fading_squares = []
    n_enemies = level * 2
    speed = math.sqrt(level) / 2

    enemy_sprite = T1enemy_image
    bullet = bullet_image

    for _ in range(n_enemies):
        squares.append(Square(enemy_sprite, speed))

    running = True
    clock = pygame.time.Clock()
    current_frame = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_ESCAPE or running == False):
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                new_c = Circle(bullet)
                circles.append(new_c.circle)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        dx = mouse_x - (screen_width // 2)
        dy = mouse_y - (screen_height // 2)
        
        length = math.sqrt(dx ** 2 + dy ** 2)
        if length > 0:
            dx /= length
            dy /= length

        end_x = (screen_width // 2) + dx * beam_length
        end_y = (screen_height // 2) + dy * beam_length

        beam_surface.fill((0, 0, 0, 0))
        
        left_x, left_y, right_x, right_y = get_points(dx, dy, end_x, end_y)

        beam_triangle = [
            (left_x, left_y),    # вершина слева
            (right_x, right_y),  # вершина справа
            (screen_width // 2, screen_height // 2)  # вершина в центре
        ]

        pygame.draw.polygon(beam_surface, beam_color, beam_triangle)

        pygame.draw.line(beam_surface, beam_color, (screen_width // 2, screen_height // 2), (end_x, end_y), 5)  

        for sq in squares:
            sq.upd_sq_pos()

        current_frame = (current_frame + 1) % frame_count
        screen.blit(frames[current_frame], (0, 0))
        screen.blit(island_image, island_rect)
        screen.blit(beam_surface, (0, 0))
        screen.blit(lighthouse_image, lighthouse_rect)

        island_center = (island_rect.centerx, island_rect.centery)
        island_radius = min(island_rect.width, island_rect.height) // 2 - 20
        island_circle = (island_center, island_radius)

        if sq.check_loss(squares, island_circle):
            Screen().endscreen("YOU LOST", level, points)

        current_time = pygame.time.get_ticks()

        for sq in squares:
            sq.draw_square(current_time, beam_triangle)

        Square(enemy_sprite, speed).update_fading_squares(fading_squares)

        n_sq = len(squares)

        check_collision(circles=circles, squares=squares, fading_squares=fading_squares)

        # если круг сбил квадрат то квадрат удаляется из массива => добавляем поинт если после проверки на столкновение квадратов оказалось меньше чем до проверки
        if len(squares) < n_sq:
            points+=1

        circles = Circle(bullet).draw_circles(circles)

        Screen().render_points(points)

        Screen().render_level(level)

        if (len(squares)==0):
            Screen().endscreen("LEVEL COMPLETED", level, points)

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    Screen().startscreen()