import pygame
from pathlib import Path

from chip8 import Chip8


class PyGameChip8:
    def __init__(self):
        self._chip8 = Chip8()
        self._width = 64
        self._height = 32
        self._pixel_size = 10
        self._border_size = 1
        self._screen: pygame.Surface = None

    def setup(self):
        self.__create_windows()
        self.__init_screen()

    def run(self):
        self.__initialize()
        fr = False
        pygame.time.set_timer(2, 1)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                if event.type == 2:
                    self.__tick()
                    fr = not fr
                    pygame.display.flip()

    def __tick(self):
        self._chip8.emulate_cycle()

        if self._chip8.draw_flag:
            self.__draw(self._chip8.gfx)
            self._chip8.draw_flag = False

        self.__handle_input()

    def __draw(self, frame):
        for row, pixels in enumerate(frame, 0):
            for col, pixel in enumerate(pixels, 0):
                rect = self.__get_rect_pos(col, row)

                if pixel:
                    pygame.draw.rect(self._screen, pygame.Color('white'), pygame.Rect(*rect))
                else:
                    pygame.draw.rect(self._screen, pygame.Color('black'), pygame.Rect(*rect))

    def __handle_input(self):
        pass

    def __initialize(self):
        self._chip8.initialize()
        rom = Path('ROMs', 'Addition Problems [Paul C. Moews].ch8')
        self._chip8.load_game(rom)

    def __init_screen(self):
        # background
        self._screen.fill(pygame.Color('gray'))

        # tiles
        for row in range(self._height):
            for col in range(self._width):
                rect = self.__get_rect_pos(col, row)
                pygame.draw.rect(self._screen, pygame.Color('black'), pygame.Rect(*rect))

    def __create_windows(self):
        pygame.init()
        screen_width = self._width * self._pixel_size + (self._width - self._border_size)
        screen_height = self._height * self._pixel_size + (self._height - self._border_size)
        self._screen = pygame.display.set_mode((screen_width, screen_height))

    # def __create_rect(self, rect, color):
    #     return self._screen.create_rectangle(*rect, outline='gray', fill=color)

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
