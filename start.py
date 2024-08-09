import pygame
import os
import ctypes
from consts import *

pygame.init()
pygame.font.init()
font = pygame.font.Font('graphics/font/super_mario.ttf', 42)

info = pygame.display.Info()
unscaled_scr_width = info.current_w
unscaled_scr_height = info.current_h

# узнаем параметр масштабирования экрана
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
scale_factor = user32.GetDpiForSystem()
scaled = scale_factor / 96 # множитель = значение масштабировния / 100
screen_height = int(unscaled_scr_height * scaled)
screen_width = int(unscaled_scr_width * scaled)
#print(f"scalar:{scaled}\nraw:{unscaled_scr_width}x{unscaled_scr_height}\nadjusted:{screen_width}x{screen_height}")

screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN, pygame.DOUBLEBUF)
pygame.display.set_caption("Lighthouse")

paths = [
    'graphics/lh/lh_top.png',
    'graphics/lh/lh.png',
    'graphics/bg/isl.png',
    'graphics/bg/bg_isl.png',
    'graphics/boss/left_bottom.png',
    'graphics/boss/left_middle.png',
    'graphics/boss/left_top.png',
    'graphics/boss/right_bottom.png',
    'graphics/boss/right_middle.png',
    'graphics/boss/right_top.png',
    'graphics/boss/preview.png'
]

sprite_properties: dict = {"img", "rect", "sf"} # image; rect of this image; surface with this image

objs = {
    "lh_top": dict.fromkeys(sprite_properties),
    "lh": dict.fromkeys(sprite_properties),
    "isl": dict.fromkeys(sprite_properties),
    "bg_isl": dict.fromkeys(sprite_properties),
    # boss tentacles:
    "lb": dict.fromkeys(sprite_properties),
    "lm": dict.fromkeys(sprite_properties),
    "lt": dict.fromkeys(sprite_properties),
    "rb": dict.fromkeys(sprite_properties),
    "rm": dict.fromkeys(sprite_properties),
    "rt": dict.fromkeys(sprite_properties),
    "preview": dict.fromkeys(sprite_properties),
}

for key, path in zip(objs.keys(), paths):
    img_path = os.path.join(os.path.dirname(__file__), path)
    objs[key]['img'] = pygame.image.load(img_path).convert_alpha()

    if key == "bg_isl" or key == "preview":
        objs[key]['img'] = pygame.transform.scale(objs[key]['img'], (screen_width, screen_height))

    objs[key]['rect'] = objs[key]['img'].get_rect()       

    if key == 'lh_top' or key == 'lh' or key == 'isl' or key == 'preview' or key == 'bg_isl':
        objs[key]['rect'].center = (screen_width // 2, screen_height // 2)
    else: # starting pos
        objs[key]['rect'].x = 0
        objs[key]['rect'].y = 0

        # no X offset needed because it is stated in bossfight func

        if key[1] == 't': # no Y offset for top right tentacle
            if key[0] == 'l':
                objs[key]['rect'].y += screen_height * 0.0644
        elif key[1] == 'm': # Y offset for middle tentacles
            objs[key]['rect'].y += screen_height * 0.268
        else: # Y offset for bottom tentacles
            if key[0] == 'l': # bottom left
                objs[key]['rect'].y = screen_height - objs[key]['rect'].height
            else: # bottom right
                objs[key]['rect'].y += screen_height * 0.6287
        
    objs[key]['sf'] = pygame.Surface((objs[key]['rect'].width, objs[key]['rect'].height), pygame.SRCALPHA)
    objs[key]['sf'].blit(objs[key]['img'], (0, 0))

beam_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)

screen_sf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
