import pygame
import os
from consts import *

# Инициализация Pygame
pygame.init()

info = pygame.display.Info()
screen_width = info.current_w
screen_height = info.current_h

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Lighthouse")

lighthouse_image_path = os.path.join(os.path.dirname(__file__), 'sprites/lighthouse.png')
lighthouse_image = pygame.image.load(lighthouse_image_path)

lighthouse_image = pygame.transform.scale(lighthouse_image, (lh_width, lh_height))
lighthouse_rect = lighthouse_image.get_rect()

lighthouse_rect.center = (screen_width // 2, screen_height // 2)


island_image_path = os.path.join(os.path.dirname(__file__), 'sprites/island.png')
island_image = pygame.image.load(island_image_path)

island_image = pygame.transform.scale(island_image, (isl_width, isl_height))
island_rect = island_image.get_rect()

island_rect.center = (screen_width // 2, screen_height // 2)


beam_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)    


font = pygame.font.Font('font/ToThePointRegular-n9y4.ttf', 36)