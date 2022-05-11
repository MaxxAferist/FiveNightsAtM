import pygame as pg
import sys
import os
from ctypes import *

import pygame.sprite
from PIL import Image, ImageEnhance
import json
import datetime
import random


pg.init()
pg.mixer.init()
FPS = 30
WIDTH = windll.user32.GetSystemMetrics(0)
HEIGHT = windll.user32.GetSystemMetrics(1)


def pilToSurface(pilImage):
    return pg.image.frombuffer(pilImage.tobytes(), pilImage.size, pilImage.mode)


def surfaceToPil(surface):
    pil_string_image = pg.image.tostring(surface, "RGBA", False)
    return Image.frombuffer("RGBA", surface.get_size(), pil_string_image)


def lowBrigthness(image, factor):
    pil_image = surfaceToPil(image)
    enhancer = ImageEnhance.Brightness(pil_image)
    image_final = enhancer.enhance(factor)
    return pilToSurface(image_final)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pg.image.load(fullname)
    return image


def termit():
    sys.exit()


def go_game(videos=None):
    game = Game(videos)
    game.run()



def go_menu():
    menu = Menu()
    menu.run()


class Menu():
    def __init__(self):
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        fon_image = load_image('menu/menu_fon.png')
        self.fon = pg.sprite.Sprite(self.all_sprites)
        self.fon.image = fon_image
        self.fon.rect = self.fon.image.get_rect()
        self.running = True
        self.buttons_sprites = pg.sprite.Group()
        buttons = ['New game', 'Load game', 'Settings', 'Exit']
        actions = [go_game, None, None, termit]
        btn_w = 300
        btn_h = 60
        top = 10
        font_size = 30
        left_top = (WIDTH - btn_w) // 7
        up_top = (HEIGHT - btn_h * len(buttons) -
                  top * (len(buttons) - 1)) // 2
        for i in range(len(buttons)):
            button = Button(
                buttons[i], (left_top, up_top + (btn_h + top) * i, btn_w, btn_h), font_size, actions[i])
            self.buttons_sprites.add(button)
            self.all_sprites.add(button)

    def run(self):
        pg.mixer.music.load('data/sounds/Fnaf_theme.mp3')
        pg.mixer.music.play(-1)
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    termit()
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)
            pg.display.flip()
            self.clock.tick(FPS)


class Button(pg.sprite.Sprite):
    def __init__(self, name, rect, font_size, action=None):
        super().__init__()
        image = pg.Surface(rect[2:])
        self.fon = image
        self.image = self.fon
        self.rect = image.get_rect()
        self.rect.x = rect[0]
        self.rect.y = rect[1]
        self.w = rect[2]
        self.h = rect[3]
        self.font_size = font_size
        self.f = pg.font.Font('data/FNAF.ttf', self.font_size)
        self.name = name
        self.text = self.f.render(self.name, True, (100, 0, 0))
        self.up_top = (self.h - self.font_size) // 2
        self.left_top = (self.w - self.text.get_rect()[2]) // 2
        self.image.blit(self.text, (self.left_top, self.up_top))
        self.action = action
        self.pressed = False
        self.possib = False

    def update(self):
        pos = pg.mouse.get_pos()
        pressed = pg.mouse.get_pressed()[0]
        if self.rect.collidepoint(pos):
            if not pressed:
                if self.pressed:
                    self.pressed = False
                    if self.action:
                        self.action()
                else:
                    self.possib = True
                    self.image = self.fon
                    self.text = self.f.render(self.name, True, (0, 162, 232))
                    self.image.blit(self.text, (self.left_top, self.up_top))
            else:
                if self.possib:
                    self.pressed = True
                if self.pressed:
                    self.image = self.fon
                    self.text = self.f.render(self.name, True, (255, 255, 0))
                    self.image.blit(self.text, (self.left_top, self.up_top))
        else:
            self.possib = False
            self.pressed = False
            self.image = self.fon
            self.text = self.f.render(self.name, True, (0, 0, 0))
            self.image.blit(self.text, (self.left_top, self.up_top))


class RoomButton(pg.sprite.Sprite):
    def __init__(self, text, rect, font_size, action=None, args=None):
        super().__init__()
        image = pg.Surface(rect[2:])
        image.fill(pg.Color(169, 169, 169))
        self.fon = image
        self.image = self.fon.copy()
        self.rect = image.get_rect()
        self.rect.x = rect[0]
        self.rect.y = rect[1]
        self.w = rect[2]
        self.h = rect[3]
        self.font_size = font_size
        self.f = pg.font.Font('data/Archive.ttf', self.font_size)
        self.name = text
        self.text = self.f.render(self.name, True, (0, 0, 0))
        self.up_top = (self.h - self.font_size) // 2
        self.left_top = (self.w - self.text.get_rect()[2]) // 2
        self.image.blit(self.text, (self.left_top, self.up_top))
        self.action = action
        self.args = args
        self.pressed = False
        self.possib = False

    def update(self):
        pos = pg.mouse.get_pos()
        pressed = pg.mouse.get_pressed()[0]
        if self.rect.collidepoint(pos):
            if not pressed:
                if self.pressed:
                    self.pressed = False
                    if self.action:
                        self.action(*self.args)
                else:
                    self.possib = True
                    self.image = self.fon.copy()
                    self.image.fill(pg.Color(192, 192, 192))
                    self.text = self.f.render(self.name, True, (0, 0, 0))
                    self.image.blit(self.text, (self.left_top, self.up_top))
            else:
                if self.possib:
                    self.pressed = True
                if self.pressed:
                    self.image = self.fon.copy()
                    self.image.fill(pg.Color(220, 220, 220))
                    self.text = self.f.render(self.name, True, (0, 0, 0))
                    self.image.blit(self.text, (self.left_top, self.up_top))
        else:
            self.possib = False
            self.pressed = False
            self.image = self.fon.copy()
            self.text = self.f.render(self.name, True, (0, 0, 0))
            self.image.blit(self.text, (self.left_top, self.up_top))

class Monster():
    def __init__(self, various, t_delta, name, other):
        self.various = various
        self.t_delta = t_delta
        self.name = name
        self.other = other
        self.room_id = self.currect_room_id()
        self.step_time = datetime.datetime.now()

    def update(self):
        time = datetime.datetime.now()
        timedelta = int((time - self.step_time).total_seconds())
        if timedelta >= self.t_delta:
            print('yeees')
            choises = [self.room_random] * self.various + [None] * (100 - self.various)
            action = random.choice(choises)
            if action:
                action()
            self.step_time = datetime.datetime.now()

    def room_random(self):
        room_id = random.choice(self.get_neighbours())
        self.trans_room(room_id)

    def currect_room_id(self):
        return [key for key in self.other.map if self.name in self.other.map[key]["locator"]][0]

    def get_neighbours(self):
        cur_room_id = self.currect_room_id()
        neigs = list((self.other.map[cur_room_id]["neighbours"].keys()))
        return neigs

    def trans_room(self, room_id):
        cur_rom = self.currect_room_id()
        if self.other.map[room_id]["locator"] == 'Vasia':
            print(self.name)
            self.other.show_skrimer(self.name)
            pg.quit()
        elif self.other.map[room_id]["locator"] == 'Zero':
            cur_room = self.currect_room_id()
            self.other.map[room_id]["locator"] = self.name
            if self.other.map[cur_room]["locator"] == self.name:
                self.other.map[cur_room]["locator"] = 'Zero'
            else:
                monsters = ['Max', 'Elc']
                del monsters[monsters.index(self.name)]
                self.other.map[cur_room]["locator"] = monsters[0]
            print(f'{self.name} перешёл из {cur_rom} в {room_id}')
        else:
            cur_room = self.currect_room_id()
            self.other.map[room_id]["locator"] = 'Max, Elc'
            self.other.map[cur_room]["locator"] = 'Zero'
            print(self.other.map[room_id]["locator"])
            print(f'{self.name} перешёл из {cur_rom} в {room_id}')


class Timer():
    def __init__(self, other):
        super().__init__()
        self.start_time = datetime.datetime.now()
        self.x = WIDTH - WIDTH // 12
        self.y = 0
        self.other = other
        self.font_size = 40
        self.f = pg.font.Font('data/FNAF.ttf', self.font_size)

    def update(self):
        self.time = datetime.datetime.now()
        timedelta = int((self.time - self.start_time).total_seconds()) // 100
        self.text = self.f.render(f'{timedelta} AM', True, (255, 255, 255))
        self.other.fon_sprite.image.blit(self.text, (self.x, self.y))


class Game():
    def __init__(self, videos=None):
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        self.running = True
        self.video = videos

    def run(self):
        pg.mixer.music.load('data/sounds/Main_theme2.mp3')
        pg.mixer.music.play(-1)
        self.load_info()
        self.map = self.get_map()
        self.load_images()
        if not self.video:
            self.get_all_videos()
        self.add_sprite()
        while self.running:
            self.screen.fill(pg.Color(0, 0, 0))
            for event in pg.event.get():
                if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    termit()
            keys = pg.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.fon_sprite.image = self.flash_light()
            else:
                self.fon_sprite.image = self.current_image()
            self.rotate_head()
            self.monsters_update()
            self.timer.update()
            self.all_sprites.update()
            self.buttons_group.update()
            self.all_sprites.draw(self.screen)
            self.buttons_group.draw(self.screen)
            pg.display.flip()
            self.clock.tick(FPS)

    def flash_light(self):
        try:
            cur_room_id = self.currect_room_id()
            neighbours = self.map[cur_room_id]["neighbours"]
            neig_keys = list(neighbours.keys())
            max_id = [key for key in self.map if 'Max' in self.map[key]["locator"]][0]
            elc_id = [key for key in self.map if 'Elc' in self.map[key]["locator"]][0]
            ids = []
            if max_id in neig_keys:
                ids.append(max_id)
            if elc_id in neig_keys:
                ids.append(elc_id)
            ids = sorted(list(set(ids)))
            dir_name = '_'.join(ids)
            if len(ids) == 2:
                file_name = '_'.join(map(lambda x: self.map[x]["locator"], ids))
                image = load_image(f'light/{cur_room_id}/{dir_name}/{file_name}.jpg')
            elif len(ids) == 1:
                mnstrs = self.map[ids[0]]["locator"].split(', ')
                file_name = '_'.join(mnstrs)
                image = load_image(f'light/{cur_room_id}/{dir_name}/{file_name}.jpg')
            else:
                file_name = cur_room_id
                image = load_image(f'light/{cur_room_id}/{file_name}.jpg')
            k = image.get_height() / HEIGHT
            # if int(image.get_width() / k) < WIDTH:
            #     image = pg.transform.scale(image, (WIDTH, HEIGHT))
            # else:
            image = pg.transform.scale(image, (int(image.get_width() / k), HEIGHT))
            return image
        except Exception as e:
            print(e)



    def show_skrimer(self, name_monster):
        pygame.mixer.music.stop()
        self.scrimer_sp_group = pygame.sprite.Group()
        image_names = os.listdir(f'data/ugly_monsters/{name_monster}')
        image_name = random.choice(image_names)
        image = load_image(f'ugly_monsters/{name_monster}/{image_name}')
        image_resize = pygame.transform.scale(image, (WIDTH, HEIGHT))
        self.scrimer_image_sprite = pygame.sprite.Sprite(self.scrimer_sp_group)
        self.scrimer_image_sprite.image = image_resize
        self.scrimer_image_sprite.rect = image_resize.get_rect()

        sounds = os.listdir(f'data/sounds/{name_monster}')
        sound = random.choice(sounds)
        sound = pygame.mixer.Sound(f'data/sounds/{name_monster}/{sound}')
        sound.play()
        while self.running:
            self.screen.fill(pg.Color(0, 0, 0))
            for event in pg.event.get():
                if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    termit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_RETURN:
                    go_game(self.video)
            self.scrimer_sp_group.draw(self.screen)
            pg.display.flip()
            self.clock.tick(FPS)

    def rotate_head(self):
        step = 40
        pos_x = pg.mouse.get_pos()[0]
        if pos_x >= WIDTH - 5:
            if self.fon_sprite.rect.x + self.fon_sprite.rect.w - step >= WIDTH:
                self.fon_sprite.rect.x -= step
            else:
                self.fon_sprite.rect.x = WIDTH - self.fon_sprite.rect.w
        elif pos_x <= 5:
            if self.fon_sprite.rect.x + step >= 0:
                self.fon_sprite.rect.x = 0
            else:
                self.fon_sprite.rect.x += step

    def add_sprite(self):
        self.fon_sprite = pg.sprite.Sprite(self.all_sprites)
        self.fon_sprite.image = self.current_image()
        self.fon_sprite.rect = self.fon_sprite.image.get_rect()
        self.timer = Timer(self)
        self.arrange_buttons(self.currect_room_id())
        self.max = Monster(40, 10, "Max", self)
        self.elc = Monster(30, 15, "Elc", self)

    def monsters_update(self):
        self.max.update()
        self.elc.update()

    def load_info(self):
        with open('data/info.json', encoding='utf-8') as file:
            self.info = json.load(file)

    def get_map(self):
        return self.info["map"]

    def load_images(self):
        self.room_images = {}
        for key in self.map:
            if self.map[key]["img"] != "":
                image = load_image(self.map[key]["img"])
                k = image.get_height() / HEIGHT
                if int(image.get_width() / k) < WIDTH:
                    self.room_images[key] = pg.transform.scale(
                        image, (WIDTH, HEIGHT))
                else:
                    self.room_images[key] = pg.transform.scale(
                        image, (int(image.get_width() / k), HEIGHT))
            else:
                self.room_images[key] = ''

    def current_image(self):
        current_room = [key for key in self.map if self.map[key]
                        ["locator"] == "Vasia"][0]
        return self.room_images[current_room].copy()

    def currect_room_id(self):
        return [key for key in self.map if self.map[key]["locator"] == "Vasia"][0]

    def trans_room(self, room_id):
        self.play_trans(self.currect_room_id(), room_id)
        if self.map[room_id]["locator"] != 'Zero':
            names = self.map[room_id]["locator"].split(', ')
            name = random.choice(names)
            self.show_skrimer(name)
            pg.quit()
        else:
            cur_room = self.currect_room_id()
            self.map[room_id]["locator"], self.map[cur_room]["locator"] = self.map[cur_room]["locator"], self.map[room_id]["locator"]
            self.fon_sprite.image = self.current_image()
            self.fon_sprite.rect = self.fon_sprite.image.get_rect()
            self.arrange_buttons(room_id)

    def arrange_buttons(self, room_id):
        self.buttons_group = pg.sprite.Group()
        neighbours = self.map[room_id]["neighbours"]
        keys = list(neighbours.keys())
        for i in range(len(keys)):
            neig = keys[i]
            button = RoomButton(neighbours[neig],
                                [5, HEIGHT * 0.8 + 35 * i, 200, 30],
                                20, action=self.trans_room, args=(neig,))
            self.buttons_group.add(button)

    def play_trans(self, from_id, to_id):
        frames = self.video[f"{from_id}_{to_id}"]
        for frame in frames:
            self.screen.blit(frame, (0, 0))
            pg.display.flip()
            self.clock.tick(FPS)

    def get_all_videos(self):
        transitions = ['1_2', '2_1', '2_3', '3_2', '3_4', '3_9', '4_3', '4_5',
                       '5_4', '5_6', '6_5', '6_7', '7_6', '7_8', '7_9', '8_7',
                       '8_9', '9_7', '9_8', '9_3']
        self.video = {}
        for trans in transitions:
            try:
                self.video[trans] = self.get_frames_from_dir(trans)
            except:
                pass

    def get_frames_from_dir(self, trans):
        files = os.listdir(f'data/Transitions_copy/{trans}')
        images = []
        for file in files:
            if file.lower().endswith('png') or file.lower().endswith('jpg'):
                images.append(pg.transform.scale(
                    load_image(f'Transitions_copy/{trans}/{file}'), (WIDTH, HEIGHT)))
        return images


if __name__ == '__main__':
    go_menu()
    pg.quit()