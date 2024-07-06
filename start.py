import pygame
import os
from consts import *
from PIL import Image

pygame.init()
pygame.font.init()
font = pygame.font.Font('graphics/font/font.ttf', 70)

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Lighthouse")

lighthouse_image_path = os.path.join(os.path.dirname(__file__), 'graphics/lh/lighthouse.png')
lighthouse_image = pygame.image.load(lighthouse_image_path)

lighthouse_image = pygame.transform.scale(lighthouse_image, (lh_width, lh_height))
lighthouse_rect = lighthouse_image.get_rect()

lighthouse_rect.center = (screen_width // 2, screen_height // 2)


island_image_path = os.path.join(os.path.dirname(__file__), 'graphics/lh/island.png')
island_image = pygame.image.load(island_image_path)

island_image = pygame.transform.scale(island_image, (isl_width, isl_height))
island_rect = island_image.get_rect()

island_rect.center = (screen_width // 2, screen_height // 2)


beam_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)    


level = 1
points=0


T1enemy_image_path = os.path.join(os.path.dirname(__file__), 'graphics/enemies/enemy1.png')
T1enemy_image = pygame.image.load(T1enemy_image_path).convert_alpha()


bullet_image_path = os.path.join(os.path.dirname(__file__), 'graphics/lh/rbullet.png')
bullet_image = pygame.image.load(bullet_image_path).convert_alpha()

# Загрузка и разделение GIF на кадры
gif_path = 'graphics/bg/bg1.gif'
gif = Image.open(gif_path)

frames = []
try:
    while True:
        frame = gif.copy().convert('RGBA')
        frame = frame.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        frames.append(pygame.image.fromstring(frame.tobytes(), frame.size, frame.mode))
        gif.seek(len(frames))  # Переход к следующему кадру
except EOFError:
    pass

# Получение информации о количестве кадров и задержке
frame_count = len(frames)
frame_durations = gif.info['duration'] / 1000  # Длительность одного кадра в секундах