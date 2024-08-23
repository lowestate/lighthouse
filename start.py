import pygame
import os
import ctypes
import json
from consts import *

pygame.init()
pygame.font.init()

sm_font_path = 'graphics/font/super_mario.ttf'
sm_outlines_font_path = 'graphics/font/sm_outlines.ttf'
font_xs = pygame.font.Font(sm_font_path, 30)
font_s = pygame.font.Font(sm_font_path, 40)
font_m = pygame.font.Font(sm_font_path, 50)
font_l = pygame.font.Font(sm_outlines_font_path, 60)
font_xl = pygame.font.Font(sm_outlines_font_path, 80)
font_for_the_biggest_nigga = pygame.font.Font(sm_outlines_font_path, 100)

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
    'graphics/boss/preview.png',
    'graphics/boss/fin.png',
    'graphics/bg/bg_shop.png',
    'graphics/bg/shop_return_button.png'
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
    'fin':  dict.fromkeys(sprite_properties),
    # shop:
    'bg_shop':  dict.fromkeys(sprite_properties),
    'shop_return':  dict.fromkeys(sprite_properties),
}

for key, path in zip(objs.keys(), paths):
    img_path = os.path.join(os.path.dirname(__file__), path)
    objs[key]['img'] = pygame.image.load(img_path).convert_alpha()

    if key == "bg_isl" or key == "preview" or key == 'bg_shop':
        objs[key]['img'] = pygame.transform.scale(objs[key]['img'], (screen_width, screen_height))

    objs[key]['rect'] = objs[key]['img'].get_rect()       
    if key == 'shop_return':
        objs[key]['rect'].x = screen_width * 0.027
        objs[key]['rect'].y = screen_height * 0.045
    elif key == 'lh_top' or key == 'lh' or key == 'isl' or key == 'preview' or key == 'bg_isl' or key == 'fin' or key == 'bg_shop':
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

def load_stats(filename='stats.json'):
    try:
        with open(filename, 'r') as f:
            stats = json.load(f)
    except FileNotFoundError:
        stats = {
                    "total_sqs_killed": 0,
                    "coins": 0,
                    "BULLET DAMAGE": 1,
                    "_progression_bullet_damage": "1, 2, 4, 7, 10",
                    "BULLET KNOCKBACK": 50,
                    "_progression_bullet_knockback": "50, 70, 100",
                    "BULLET FREQUENCY": 10,
                    "_progression_bullet_frequency": "10, 45, 70, 90, 100",
                    "BULLET SPEED": 7,
                    "_progression_bullet_speed": "7, 9, 12, 14, 17",
                    "TURRET LEVEL": 1,
                    "_progression_turret_level": "1, 2, 3, 4, 5",
                    "BEAM WIDTH": 15,
                    "_progression_beam_width": "15, 18, 22, 25, 28",
                    "LIGHTHOUSE HP": 2,
                    "_progression_lighthouse_hp": "2, 3, 4, 5, 6"
                }
    return stats

def save_stats(stats, filename='stats.json'):
    with open(filename, 'w') as f:
        json.dump(stats, f, indent=4) 

STATS = load_stats()