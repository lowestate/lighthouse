import pygame
import os
import ctypes
from consts import *

pygame.init()
pygame.font.init()
font = pygame.font.Font('graphics/font/font.ttf', 70)

info = pygame.display.Info()
unscaled_scr_width = info.current_w
unscaled_scr_height = info.current_h

# узнаем параматр масштабирования экрана
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
scale_factor = user32.GetDpiForSystem()
scaled = scale_factor / 96 # значение масштабировния / 100, в моем случае - 1.25
screen_height = int(unscaled_scr_height * scaled)
screen_width = int(unscaled_scr_width * scaled)
print(f"scalar:{scaled}\nraw:{unscaled_scr_width}x{unscaled_scr_height}\nadjusted:{screen_width}x{screen_height}")

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Lighthouse")

paths = [
    'graphics/bg/lh_top.png',
    'graphics/bg/lh.png',
    'graphics/bg/isl.png',
    'graphics/bg/bg_isl.png',
]

sprite_properties: dict = {"img", "rect", "sf"} # image; rect of this image; surface with this image

objs = {
    "lh_top": dict.fromkeys(sprite_properties),
    "lh": dict.fromkeys(sprite_properties),
    "isl": dict.fromkeys(sprite_properties),
    "bg_isl": dict.fromkeys(sprite_properties),
}

for key, path in zip(objs.keys(), paths):
    img_path = os.path.join(os.path.dirname(__file__), path)
    objs[key]['img'] = pygame.image.load(img_path)

    if key == "bg_isl":
        objs[key]['img'] = pygame.transform.scale(objs[key]['img'], (screen_width, screen_height))

    objs[key]['rect'] = objs[key]['img'].get_rect()       
    objs[key]['rect'].center = (screen_width // 2, screen_height // 2)
    objs[key]['sf'] = pygame.Surface((objs[key]['rect'].width, objs[key]['rect'].height), pygame.SRCALPHA)
    objs[key]['sf'].blit(objs[key]['img'], (0, 0))

beam_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
