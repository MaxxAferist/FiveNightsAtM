import pygame as pg
import sys
import os
from ctypes import *
from PIL import Image, ImageEnhance


pg.init()
pg.mixer.init()
FPS = 60
WIDTH = windll.user32.GetSystemMetrics(0)
HEIGHT = windll.user32.GetSystemMetrics(1)


def pilToSurface(pilImage):
    return pg.image.frombuffer(pilImage.tobytes(), pilImage.size, pilImage.mode)


def surfaceToPil(surface):
    pil_string_image = pg.image.tostring(surface, "RGBA", False)
    return Image.frombuffer("RGBA", surface.get_size(), pil_string_image)


def lowBrightness(image, factor):
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


def go_game():
    game = Game()
    game.run()


def go_menu():
    menu = Menu()
    menu.run()


class Menu():
    def __init__(self):
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        fon_image = load_image('menu_fon.png')
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
        up_top = (HEIGHT - btn_h * len(buttons) - top * (len(buttons) - 1)) // 2
        for i in range(len(buttons)):
            button = Button(buttons[i], (left_top, up_top + (btn_h + top) * i, btn_w, btn_h), font_size, actions[i])
            self.buttons_sprites.add(button)
            self.all_sprites.add(button)

    def run(self):
        pg.mixer.music.load('data/sounds/Fnaf_theme.mp3')
        pg.mixer.music.play()
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
        self.text = self.f.render(self.name, True, (0, 0, 0))
        self.up_top = (self.h - self.font_size) // 2
        self.left_top = (self.w - self.text.get_rect()[2]) // 2
        self.image.blit(self.text, (self.left_top, self.up_top))
        self.click_flag = False
        self.pressed = False
        self.action = action

    def update(self):
        pos = pg.mouse.get_pos()
        pressed = pg.mouse.get_pressed()[0]
        if self.rect.collidepoint(pos) and pressed:
            self.image = self.fon
            self.text = self.f.render(self.name, True, (255, 255, 0))
            self.image.blit(self.text, (self.left_top, self.up_top))
            self.pressed = True
        elif self.rect.collidepoint(pos) and self.pressed and not pressed:
            self.pressed = False
            if self.click_flag and self.action:
                self.action()
        elif self.rect.collidepoint(pos):
            self.click_flag = True
            self.image = self.fon
            self.text = self.f.render(self.name, True, (0, 162, 232))
            self.image.blit(self.text, (self.left_top, self.up_top))
        else:
            self.pressed = False
            self.image = self.fon
            self.text = self.f.render(self.name, True, (0, 0, 0))
            self.image.blit(self.text, (self.left_top, self.up_top))


class Game():
    def __init__(self):
        self.screen = pg.display.set_mode((0, 0), pg.FULLSCREEN)
        self.clock = pg.time.Clock()
        self.all_sprites = pg.sprite.Group()
        self.running = True

    def run(self):
        # pg.mixer.music.load('data/sounds/Fnaf_theme.mp3')
        # pg.mixer.music.play()
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    termit()
            self.all_sprites.update()
            self.all_sprites.draw(self.screen)
            pg.display.flip()
            self.clock.tick(FPS)


if __name__ == '__main__':
    go_menu()
