import pygame as pg
import sys
import os
from ctypes import *
import pygame.sprite
from PIL import Image, ImageEnhance
import json
import datetime
import random
import numpy as np
import pygame.camera


pg.init()
pg.mixer.init()
FPSVIDEOS = 30
FPS = 60
WIDTH = windll.user32.GetSystemMetrics(0)
HEIGHT = windll.user32.GetSystemMetrics(1)
sounds = {
    "Max_1": pg.mixer.Sound('data/sounds/laugh-girl.mp3'),
    "Elc_1": pg.mixer.Sound('data/sounds/laugh-girl.mp3'),
    "Max_1_Elc_1": pg.mixer.Sound('data/sounds/laugh-girl.mp3'),
    "Elc_6": pg.mixer.Sound('data/sounds/Abu Ali - Nasheed - about Prophet Mohammad PBUH.mp3')
}


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
        raise 'Файл не найден. Подробности в консоли'
    image = pg.image.load(fullname)
    return image


def termit():
    sys.exit()


def go_game(videos=None, light_photos=None):
    game = Game(videos, light_photos)
    game.run()


def go_menu():
    menu = Menu()
    menu.run()


class Matrix():
    def __init__(self, app, font_size=8):
        self.app = app
        self.FONT_SIZE = font_size
        self.SIZE = self.ROWS, self.COLS = HEIGHT // font_size, WIDTH // font_size
        self.katakana = np.array([chr(int('0x30a0', 16) + i)
                                 for i in range(96)] + ['' for i in range(10)])
        self.font = pg.font.Font('data/MS Mincho.ttf', font_size, bold=True)

        self.matrix = np.random.choice(self.katakana, self.SIZE)
        self.char_intervals = np.random.randint(25, 50, size=self.SIZE)
        self.cols_speed = np.random.randint(1, 500, size=self.SIZE)
        self.prerendered_chars = self.get_prerendered_chars()

        self.image = self.get_image('data/anonimus.jpg')

    def get_frame(self):
        image = self.app.cam.get_image()
        image = pg.transform.scale(image, (WIDTH, HEIGHT))
        pixel_array = pg.pixelarray.PixelArray(image)
        return pixel_array

    def get_image(self, path_to_file):
        image = pg.image.load(path_to_file)
        image = pg.transform.scale(image, (WIDTH, HEIGHT))
        pixel_array = pg.pixelarray.PixelArray(image)
        return pixel_array

    def get_prerendered_chars(self):
        char_colors = [(0, green, 0) for green in range(256)]
        prerendered_chars = {}
        for char in self.katakana:
            prerendered_char = {(char, color): self.font.render(
                char, True, color) for color in char_colors}
            prerendered_chars.update(prerendered_char)
        return prerendered_chars

    def run(self):
        frames = pg.time.get_ticks()
        self.change_chars(frames)
        self.shift_column(frames)
        self.draw()

    def shift_column(self, frames):
        num_cols = np.argwhere(frames % self.cols_speed == 0)
        num_cols = num_cols[:, 1]
        num_cols = np.unique(num_cols)
        self.matrix[:, num_cols] = np.roll(
            self.matrix[:, num_cols], shift=1, axis=0)

    def change_chars(self, frames):
        mask = np.argwhere(frames % self.char_intervals == 0)
        new_chars = np.random.choice(self.katakana, mask.shape[0])
        self.matrix[mask[:, 0], mask[:, 1]] = new_chars

    def draw(self):
        self.image = self.get_frame()
        for y, row in enumerate(self.matrix):
            for x, char in enumerate(row):
                if char:
                    pos = x * self.FONT_SIZE, y * self.FONT_SIZE
                    _, red, green, blue = pg.Color(self.image[pos])
                    if red and green and blue:
                        color = (red + green + blue) // 3
                        color = 220 if 160 < color < 220 else color
                        char = self.prerendered_chars[(char, (0, color, 0))]
                        char.set_alpha(color + 100)
                        self.app.screen.blit(char, pos)


class Menu():
    def __init__(self):
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        # fon_image = load_image('menu/menu_fon.png')
        # self.fon = pg.sprite.Sprite(self.all_sprites)
        # self.fon.image = fon_image
        # self.fon.rect = self.fon.image.get_rect()
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

        pygame.camera.init()
        self.cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
        self.cam.start()
        self.matrix = Matrix(self)

    def run(self):
        pg.mixer.music.load('data/sounds/Fnaf_theme.mp3')
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(0.5)
        while self.running:
            self.screen.fill('black')
            for event in pg.event.get():
                if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    termit()
            self.matrix.run()
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
        self.add_sounds()
        self.times = datetime.datetime.now()

    def update(self):
        time = datetime.datetime.now()
        timedelta = int((time - self.step_time).total_seconds())
        if timedelta >= self.t_delta:
            print('yeees')
            choises = [self.room_random] * self.various + [None] * (100 - self.various)
            action = random.choice(choises)
            if action:
                choises = [random.choice(self.sounds).play] * 10 + [None] * 90
                play_song = random.choice(choises)
                if play_song:
                    play_song()
                action()
            self.step_time = datetime.datetime.now()

    def add_sounds(self):
        path = os.path.join(os.getcwd(), 'data/sounds/sharp')
        sounds_names = os.listdir(path)
        self.sounds = [pg.mixer.Sound(f'data/sounds/sharp/{x}') for x in sounds_names]

    def room_random(self):
        niggers = self.get_neighbours()
        pl_way = random.choice(self.dist_from_player(self.currect_room_id(), self.other.currect_room_id()))
        niggers.remove(pl_way)
        active_distraction = (datetime.datetime.now() - self.times).total_seconds() < 25
        if not active_distraction:
            if len(niggers) == 0:
                room_id = pl_way
            elif len(niggers) == 1:
                room_id = random.choice(7 * [pl_way] + 3 * niggers)
            else:
                room_id = random.choice(14 * [pl_way] + 3 * [niggers[0]] + 3 * [niggers[1]])
        else:
            if len(niggers) == 0:
                room_id = pl_way
            elif len(niggers) == 1:
                room_id = random.choice([pl_way] + 9 * niggers)
            else:
                room_id = random.choice([pl_way] + 5 * [niggers[0]] + 5 * [niggers[1]])
        self.trans_room(room_id)

    def dist_from_player(self, cur_room_id, player_room_id):
        room_ids = [[i, i] for i in self.get_nig(cur_room_id)]
        res = []
        flag = False
        while True:
            room_clon = []
            for i in room_ids:
                if i[1] == player_room_id:
                    res.append(i[0])
                    flag = True
            if flag:
                return list(set(res))
            for room in room_ids:
                niggers = self.get_nig(room[1])
                for i in niggers:
                    room_clon.append([room[0], i])
            room_ids = room_clon.copy()


    def get_nig(self, room_id):
        neigs = list((self.other.map[room_id]["neighbours"].keys()))
        return neigs

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
        self.other.camers.switch_image(self.other.camers.cur_id_cum, False)


class Timer(pg.sprite.Sprite):
    def __init__(self, other):
        super().__init__(other.all_sprites)
        self.start_time = datetime.datetime.now()
        self.font_size = 40
        self.f = pg.font.Font('data/FNAF.ttf', self.font_size)
        self.image = self.f.render(f'Cum AM', True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH - WIDTH // 12
        self.rect.y = 0
        self.other = other
        self.time_timer = 0

    def update(self):
        self.time = datetime.datetime.now()
        self.time_timer = int((self.time - self.start_time).total_seconds()) // 100
        self.image = self.f.render(f'{self.time_timer} AM', True, (255, 255, 255))


class Battery(pg.sprite.Sprite):
    def __init__(self, other):
        super().__init__(other.all_sprites)
        self.other = other
        self.s = {5: load_image('Battery/Charge_5 +.png'),
                  4: load_image('Battery/Charge_5 +.png'),
                  3: load_image('Battery/Charge_4 +.png'),
                  2: load_image('Battery/Charge_3 +.png'),
                  1: load_image('Battery/Charge_2 +.png'),
                  0: load_image('Battery/Charge_1 +.png'),
                  -1: load_image('Battery/Charge_0 +.png')}
        self.image = self.s[5]
        self.rect = self.image.get_rect()
        self.rect.x = 10
        self.rect.y = 10

    def update(self):
        if self.other.charge == 0:
            key = -1
        else:
            key = self.other.charge // 20
        self.image = self.s[key]


class Camers():
    def __init__(self, other):
        self.other = other
        self.switch_sound = pg.mixer.Sound('data/Sounds/switch_camera.mp3')
        self.gear = pg.sprite.Sprite(self.other.all_sprites)
        self.orig_gear_image = pg.transform.scale(load_image('Camers/gear.png'), (WIDTH // 10, WIDTH // 10))
        self.gear.image = self.orig_gear_image.copy()
        self.gear.rect = self.gear.image.get_rect()
        self.gear.rect.x = WIDTH
        self.gear.rect.y = HEIGHT // 10
        self.loads_cums_photos()
        self.scr = pg.sprite.Sprite(self.other.all_sprites)
        self.switch_image("5")
        self.scr.rect = self.scr.image.get_rect()
        self.scr.rect.x = WIDTH
        self.scr.rect.y = 0
        self.scheme = pg.sprite.Sprite(self.other.all_sprites)
        self.scheme.image = pg.transform.scale(load_image('Camers/scheme.png'),
                                               (self.scr.rect.w // 3, HEIGHT * 2 // 3))
        self.scheme.rect = self.scheme.image.get_rect()
        self.scheme.rect.x = self.scr.rect.w * 2 // 3 + self.scr.rect.x
        self.scheme.rect.y = self.scr.rect.h // 3 + self.scr.rect.y
        self.active = False
        self.move = False
        self.gear_angle = 0
        self.time_active = datetime.datetime.now()
        self.cur_id_cum = "5"
        self.camera_sound = pg.mixer.Sound('data/sounds/camera_main_theme.mp3')
        self.camera_sound.set_volume(0.1)

    def movement(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_1:
                self.switch_image("1")
            if event.key == pg.K_2:
                self.switch_image("2")
            if event.key == pg.K_3:
                self.switch_image("3")
            if event.key == pg.K_4:
                self.switch_image("4")
            if event.key == pg.K_5:
                self.switch_image("5")
            if event.key == pg.K_6:
                self.switch_image("6")
            if event.key == pg.K_TAB or event.key == pg.K_ESCAPE:
                self.move = True

    def switch_image(self, cum_id, flag=True):
        self.cur_id_cum = cum_id
        neighbours = self.other.info["camers"][self.cur_id_cum]["rooms"]
        if self.other.cur_sound_room in neighbours:
            self.other.sound_volume = 0.7
        else:
            self.other.sound_volume = 0.1
        if self.other.cur_sound_room != -1:
            self.other.cur_sound_play.set_volume(self.other.sound_volume)
        if flag:
            self.switch_sound.play()
        self.scr.image = self.get_cam_image(cum_id).copy()

    def get_cam_image(self, cum_id):
        try:
            neighbours = self.other.info["camers"][cum_id]["rooms"]
            neig_keys = list(map(str, neighbours))
            max_id = [
                key for key in self.other.map if 'Max' in self.other.map[key]["locator"]][0]
            elc_id = [
                key for key in self.other.map if 'Elc' in self.other.map[key]["locator"]][0]
            ids = []
            if max_id in neig_keys:
                ids.append(max_id)
            if elc_id in neig_keys:
                ids.append(elc_id)
            ids = sorted(list(set(ids)))
            dir_name = '_'.join(ids)
            if len(ids) == 2:
                file_name = '_'.join(
                    map(lambda x: self.other.map[x]["locator"], ids))
                image = self.cams_photo[cum_id][dir_name][file_name]
            elif len(ids) == 1:
                mnstrs = self.other.map[ids[0]]["locator"].split(', ')
                file_name = '_'.join(mnstrs)
                image = self.cams_photo[cum_id][dir_name][file_name]
            else:
                file_name = cum_id
                image = self.cams_photo[cum_id][file_name]
            return image
        except Exception as e:
            print(e)

    def loads_cums_photos(self):
        self.cams_photo = {}
        path = os.path.join(os.getcwd(), 'data\Camers\cums')
        dirs = os.listdir(path)
        for room_id in dirs:
            places = os.listdir(os.path.join(path, room_id))
            self.cams_photo[room_id] = {}
            for file in places:
                if os.path.isfile(os.path.join(path, room_id, file)):
                    try:
                        img = load_image(f'Camers/cums/{room_id}/{file}')
                        file = file[:file.find('.')]
                        k = img.get_height() / HEIGHT
                        if int(img.get_width() / k) < WIDTH:
                            self.cams_photo[room_id][file] = pg.transform.scale(
                                img, (WIDTH, HEIGHT))
                        else:
                            self.cams_photo[room_id][file] = pg.transform.scale(
                                img, (int(img.get_width() / k), HEIGHT))
                    except Exception as e:
                        print(e)
                elif os.path.isdir(os.path.join(path, room_id, file)):
                    file_room = os.listdir(os.path.join(path, room_id, file))
                    self.cams_photo[room_id][file] = {}
                    for image in file_room:
                        try:
                            img = load_image(
                                f'Camers/cums/{room_id}/{file}/{image}')
                            k = img.get_height() / HEIGHT
                            image = image[:image.find('.')]
                            if int(img.get_width() / k) < WIDTH:
                                self.cams_photo[room_id][file][image] = pg.transform.scale(
                                    img, (WIDTH, HEIGHT))
                            else:
                                self.cams_photo[room_id][file][image] = pg.transform.scale(
                                    img, (int(img.get_width() / k), HEIGHT))
                        except Exception as e:
                            print(e)

    def move_left(self):
        self.scr.rect.x -= 50
        self.gear_angle += 10
        self.gear_angle = self.gear_angle % 360
        self.gear.image = pg.transform.rotate(self.orig_gear_image, self.gear_angle)
        self.scheme.rect.x = self.scr.rect.w * 2 // 3 + self.scr.rect.x
        if self.scr.rect.x < 0:
            self.scr.rect.x = 0
            self.move = False
            self.active = True
            self.camera_sound.play(-1)
            neighbours = self.other.info["camers"][self.cur_id_cum]["rooms"]
            if self.other.cur_sound_room in neighbours:
                self.other.sound_volume = 0.7
            else:
                self.other.sound_volume = 0.2
            if self.other.cur_sound_room != -1:
                self.other.cur_sound_play.set_volume(self.other.sound_volume)

    def move_right(self):
        self.other.sound_volume = 0.1
        if self.other.cur_sound_room != -1:
            self.other.cur_sound_play.set_volume(self.other.sound_volume)
        self.scr.rect.x += 50
        self.gear_angle -= 10
        self.gear_angle = self.gear_angle % 360
        self.gear.image = pg.transform.rotate(self.orig_gear_image, self.gear_angle)
        self.scheme.rect.x = self.scr.rect.w * 2 // 3 + self.scr.rect.x
        if self.scr.rect.x > WIDTH:
            self.scr.rect.x = WIDTH
            self.move = False
            self.active = False
            self.camera_sound.stop()


class Game():
    def __init__(self, videos=None, light_photos=None):
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        self.fon_sprites = pg.sprite.Group()
        self.running = True
        self.video = videos
        self.light_photos = light_photos
        self.flash_light_on = pg.mixer.Sound('data/sounds/flashlight_on.mp3')
        self.flash_light_off = pg.mixer.Sound('data/sounds/flashlight_off.mp3')
        self.charge = 100
        self.last_distraction = datetime.datetime.now()
        self.distaction_sound = pg.mixer.Sound('data/sounds/nosehonk.mp3')
        self.battery_10_sound = pg.mixer.Sound('data/sounds/battery_10.mp3')
        self.battery_10 = False
        self.battery_died_sound = pg.mixer.Sound('data/sounds/battery_died.mp3')
        self.battery_died = False
        self.chika_sound = pg.mixer.Sound('data/sounds/chika.mp3')
        self.chimes = pg.mixer.Sound('data/sounds/chimes.mp3')
        self.easter_egg = False
        self.camera_load_sound = pg.mixer.Sound('data/sounds/camera_load.mp3')
        self.cur_sound_room = -1
        self.cur_sound_play = None
        self.sound_volume = 0.1
        self.cur_key = None

    def run(self):
        self.load_info()
        self.map = self.get_map()
        self.load_images()
        if not self.video:
            self.get_all_videos()
        if not self.light_photos:
            self.loads_light_photos()
        self.chika_scr = self.get_chika_frames()
        self.chika_scr = self.chika_scr + self.chika_scr + self.chika_scr
        self.add_sprite()
        pg.mixer.music.load('data/sounds/Main_theme_4.mp3')
        pg.mixer.music.play(-1)
        pg.mixer.music.set_volume(0.1)
        self.flash_on = False
        if self.get_mode_camers():
            self.camers.gear.rect.x = 0
        else:
            self.camers.gear.rect.x = WIDTH
        while self.running:
            self.screen.fill(pg.Color(0, 0, 0))
            for event in pg.event.get():
                if event.type == pg.KEYDOWN and event.key == pg.K_TAB:
                    if self.get_mode_camers() and not self.camers.move and not self.camers.active and self.charge > 0:
                        self.camers.move = True
                        self.camera_load_sound.play()
                if event.type == pg.KEYDOWN and event.key == pg.K_v:
                    if (datetime.datetime.now() - self.last_distraction).total_seconds() > 40 and len(self.get_neighbours()) < 3:
                        self.distaction_sound.play()
                        self.last_distraction = datetime.datetime.now()
                        if self.max.currect_room_id() in self.get_neighbours():
                            self.max.times = datetime.datetime.now()
                        if self.elc.currect_room_id() in self.get_neighbours():
                            self.elc.times = datetime.datetime.now()
                if self.camers.active:
                    self.camers.movement(event)
            if self.charge <= 0 and self.camers.active:
                self.camers.move_right()
            if self.charge < 20 and not self.battery_10:
                self.battery_10_sound.play()
                self.battery_10 = True
            if self.charge <= 0 and not self.battery_died:
                self.battery_died_sound.play()
                self.battery_died = True
            self.play_sound()
            if self.camers.active:
                if (datetime.datetime.now() - self.camers.time_active).total_seconds() > 1 and self.charge > 0:
                    self.charge -= 0.4
                    self.camers.time_active = datetime.datetime.now()
            if self.timer.time_timer == 6 and not self.easter_egg:
                action = random.choice([self.chika_scrimer] * 2 + [self.chimes.play] * 2 + [None] * 8)
                self.easter_egg = True
                if action:
                    action()
            if self.camers.move and not self.camers.active:
                self.camers.move_left()
            if self.camers.move and self.camers.active:
                self.camers.move_right()
            keys = pg.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if not self.charge < -0.4:
                    if not self.flash_on:
                        self.charge -= 0.5
                        self.flash_light_on.play()
                        self.flash_on = True
                    try:
                        self.fon_sprite.image = self.flash_light().copy()
                    except:
                        pass
                else:
                    self.fon_sprite.image = self.current_image()
            else:
                if self.flash_on:
                    self.flash_light_off.play()
                    self.flash_on = False
                self.fon_sprite.image = self.current_image().copy()
            self.rotate_head()
            self.monsters_update()
            self.timer.update()
            self.battery.update()
            self.all_sprites.update()
            self.buttons_group.update()
            self.fon_sprites.draw(self.screen)
            self.buttons_group.draw(self.screen)
            self.all_sprites.draw(self.screen)
            if self.timer.time_timer == 10:
                self.player_win()
            pg.display.flip()
            self.clock.tick(FPS)

    def play_sound(self):
        play_sounds = []
        keys = [f'Max_{self.max.currect_room_id()}', f'Elc_{self.elc.currect_room_id()}', f'Max_{self.max.currect_room_id()}_Elc_{self.elc.currect_room_id()}']
        sounds_keys = list(sounds.keys())
        for key in keys:
            if key in sounds_keys:
                play_sounds.append(key)
        if len(play_sounds) == 0:
            if self.cur_sound_play:
                self.cur_sound_play.stop()
            self.cur_key = None
            self.cur_sound_play = None
            self.cur_sound_room = -1
        else:
            if self.cur_key not in play_sounds:
                self.cur_key = random.choice(play_sounds)
                self.cur_sound_room = self.cur_key.split('_')[-1]
                self.cur_sound_play = sounds[self.cur_key]
                self.cur_sound_play.play()

    def get_neighbours(self):
        cur_room_id = self.currect_room_id()
        neigs = list((self.map[cur_room_id]["neighbours"].keys()))
        return neigs

    def chika_scrimer(self):
        self.chika_sound.play()
        for frame in self.chika_scr:
            self.screen.blit(frame, (0, 0))
            pg.display.flip()
            self.clock.tick(FPSVIDEOS)

    def player_win(self):
        pass

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
                image = self.light_photos[cur_room_id][dir_name][file_name]
            elif len(ids) == 1:
                mnstrs = self.map[ids[0]]["locator"].split(', ')
                file_name = '_'.join(mnstrs)
                image = self.light_photos[cur_room_id][dir_name][file_name]
            else:
                file_name = cur_room_id
                image = self.light_photos[cur_room_id][file_name]
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
                    go_game(self.video, self.light_photos)
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
        self.fon_sprite = pg.sprite.Sprite(self.fon_sprites)
        self.fon_sprite.image = self.current_image()
        self.fon_sprite.rect = self.fon_sprite.image.get_rect()
        self.arrange_buttons(self.currect_room_id())
        self.camers = Camers(self)
        self.timer = Timer(self)
        self.battery = Battery(self)
        self.max = Monster(40, 10, "Max", self)
        self.elc = Monster(30, 7, "Elc", self)

    def monsters_update(self):
        self.max.update()
        self.elc.update()

    def load_info(self):
        with open('data/info.json', encoding='utf-8') as file:
            self.info = json.load(file)

    def get_map(self):
        return self.info["map"]

    def get_mode_camers(self):
        id = self.currect_room_id()
        return self.map[id]["cam"]

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
            if self.get_mode_camers():
                self.camers.gear.rect.x = 0
            else:
                self.camers.gear.rect.x = WIDTH

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
            self.clock.tick(FPSVIDEOS)

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

    def get_chika_frames(self):
        files = os.listdir(f'data/chika_scrim/frames')
        images = []
        for file in files:
            if file.lower().endswith('png') or file.lower().endswith('jpg'):
                images.append(pg.transform.scale(
                    load_image(f'chika_scrim/frames/{file}'), (WIDTH, HEIGHT)))
        return images

    def loads_light_photos(self):
        self.light_photos = {}
        path = os.path.join(os.getcwd(), 'data/light')
        dirs = os.listdir(path)
        for room_id in dirs:
            places = os.listdir(os.path.join(path, room_id))
            self.light_photos[room_id] = {}
            for file in places:
                if os.path.isfile(os.path.join(path, room_id, file)):
                    try:
                        img = load_image(f'light/{room_id}/{file}')
                        file = file[:file.find('.')]
                        k = img.get_height() / HEIGHT
                        if int(img.get_width() / k) < WIDTH:
                            self.light_photos[room_id][file] = pg.transform.scale(
                                img, (WIDTH, HEIGHT))
                        else:
                            self.light_photos[room_id][file] = pg.transform.scale(
                                img, (int(img.get_width() / k), HEIGHT))
                    except Exception as e:
                        print(e)
                elif os.path.isdir(os.path.join(path, room_id, file)):
                    file_room = os.listdir(os.path.join(path, room_id, file))
                    self.light_photos[room_id][file] = {}
                    for image in file_room:
                        try:
                            img = load_image(f'light/{room_id}/{file}/{image}')
                            k = img.get_height() / HEIGHT
                            image = image[:image.find('.')]
                            if int(img.get_width() / k) < WIDTH:
                                self.light_photos[room_id][file][image] = pg.transform.scale(
                                    img, (WIDTH, HEIGHT))
                            else:
                                self.light_photos[room_id][file][image] = pg.transform.scale(
                                    img, (int(img.get_width() / k), HEIGHT))
                        except Exception as e:
                            print(e)


if __name__ == '__main__':
    go_menu()
    pg.quit()