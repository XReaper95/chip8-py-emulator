import platform
from random import randint


def center_pygame_windows(width: int, height: int):
    import screeninfo
    import os

    if platform.system() == 'Windows':
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
        monitors = screeninfo.get_monitors(screeninfo.Enumerator.Cygwin)
    else:
        monitors = screeninfo.get_monitors()

    if len(monitors) < 1:
        print("Cannot get display info, using default windows position")
        return

    current_monitor = monitors[-1]

    screen_width = current_monitor.width
    screen_height = current_monitor.height
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'


def generate_random_frame(w, h, pix):
    result = []
    pixel_count = 0
    for _ in range(h):
        row = []
        for _ in range(w):
            if pixel_count < pix:
                rand_pix = randint(0, 1)
                row.append(rand_pix)
                pixel_count += rand_pix
            else:
                row.append(0)
        result.append(row)

    return result


def generate_x(w, h):
    result = []
    for x in range(h + 1):
        row = []
        for y in range(w + 1):
            if x == y / 2 or y == y + 1 - x * 2:
                row.append(1)
            else:
                row.append(0)
        result.append(row)

    return result


def generate_lines(w, h, even):
    result = []
    for x in range(h):
        row = []
        for y in range(w):
            if x % 2 == 0 and even:
                row.append(1)
            elif x % 2 != 0 and not even:
                row.append(1)
            else:
                row.append(0)
        result.append(row)

    return result


def print_sprite(sprite_bitmap):
    for row in sprite_bitmap:
        for bit in row:
            pixel = '*' if bit else ' '
            print(pixel, end='')
        print()


def snapshot_frame(gfx):
    horizontal_margin = '#' * (len(gfx[0]) + 2)

    print(horizontal_margin)

    for row in gfx:
        print('#', end='')
        for sprite_bit in row:
            pixel = '*' if sprite_bit else ' '
            print(pixel, end='')
        print('#')

    print(horizontal_margin)
