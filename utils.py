from random import randint


def generate_random_frame(w, h):
    result = []
    for x in range(h):
        row = []
        for y in range(w):
            row.append(randint(0, 1))
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
