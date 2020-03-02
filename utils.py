from random import randint


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
