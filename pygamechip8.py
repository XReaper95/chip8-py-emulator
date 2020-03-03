import pygame as pg
from pygame import Surface
from pathlib import Path

from chip8 import (
    Chip8,
    KEY_1,
    KEY_2,
    KEY_3,
    KEY_4,
    KEY_5,
    KEY_6,
    KEY_7,
    KEY_8,
    KEY_9,
    KEY_0,
    KEY_A,
    KEY_B,
    KEY_C,
    KEY_D,
    KEY_E,
    KEY_F
)
from utils import center_pygame_windows


class PyGameChip8:
    def __init__(self):
        self._chip8: Chip8 = Chip8()
        self._width: int = 64
        self._height: int = 32
        self._pixel_size: int = 10
        self._border_size: int = 1
        self._screen: Surface
        self.instruction_count = 0
        self.beep_sound = None
        self.sound_playing = False

    def setup(self):
        self.__create_windows()
        self.__init_screen()
        pg.mixer.init()
        self.beep_sound = pg.mixer.Sound('res/beep.wav')

    def run(self):
        self.__initialize()
        main_clock = pg.time.Clock()

        try:
            running = True
            while running:
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        pg.quit()
                        running = False
                        break
                    if event.type == pg.KEYDOWN:
                        self.__handle_input(event.key)
                    if event.type == pg.KEYUP:
                        self._chip8.key_pressed = ''

                self.__tick()
                if self.instruction_count == 9:
                    self.__update_timers()
                    self.instruction_count = 0

                main_clock.tick(540)

        except KeyboardInterrupt:
            pass

    def __tick(self):
        self._chip8.emulate_cycle()
        self.instruction_count += 1

        if self._chip8.draw_flag:
            self.__draw(self._chip8.gfx)
            pg.display.flip()
            self._chip8.draw_flag = False

    def __draw(self, frame):
        for row, pixels in enumerate(frame, 0):
            for col, pixel in enumerate(pixels, 0):
                rect = self.__get_rect_pos(col, row)

                if pixel:
                    pg.draw.rect(self._screen, pg.Color('white'), pg.Rect(*rect))
                else:
                    pg.draw.rect(self._screen, pg.Color('black'), pg.Rect(*rect))

    def __handle_input(self, key_id: int):
        if self._chip8.key_pressed == '':
            keymap = {
                pg.K_1: KEY_1, pg.K_2: KEY_2, pg.K_3: KEY_3, pg.K_4: KEY_C,
                pg.K_q: KEY_4, pg.K_w: KEY_5, pg.K_e: KEY_6, pg.K_r: KEY_D,
                pg.K_a: KEY_7, pg.K_s: KEY_8, pg.K_d: KEY_9, pg.K_f: KEY_E,
                pg.K_z: KEY_A, pg.K_x: KEY_0, pg.K_c: KEY_B, pg.K_v: KEY_F,
                }

            key = keymap.get(key_id)
            if id:
                self._chip8.key_press(key)

    def __update_timers(self):
        if self._chip8.sound_reg > 0:
            self._chip8.sound_reg -= 1
            if not self.sound_playing:
                self.sound_playing = True
                self.beep_sound.play()
        else:
            if self.sound_playing:
                self.beep_sound.stop()
                self.sound_playing = False

        if self._chip8.delay_reg > 0:
            self._chip8.delay_reg -= 1

    def __initialize(self):
        self._chip8.initialize()
        rom = Path('ROMs', 'Minimal game [Revival Studios, 2007].ch8')
        self._chip8.load_game(rom)

    def __init_screen(self):
        # background
        self._screen.fill((35, 35, 35))

        # tiles
        for row in range(self._height):
            for col in range(self._width):
                rect = self.__get_rect_pos(col, row)
                pg.draw.rect(self._screen, pg.Color('black'), pg.Rect(*rect))

    def __create_windows(self):
        screen_width = self._width * self._pixel_size + (self._width - self._border_size)
        screen_height = self._height * self._pixel_size + (self._height - self._border_size)
        # workaround to get pygame window at center of main display
        center_pygame_windows(screen_width, screen_height)
        pg.init()
        self._screen = pg.display.set_mode((screen_width, screen_height))

    def __get_rect_pos(self, col, row):
        x1 = col * self._pixel_size + col
        y1 = row * self._pixel_size + row
        w = self._pixel_size - self._border_size
        h = w
        return x1, y1, w, h


if __name__ == '__main__':
    pyg_chip8 = PyGameChip8()
    pyg_chip8.setup()
    pyg_chip8.run()
