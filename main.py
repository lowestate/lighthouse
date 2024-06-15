import math
import pygame
from consts import *
from start import *

circles = []
squares = []
fading_squares = []
points=0

def get_points():
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

def draw_circles(circles):
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
        # Отрисовка круга
        pygame.draw.circle(screen, circle_color, (int(circle_x), int(circle_y)), circle_radius)
        # Добавляем круг в новый список
        new_circles.append((circle_x, circle_y, dx, dy))
    # Заменяем старый список новым
    return new_circles

def draw_squares(squares):
    for square in squares:
        square_x, square_y = square['position']
        distance_to_center = math.sqrt((square_x + 20 - screen_width // 2) ** 2 + (square_y + 20 - screen_height // 2) ** 2)

        if distance_to_center < 250:
            pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(square_x, square_y, square_size, square_size))
            continue

        if square['state'] == 'normal' and any(point_inside_triangle(square_x, square_y, beam_triangle) for square_x, square_y in [(square_x, square_y), (square_x + square_size, square_y), (square_x, square_y + square_size), (square_x + square_size, square_y + square_size)]):
            square['state'] = 'hit'
            square['start_time'] = current_time

        if square['state'] == 'hit':
            elapsed_time = (current_time - square['start_time']) / 1000
            if elapsed_time < 1:
                alpha = max(0, int(255 * (1 - elapsed_time)))
                square_color = (255, 0, 0, alpha)
                s = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
                s.fill(square_color)
                screen.blit(s, (square_x, square_y))
            else:
                square['state'] = 'normal'
        elif square['state'] == 'normal':
            pygame.draw.rect(screen, blue_color, pygame.Rect(square_x, square_y, square_size, square_size))

def check_collision(circles, squares):
    for circle in circles:
        circle_x, circle_y, dx, dy = circle
        for square in squares:
            square_x, square_y = square['position']
            if (square_x <= circle_x <= square_x + 40) and (square_y <= circle_y <= square_y + 40):        
                death_anim(square=square)
                squares.remove(square)

def death_anim(square):
    square['fade'] = pygame.time.get_ticks()
    fading_squares.append(square)

def update_fading_squares():
    current_time = pygame.time.get_ticks()
    for square in fading_squares:
        elapsed_time = (current_time - square['fade']) / 1000
        if elapsed_time < 1:
            alpha = max(0, int(255 * (1 - elapsed_time / 1)))
            square_color = (240, 240, 240, alpha)
            sq_x, sq_y = square['position']
            s = pygame.Surface((square_size, square_size), pygame.SRCALPHA)
            s.fill(square_color)
            screen.blit(s, (sq_x, sq_y))
        else:
            fading_squares.remove(square)    

def shoot():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - (screen_width // 2)
    dy = mouse_y - (screen_height // 2)
           
    length = math.sqrt(dx ** 2 + dy ** 2)
    if length > 0:
        dx /= length
        dy /= length
           
            
    circle_x = screen_width // 2
    circle_y = screen_height // 2
    speed = 10
    circles.append((circle_x, circle_y, dx * speed, dy * speed))

def render_points(points):
    print(points)
    points_text = font.render(f'SCORE:  {points} ', True, (255, 255, 255))
    text_rect = points_text.get_rect(center=(screen_width // 2, 30))
    screen.blit(points_text, text_rect)

square_positions = [(1000, 50), (400, 170), (150, 900), (1450, 200), (1700, 900)]
for pos in square_positions:
    squares.append({'position': pos, 'state': 'normal', 'start_time': 0, 'fade': 0})

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            shoot()

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
    
    left_x, left_y, right_x, right_y = get_points()

    beam_triangle = [
        (left_x, left_y),    # вершина слева
        (right_x, right_y),  # вершина справа
        (screen_width // 2, screen_height // 2)  # вершина в центре
    ]

    pygame.draw.polygon(beam_surface, beam_color, beam_triangle)

    pygame.draw.line(beam_surface, beam_color, (screen_width // 2, screen_height // 2), (end_x, end_y), 5)  

    for square in squares:
        square_x, square_y = square['position']

        direction_x = (screen_width // 2) - square_x
        direction_y = (screen_height // 2) - square_y
        distance = math.sqrt(direction_x ** 2 + direction_y ** 2)

        if distance > 0:
            direction_x /= distance
            direction_y /= distance

        square_x += direction_x * enemy_speed
        square_y += direction_y * enemy_speed

        square['position'] = (square_x, square_y)

    screen.fill(blue_color)
    screen.blit(island_image, island_rect)
    screen.blit(beam_surface, (0, 0))
    screen.blit(lighthouse_image, lighthouse_rect)

    current_time = pygame.time.get_ticks()

    draw_squares(squares)
    update_fading_squares()

    n_sq = len(squares)

    check_collision(circles=circles, squares=squares)

    # если круг сбил квадрат то квадрат удаляется из массива => добавляем поинт если после проверки на столкновение квадратов оказалось меньше чем до проверки
    if len(squares) < n_sq:
        points+=1
        
    circles = draw_circles(circles)

    render_points(points=points)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
