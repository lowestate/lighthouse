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
beam_state = 'normal'


bg_image_path = os.path.join(os.path.dirname(__file__), 'graphics/bg/bg_isl.png')
bg_image = pygame.image.load(bg_image_path)
bg_image = pygame.transform.scale(bg_image, (screen_width, screen_height))
bg_rect = bg_image.get_rect()


# right arrow
r_arrow_image_path = os.path.join(os.path.dirname(__file__), 'graphics/other/arrow.png')
r_arrow_image = pygame.image.load(r_arrow_image_path)
r_arrow_image = pygame.transform.scale(r_arrow_image, (r_arrow_image.get_width() // 2, r_arrow_image.get_height() // 2))
r_arrow_rect = r_arrow_image.get_rect()
r_arrow_rect.center = (screen_width // 2 + 300, screen_height // 2)

# left arrow
l_arrow_image = r_arrow_image.copy()
l_arrow_image = pygame.transform.flip(l_arrow_image, True, False) # flip_x : True, flip_y : False - отображение по горизонтали
l_arrow_rect = l_arrow_image.get_rect()
l_arrow_rect.center = (screen_width // 2 - 300, screen_height // 2)
